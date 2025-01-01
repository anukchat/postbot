# from langchain_anthropic import ChatAnthropic 
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from src import utils
from src.ai.agent.v2.utils import *
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph

# import agent.configuration as configuration
from src.ai.agent.v2.state import Sections, BlogState, BlogStateInput, BlogStateOutput, SectionState
from src.ai.agent.v2.prompts import blog_planner_instructions, main_body_section_writer_instructions, intro_conclusion_instructions, linkedin_post_instructions,twitter_post_instructions, tags_generator
# from agent.utils import load_and_format_urls, read_dictation_file, format_sections
from ai.agent.v2 import configuration
from ai.service import get_gemini
import json
import re
import ast
from db.sql import get_tweet_by_id
from extractors.docintelligence import DocumentExtractor
# ------------------------------------------------------------
# LLMs 
# claude_3_5_sonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0) 
# gemini=get_gemini()
# ------------------------------------------------------------
# Graph


class AgentWorkflow:

    def __init__(self):
        self.llm=get_gemini()
        self.builder= StateGraph(BlogState, input=BlogStateInput, output=BlogStateOutput, config_schema=configuration.Configuration)
        self.graph=self.setup_workflow()
        self.extractor = DocumentExtractor()

    def generate_blog_plan(self,state: BlogState, config: RunnableConfig):
        """ Generate the report plan """

        # Read transcribed notes
        if state.tweet:
            user_instructions,reference_link, media_markdown  = get_reference_content(state.tweet)
        elif state.input_url:
            reference_link=state.input_url
            user_instructions=state.input_content

        # Get configuration
        configurable = configuration.Configuration.from_runnable_config(config)
        blog_structure = configurable.blog_structure

        # Format system instructions
        system_instructions_sections = blog_planner_instructions.format(user_instructions=user_instructions, blog_structure=blog_structure)

        # Generate sections 
        # structured_llm = gemini.with_structured_output(Sections)
        report_sections = self.llm.invoke([SystemMessage(content=system_instructions_sections)]+[HumanMessage(content="Generate the sections of the blog. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, and content fields.")])
        pattern = r'```json\n([\s\S]*?)\n```'
        match = re.search(pattern, report_sections.content)

        # Parse JSON if found
        if match:
            report_sections = json.loads(match.group(1))
            report_sections  # Return JSON object
        else:
            report_sections = {"sections": []}
        sections_object=Sections(**report_sections)
        return {"sections": sections_object.sections}

    def write_section(self,state: SectionState):
        """ Write a section of the report """

        # Get state 
        section = state.section
        # urls = state.urls

        # Read transcribed notes

        if state.tweet:
            user_instructions,reference_link, media_markdown  = get_reference_content(state.tweet)
        elif state.input_url:
            reference_link=state.input_url
            user_instructions=state.input_content
            media_markdown = ""

        # Load and format urls
        url_source_str = reference_link#"" if not urls else load_and_format_urls(urls)

        # Format system instructions
        system_instructions = main_body_section_writer_instructions.format(section_name=section.name, 
                                                                        section_topic=section.description, 
                                                                        user_instructions=user_instructions, 
                                                                        source_urls=url_source_str,
                                                                        media_markdown=media_markdown)

        # Generate section  
        section_content = self.llm.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate a blog section based on the provided information.")])
        
        # Write content to the section object  
        section.content = section_content.content

        # Write the updated section to completed sections
        return {"completed_sections": [section]}

    def write_final_sections(self,state: SectionState):
        """ Write final sections of the report, which do not require web search and use the completed sections as context """

        # Get state 
        section = state.section
        
        # Format system instructions
        system_instructions = intro_conclusion_instructions.format(section_name=section.name, 
                                                                section_topic=section.description, 
                                                                main_body_sections=state.blog_main_body_sections, 
                                                                source_urls=state.urls)

        # Generate section  
        section_content = self.llm.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate an intro/conclusion section based on the provided main body sections.")])
        
        # Write content to section 
        section.content = section_content.content

        # Write the updated section to completed sections
        return {"completed_sections": [section]}

    def initiate_section_writing(self,state: BlogState):
        """ This is the "map" step when we kick off web research for some sections of the report """    
            
        # Kick off section writing in parallel via Send() API for any sections that require research
        return [
            Send("write_section", SectionState(
                section=s,
                tweet=state.tweet,
                input_url=state.input_url,
                input_content=state.input_content,
                urls=[url['original_url'] for url in state.tweet['urls']] if state.tweet else [state.input_url],
                completed_sections=[]  # Initialize with empty list
            )) 
            for s in state.sections 
            if s.main_body
        ]

    def gather_completed_sections(self,state: BlogState):
        """ Gather completed main body sections"""    

        # List of completed sections
        completed_sections = state.completed_sections

        # Format completed section to str to use as context for final sections
        completed_report_sections = format_sections(completed_sections)

        return {"blog_main_body_sections": completed_report_sections}

    def initiate_final_section_writing(self,state: BlogState):
        """ This is the "map" step when we kick off research on any sections that require it using the Send API """    

        # Kick off section writing in parallel via Send() API for any sections that do not require research
        return [
            Send("write_final_sections", SectionState(
                tweet=state.tweet,
                input_url=state.input_url,
                input_content=state.input_content,
                section=s,
                blog_main_body_sections=state.blog_main_body_sections,
                urls=[url['original_url'] for url in state.tweet['urls']] if state.tweet else [state.input_url],
                completed_sections=[]  # Initialize with empty list
            )) 
            for s in state.sections 
            if not s.main_body
        ]

    def compile_final_blog(self,state: BlogState):
        """ Compile the final blog """    

        # Get sections
        sections = state.sections
        completed_sections = {s.name: s.content for s in state.completed_sections}

        # Update sections with completed content while maintaining original order
        for section in sections:
            section.content = completed_sections[section.name]

        # Compile final report
        all_sections = "\n\n".join([s.content for s in sections])

        return {"final_blog": all_sections}

    def write_twitter_post(self,state: BlogState):
        """ Write the Twitter post """    

        # Get final blog
        final_blog = state.final_blog

        # Generate Twitter post
        twitter_post = self.llm.invoke([SystemMessage(content=twitter_post_instructions.format(final_blog=final_blog))]+[HumanMessage(content="Generate a Twitter post based on the provided article ")])
        
        return {"twitter_post": twitter_post.content}

    def write_linkedin_post(self,state: BlogState):
        """ Write the Twitter post """    

        # Get final blog
        final_blog = state.final_blog

        # Generate linkedin post
        linkedin_post = self.llm.invoke([SystemMessage(content=linkedin_post_instructions.format(final_blog=final_blog))]+[HumanMessage(content="Generate a LinkedIn post based on the provided article ")])

        return {"linkedin_post": linkedin_post.content}

    def generate_tags(self,state: BlogState):
        """ Generate tags for the blog """    

        # Get final blog
        linkedin_post = state.linkedin_post


        # Generate tags
        result = self.llm.invoke([SystemMessage(content=tags_generator.format(linkedin_post=linkedin_post))]+[HumanMessage(content="Generate tags for the blog.")])

        tags_match = re.findall(r"<tags>(.*?)</tags>", result.content, re.DOTALL)
        if tags_match:
            tags_string = tags_match[0].strip()
            # Parse the string as a Python list
            try:
                tags = ast.literal_eval(tags_string)
                # Remove any surrounding quotes and spaces from each tag
                tags = [tag.strip().strip('"') for tag in tags]
            except:
                # If parsing fails, fall back to splitting by comma
                tags = [tag.strip().strip('"[]') for tag in tags_string.split(",")]
        else:
            tags = []
        return {"tags": tags}

    def setup_workflow(self):
        # Add nodes and edges 
        # builder = self.builder#StateGraph(BlogState, input=BlogStateInput, output=BlogStateOutput, config_schema=configuration.Configuration)
        self.builder.add_node("generate_blog_plan", self.generate_blog_plan)
        self.builder.add_node("write_section", self.write_section)
        self.builder.add_node("compile_final_blog", self.compile_final_blog)
        self.builder.add_node("gather_completed_sections", self.gather_completed_sections)
        self.builder.add_node("write_final_sections", self.write_final_sections)
        self.builder.add_node("write_twitter_post", self.write_twitter_post)
        self.builder.add_node("write_linkedin_post", self.write_linkedin_post)
        self.builder.add_node("generate_tags", self.generate_tags)
        self.builder.add_edge(START, "generate_blog_plan")
        self.builder.add_conditional_edges("generate_blog_plan", self.initiate_section_writing, ["write_section"])
        self.builder.add_edge("write_section", "gather_completed_sections")
        self.builder.add_conditional_edges("gather_completed_sections", self.initiate_final_section_writing, ["write_final_sections"])
        self.builder.add_edge("write_final_sections", "compile_final_blog")
        self.builder.add_edge("compile_final_blog", "write_twitter_post")
        self.builder.add_edge("write_twitter_post", "write_linkedin_post")
        self.builder.add_edge("write_linkedin_post", "generate_tags")
        self.builder.add_edge("generate_tags", END)

        graph = self.builder.compile() 

        return graph


    def run_generic_workflow(self,payload):
        # from payload, find the type of workflow to run
        if payload["tweet_id"]:
            tweet = get_tweet_by_id(payload["tweet_id"])
            test_input = BlogStateInput(tweet=tweet)
            result = self.graph.invoke(test_input)
            result['blog_title'] = re.findall(r"^#\s+(.*)$", result['final_blog'], re.MULTILINE)[0]
            response = BlogStateOutput(**result)
            return response
        if payload["url"]:
            # do something
            # if payload url is of type html, then extract content
            type,content=utils.get_url_metadata(payload["url"])
            if type=="html":
                content=self.extractor.extract_html(html_content=content)
            elif type=="pdf":
                content=self.extractor.extract_pdf(input_file=content)
            
            test_input = BlogStateInput(input_url=payload["url"],input_content=content)
            result = self.graph.invoke(test_input)
            result['blog_title'] = re.findall(r"^#\s+(.*)$", result['final_blog'], re.MULTILINE)[0]
            response = BlogStateOutput(**result)
            return response
        if payload["topic"]:
            # do something
            pass

    def run_workflow(self,payload):
        tweet = get_tweet_by_id(payload["tweet_id"])
        print(f"Retrieved {tweet['tweet_id']}")
        test_input = BlogStateInput(tweet=tweet)
        result = self.graph.invoke(test_input)
        result['blog_title'] = re.findall(r"^#\s+(.*)$", result['final_blog'], re.MULTILINE)[0]
        response = BlogStateOutput(**result)
        return response

if __name__ == "__main__":
    # Test the graph
    tweet={
    "tweet_id": "1864215823830732889",
    "created_at": "2024-12-04T13:21:02+05:30",
    "full_text": "such a great paper on quantization of deep neural networks: https://t.co/xF34rTrPXd https://t.co/7uuUW6Tgzz",
    "language": "unknown",
    "favorite_count": 321,
    "retweet_count": 35,
    "bookmark_count": 211,
    "quote_count": 0,
    "reply_count": 5,
    "views_count": 12377,
    "screen_name": "darkyboy_",
    "user_name": "Ishaan",
    "profile_image_url": "https://pbs.twimg.com/profile_images/1799289093916135424/So7iqBs9_normal.jpg",
    "urls": [
      {
        "tweet_id": "1864215823830732889",
        "index": 0,
        "original_url": "https://arxiv.org/pdf/1911.09464",
        "downloaded_path": "tweet_collection/arxiv/arxiv_de7f6502b6_0.pdf",
        "downloaded_path_md": "tweet_collection/arxiv/markdown/arxiv_de7f6502b6_0.md",
        "type": "arxiv",
        "domain": "arxiv.org",
        "content_type": ".pdf",
        "file_category": "document",
        "downloaded_at": "2024-12-18 13:07:29"
      }
    ],
    "media": [
      {
        "tweet_id": "1864215823830732889",
        "type": "photo",
        "original_url": "https://pbs.twimg.com/media/Gd8GX3WasAAZJ8-?format=png&name=orig",
        "final_url": "https://pbs.twimg.com/media/Gd8GX3WasAAZJ8-?format=png&name=orig",
        "downloaded_path": "tweet_collection/media/reference_media/photo_b5eb2e6e06.jpg",
        "content_type": "image/png",
        "thumbnail": "https://pbs.twimg.com/media/Gd8GX3WasAAZJ8-?format=png&name=thumb",
        "downloaded_at": "2024-12-18 13:07:29"
      }
    ],
    "is_retweet": False,
    "is_quote": False,
    "possibly_sensitive": False
  }
    
    agent=AgentWorkflow()
    test_input = BlogStateInput(tweet=tweet)
    result = agent.setup_workflow(test_input)
    result['blog_title']=  re.findall(r"^#\s+(.*)",result['final_blog'],re.DOTALL)[0]
    result = BlogStateOutput(**result)
    print(result)