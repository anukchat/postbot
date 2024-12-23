# from langchain_anthropic import ChatAnthropic 
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from src.ai.agent.v2.utils import *
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph

# import agent.configuration as configuration
from src.ai.agent.v2.state import Sections, BlogState, BlogStateInput, BlogStateOutput, SectionState
from src.ai.agent.v2.prompts import blog_planner_instructions, main_body_section_writer_instructions, intro_conclusion_instructions
# from agent.utils import load_and_format_urls, read_dictation_file, format_sections
import configuration
from src.ai.service import get_gemini
import json
import re

# ------------------------------------------------------------
# LLMs 
# claude_3_5_sonnet = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0) 
gemini=get_gemini()
# ------------------------------------------------------------
# Graph
def generate_blog_plan(state: BlogState, config: RunnableConfig):
    """ Generate the report plan """

    # Read transcribed notes
    user_instructions,reference_link, media_markdown  = get_reference_content(state.tweet)

    # Get configuration
    configurable = configuration.Configuration.from_runnable_config(config)
    blog_structure = configurable.blog_structure

    # Format system instructions
    system_instructions_sections = blog_planner_instructions.format(user_instructions=user_instructions, blog_structure=blog_structure)

    # Generate sections 
    # structured_llm = gemini.with_structured_output(Sections)
    report_sections = gemini.invoke([SystemMessage(content=system_instructions_sections)]+[HumanMessage(content="Generate the sections of the blog. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, and content fields.")])
    pattern = r'```json\n([\s\S]*?)\n```'
    match = re.search(pattern, report_sections.content)

    # Parse JSON if found
    if match:
        report_sections = json.loads(match.group(1))
        report_sections  # Return JSON object
    else:
        report_sections = {"sections": []}
    return {"sections": report_sections.sections}

def write_section(state: SectionState):
    """ Write a section of the report """

    # Get state 
    section = state.section
    # urls = state.urls

    # Read transcribed notes
    user_instructions,reference_link, media_markdown  = get_reference_content(state.tweet)

    # Load and format urls
    url_source_str = reference_link#"" if not urls else load_and_format_urls(urls)

    # Format system instructions
    system_instructions = main_body_section_writer_instructions.format(section_name=section.name, 
                                                                       section_topic=section.description, 
                                                                       user_instructions=user_instructions, 
                                                                       source_urls=url_source_str)

    # Generate section  
    section_content = gemini.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate a blog section based on the provided information.")])
    
    # Write content to the section object  
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}

def write_final_sections(state: SectionState):
    """ Write final sections of the report, which do not require web search and use the completed sections as context """

    # Get state 
    section = state.section
    
    # Format system instructions
    system_instructions = intro_conclusion_instructions.format(section_name=section.name, 
                                                               section_topic=section.description, 
                                                               main_body_sections=state.blog_main_body_sections, 
                                                               source_urls=state.urls)

    # Generate section  
    section_content = gemini.invoke([SystemMessage(content=system_instructions)]+[HumanMessage(content="Generate an intro/conclusion section based on the provided main body sections.")])
    
    # Write content to section 
    section.content = section_content.content

    # Write the updated section to completed sections
    return {"completed_sections": [section]}

def initiate_section_writing(state: BlogState):
    """ This is the "map" step when we kick off web research for some sections of the report """    
        
    # Kick off section writing in parallel via Send() API for any sections that require research
    return [
        Send("write_section", SectionState(
            section=s,
            tweet=state.tweet,
            urls=state.urls,
            completed_sections=[]  # Initialize with empty list
        )) 
        for s in state.sections 
        if s.main_body
    ]

def gather_completed_sections(state: BlogState):
    """ Gather completed main body sections"""    

    # List of completed sections
    completed_sections = state.completed_sections

    # Format completed section to str to use as context for final sections
    completed_report_sections = format_sections(completed_sections)

    return {"blog_main_body_sections": completed_report_sections}

def initiate_final_section_writing(state: BlogState):
    """ This is the "map" step when we kick off research on any sections that require it using the Send API """    

    # Kick off section writing in parallel via Send() API for any sections that do not require research
    return [
        Send("write_final_sections", SectionState(
            section=s,
            blog_main_body_sections=state.blog_main_body_sections,
            urls=state.urls,
            completed_sections=[]  # Initialize with empty list
        )) 
        for s in state.sections 
        if not s.main_body
    ]

def compile_final_blog(state: BlogState):
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

# Add nodes and edges 
builder = StateGraph(BlogState, input=BlogStateInput, output=BlogStateOutput, config_schema=configuration.Configuration)
builder.add_node("generate_blog_plan", generate_blog_plan)
builder.add_node("write_section", write_section)
builder.add_node("compile_final_blog", compile_final_blog)
builder.add_node("gather_completed_sections", gather_completed_sections)
builder.add_node("write_final_sections", write_final_sections)
builder.add_edge(START, "generate_blog_plan")
builder.add_conditional_edges("generate_blog_plan", initiate_section_writing, ["write_section"])
builder.add_edge("write_section", "gather_completed_sections")
builder.add_conditional_edges("gather_completed_sections", initiate_final_section_writing, ["write_final_sections"])
builder.add_edge("write_final_sections", "compile_final_blog")
builder.add_edge("compile_final_blog", END)

graph = builder.compile() 


if __name__ == "__main__":
    # Test the graph
    tweet={
    "tweet_id": "1866137546528350566",
    "created_at": "2024-12-09T20:37:16+05:30",
    "full_text": "Great little primer on LLMs and their limitations. \\n\\nUseful for those who want to learn about key LLM concepts and their applications. \\n\\nhttps://t.co/J0NDd1qGrt https://t.co/tZPK7HItKt",
    "language": "unknown",
    "favorite_count": 215,
    "retweet_count": 49,
    "bookmark_count": 200,
    "quote_count": 1,
    "reply_count": 4,
    "views_count": 14466,
    "screen_name": "omarsar0",
    "user_name": "elvis",
    "profile_image_url": "https://pbs.twimg.com/profile_images/939313677647282181/vZjFWtAn_normal.jpg",
    "urls": [
      {
        "tweet_id": "1866137546528350566",
        "index": 0,
        "original_url": "https://arxiv.org/abs/2412.04503",
        "downloaded_path": "tweet_collection/arxiv/arxiv_2fd14a8788_0.html",
        "downloaded_path_md": "tweet_collection/arxiv/markdown/arxiv_2fd14a8788_0.md",
        "type": "arxiv",
        "domain": "arxiv.org",
        "content_type": ".html",
        "file_category": "document",
        "downloaded_at": "2024-12-18 13:05:36"
      }
    ],
    "media": [
      {
        "tweet_id": "1866137546528350566",
        "type": "photo",
        "original_url": "https://pbs.twimg.com/media/GeXZ8qXXIAArU5M?format=png&name=orig",
        "final_url": "https://pbs.twimg.com/media/GeXZ8qXXIAArU5M?format=png&name=orig",
        "downloaded_path": "tweet_collection/media/reference_media/photo_2032a8b06b.jpg",
        "content_type": "image/png",
        "thumbnail": "https://pbs.twimg.com/media/GeXZ8qXXIAArU5M?format=png&name=thumb",
        "downloaded_at": "2024-12-18 13:05:37"
      }
    ],
    "is_retweet": False,
    "is_quote": False,
    "possibly_sensitive": False
  }
    test_input = BlogStateInput(tweet=tweet)
    result = graph.invoke(test_input)