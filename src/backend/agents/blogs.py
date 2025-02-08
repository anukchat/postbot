import ast
import json
import logging
import os
import re
import uuid

from fastapi import HTTPException
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.constants import Send
from langgraph.graph import START, END, StateGraph
# from langchain_core.messages import HumanMessage, SystemMessage
from psycopg import Connection
from supabase import Client

# from src.agents import configuration
from src.backend.agents.prompts import (
    default_blog_structure,
    blog_planner_instructions,
    main_body_section_writer_instructions,
    intro_conclusion_instructions,
    linkedin_post_instructions,
    twitter_post_instructions,
    tags_generator,
    query_creator,
    reddit_query_creator,
    summary_instructions,
    relevant_search_prompt,
    relevant_reddit_prompt,
    twitter_query_creator
)
from src.backend.agents.tools import RedditSearch, WebSearch
from src.backend.clients.llm import LLMClient, HumanMessage, SystemMessage
from src.backend.agents.state import BlogState, BlogStateInput, BlogStateOutput, SectionState
from src.backend.agents.utils import *
from src.backend.db.supabaseclient import supabase_client
from src.backend.extraction.factory import ConverterRegistry, ExtracterRegistry
import atexit
from src.backend.utils.logger import setup_logger
from src.backend.utils.general import safe_json_loads

# Setup logger
logger = setup_logger(__name__)

supabase: Client = supabase_client()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class AgentWorkflow:

    def __init__(self):
        logger.info("Initializing AgentWorkflow")
        self.llm = LLMClient()
        self.websearcher = WebSearch(provider='google', num_results=15)
        self.reddit_searcher=RedditSearch()
        self.builder = StateGraph(
            BlogState,
            input=BlogStateInput,
            output=BlogStateOutput
            # config_schema=configuration.Configuration,
        )
        dsn = os.getenv("SUPABASE_POSTGRES_DSN", "")
        connection_kwargs = {
            "autocommit": True,
            "keepalives": 1,
            "keepalives_idle": 60,
            "keepalives_interval": 10,
            "keepalives_count": 5,
        }
        self.conn = Connection.connect(dsn, **connection_kwargs)
        self.checkpointer = PostgresSaver(self.conn)

        # self.checkpointer.setup()

        # Add finalizer to close connection when object is destroyed
        atexit.register(self._cleanup)
        self.graph = self.setup_workflow()
        self.generic_converter=ConverterRegistry.get_converter("generic")
        self.html_converter=ConverterRegistry.get_converter("html")
        self.arxiv_extracter=ExtracterRegistry.get_extractor("arxiv")
        self.github_extracter=ExtracterRegistry.get_extractor("github")
        self.reddit_extracter=ExtracterRegistry.get_extractor("reddit")

    def _cleanup(self):
        """Close database connection on exit"""
        if hasattr(self, 'conn'):
            self.conn.close()

    def generate_blog_plan(self, state: BlogState):
        """Generate the report plan"""
        reference_link = state.input_url
        media_markdown = state.media_markdown
        user_instructions = state.input_content
        blog_structure = default_blog_structure

        system_instructions_sections = blog_planner_instructions.format(
            user_instructions=user_instructions, blog_structure=blog_structure
        )

        report_sections = self.llm.invoke(
            [
                SystemMessage(content=system_instructions_sections),
                HumanMessage(
                    content="Generate the sections of the blog. Your response must include a 'sections' field containing a list of sections. Each section must have: name, description, and content fields."
                ),
            ]
        )

        pattern = r"```json\n([\s\S]*?)\n```"
        match = re.search(pattern, report_sections)

        if match:
            parsed = safe_json_loads(match.group(1))
        else:
            parsed = {"sections": []}

        # Convert dict items into actual Section objects
        sections = [Section(**sec) for sec in parsed.get("sections", [])]

        return {"sections": sections}

    def write_section(self, state: SectionState):
        """Write a section of the report"""
        section = state.section
        reference_link = state.input_url
        user_instructions = state.input_content
        media_markdown = state.media_markdown
        url_source_str = reference_link

        system_instructions = main_body_section_writer_instructions.format(
            section_name=section.name,
            section_topic=section.description,
            user_instructions=user_instructions,
            source_urls=url_source_str,
            media_markdown=media_markdown,
        )

        section_content = self.llm.invoke(
            [
                SystemMessage(content=system_instructions),
                HumanMessage(
                    content="Generate a blog section based on the provided information."
                ),
            ]
        )

        section.content = section_content
        return {"completed_sections": [section]}

    def write_final_sections(self, state: SectionState):
        """Write final sections of the report, which do not require web search and use the completed sections as context"""
        section = state.section

        system_instructions = intro_conclusion_instructions.format(
            section_name=section.name,
            section_topic=section.description,
            main_body_sections=state.blog_main_body_sections,
            source_urls=state.urls,
        )

        section_content = self.llm.invoke([
            SystemMessage(content=system_instructions),
            HumanMessage(content="Generate an intro/conclusion section based on the provided main body sections.")
        ])
        section.content = section_content

        return {"completed_sections": [section]}

    def initiate_section_writing(self, state: BlogState):
        """This is the "map" step when we kick off web research for some sections of the report"""
        return [
            Send(
                "write_section",
                SectionState(
                    section=s,
                    input_url=state.input_url,
                    input_content=state.input_content,
                    media_markdown=state.media_markdown,
                    urls=[state.input_url],
                    completed_sections=[],  # Initialize with empty list
                ),
            )
            for s in state.sections
            if s.main_body
        ]

    def gather_completed_sections(self, state: BlogState):
        """Gather completed main body sections"""
        completed_sections = state.completed_sections
        completed_report_sections = format_sections(completed_sections)
        return {"blog_main_body_sections": completed_report_sections}

    def initiate_final_section_writing(self, state: BlogState):
        """This is the "map" step when we kick off research on any sections that require it using the Send API"""
        return [
            Send(
                "write_final_sections",
                SectionState(
                    input_url=state.input_url,
                    input_content=state.input_content,
                    section=s,
                    blog_main_body_sections=state.blog_main_body_sections,
                    urls=[state.input_url],
                    completed_sections=[],  # Initialize with empty list
                ),
            )
            for s in state.sections
            if not s.main_body
        ]

    def compile_final_blog(self, state: BlogState):
        """Compile the final blog"""
        sections = state.sections
        completed_sections = {s.name: s.content for s in sections}

        for section in sections:
            section.content = completed_sections[section.name]

        all_sections = "\n\n".join([s.content for s in sections])
        #ToDO: Add title to the final blog
        blog_title_matches = re.findall(r"^#\s+(.*)$", all_sections, re.MULTILINE)
        blog_title = blog_title_matches[0] if blog_title_matches else ""
        return {"final_blog": all_sections, "blog_title": blog_title}

    def write_twitter_post(self, state: BlogState):
        """Write the Twitter post"""
        final_blog = state.final_blog
        twitter_post = self.llm.invoke([
            SystemMessage(content=twitter_post_instructions.format(final_blog=final_blog)),
            HumanMessage(content="Generate a Twitter post based on the provided article")
        ])
        return {"twitter_post": twitter_post}

    def write_linkedin_post(self, state: BlogState):
        """Write the LinkedIn post"""
        final_blog = state.final_blog
        linkedin_post = self.llm.invoke([
            SystemMessage(content=linkedin_post_instructions.format(final_blog=final_blog)),
            HumanMessage(content="Generate a LinkedIn post based on the provided article")
        ])
        return {"linkedin_post": linkedin_post}

    def generate_tags(self, state: BlogState):
        """Generate tags for the blog"""
        linkedin_post = state.final_blog

        # Cleaner version
        result = self.llm.invoke([
            SystemMessage(content=tags_generator.format(linkedin_post=linkedin_post)),
            HumanMessage(content="Generate tags for the blog.")
        ])

        tags_match = re.findall(r"<tags>(.*?)</tags>", result, re.DOTALL)
        if tags_match:
            tags_string = tags_match[0].strip()
            try:
                tags = ast.literal_eval(tags_string)
                tags = [tag.strip().strip('"') for tag in tags]
            except:
                tags = [tag.strip().strip('"[]') for tag in tags_string.split(",")]
        else:
            tags = []
        return {"tags": tags}

    def handle_feedback(self, state: BlogState):
        """Process feedback and regenerate content"""
        if not state.feedback:
            return state

        # Determine which content to modify based on post_types
        if "blog" in state.post_types:
            content = state.final_blog
        elif "twitter" in state.post_types:
            content = state.twitter_post
        elif "linkedin" in state.post_types:
            content = state.linkedin_post
        else:
            return state

        # System prompt for modifying content based on feedback
        system_prompt = f"""You are an AI assistant helping to modify content based on user feedback.
        Original content:
        {content}
        
        User feedback:
        {state.feedback}
        
        Please modify the content according to the feedback while maintaining the technical accuracy and quality."""

        # Invoke the LLM to modify the content
        modified_content = self.llm.invoke(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content="Modify the content based on the feedback"),
            ]
        )

        # Update the state with the modified content
        if "blog" in state.post_types:
            return {
                "final_blog": modified_content,
                "feedback_applied": True,
                "feedback": None,
            }
        elif "twitter" in state.post_types:
            return {
                "twitter_post": modified_content,
                "feedback_applied": True,
                "feedback": None,
            }
        elif "linkedin" in state.post_types:
            return {
                "linkedin_post": modified_content,
                "feedback_applied": True,
                "feedback": None,
            }
        else:
            return state

#-------------Agent helpers----------------

    def fetch_urls_and_media(self, tweet_id):
        """
        Fetches URLs and media associated with a tweet from the database.
        
        Args:
            tweet_id (str): The ID of the tweet to fetch data for
            
        Returns:
            dict: Contains source_id, urls and media data
            
        Raises:
            ValueError: If no source is found for the tweet_id
        """
        try:
            # Get source record
            source_id = self._get_source_id(tweet_id)
            
            # Fetch associated data
            urls = self._fetch_url_references(source_id)
            media = self._fetch_media(source_id)

            return {
                "tweet_id": tweet_id,
                "source_id": source_id,
                "urls": urls,
                "media": media
            }

        except Exception as e:
            logger.error(f"Error fetching data for tweet {tweet_id}: {str(e)}")
            raise

    def _get_source_id(self, tweet_id):
        """Helper method to get source_id for a tweet"""
        source = (supabase.table("sources")
                 .select("source_id")
                 .eq("source_identifier", tweet_id)
                 .single()
                 .execute())
                 
        if not source.data:
            raise ValueError(f"No source found for tweet_id: {tweet_id}")
            
        return source.data["source_id"]

    def _fetch_url_references(self, source_id):
        """Helper method to fetch URL references"""
        response = (supabase.table("url_references")
                   .select("*")
                   .eq("source_id", source_id)
                   .execute())
        return response.data

    def _fetch_media(self, source_id):
        """Helper method to fetch media"""
        response = (supabase.table("media")
                   .select("*")
                   .eq("source_id", source_id)
                   .execute())
        return response.data

    def _fetch_content_metadata(self, source_id):
        """Helper method to fetch content metadata"""
        response = (supabase.table("source_metadata")
                   .select("*")
                   .eq("source_id", source_id)
                   .execute())
        return response.data
#-------------Agent main workflow----------------

    def _summarize_websearch_results(self, urls, search_query):
        """Summarize websearch results"""

        research_prompt = summary_instructions.format(source_urls="\n".join(urls), topic=search_query)
        
        llm_response= self.llm.invoke(
            [
                HumanMessage(content=research_prompt)
            ]
        )
        
        return llm_response    
    
    def _relevant_search_selection(self, urls,query):
        """Select relevant search results"""

        # if payload.get("topic"):
        #     search_query = payload["topic"]
        # elif payload.get("reddit_query"):
        #     search_query = payload["reddit_query"]
        # elif :
        #     search_query = ""

        relevance_prompt = relevant_search_prompt.format(search_results="\n".join(urls),user_query=query)
        
        llm_response= self.llm.invoke(
            [
                HumanMessage(content=relevance_prompt)
            ]
        )

        def parse_url_string(relevant_match):
            """Parse string of comma-separated URLs into list"""
            if not relevant_match:
                return []
                
            # Extract string and remove brackets
            url_string = relevant_match[0].strip('[]')
            
            # Split by comma and clean each URL
            urls = [url.strip() for url in url_string.split(',')]
            
            return urls
        
        relevant_match = re.findall(r"<relevant_urls>(.*?)</relevant_urls>", llm_response, re.DOTALL)
        relevant_urls = parse_url_string(relevant_match)
        return relevant_urls
                
    
    def _relevant_reddit_post_selection(self,reddit_obj,topic):
        """Select relevant search results"""

        pre_relevance_prompt=""
        for data in reddit_obj:
            content = data['content']
            title = data['title']
            url=data['url']

            pre_relevance_prompt += f"""
                **Post Title:** {title}
                **Post URL:** {url}
                **Post Content:** {content}

                -----------------------------------------
            """

        relevance_prompt = relevant_reddit_prompt.format(reddit_content=pre_relevance_prompt,topic=topic)
        
        llm_response= self.llm.invoke(
            [
                HumanMessage(content=relevance_prompt)
            ]
        )

        def parse_url_string(relevant_match):
            """Parse string of comma-separated URLs into list"""
            if not relevant_match:
                return []
                
            # Extract string and remove brackets
            url_string = relevant_match[0].strip('[]')
            
            # Split by comma and clean each URL
            urls = [url.strip() for url in url_string.split(',')]
            
            return urls
        
        relevant_match = re.findall(r"<relevant_urls>(.*?)</relevant_urls>", llm_response, re.DOTALL)
        relevant_urls = parse_url_string(relevant_match)
        return relevant_urls
    
    def _initialize_workflow(self, payload,thread_id):
        """Initialize workflow with thread ID and empty source data"""
        thread_id = payload.get("thread_id") or thread_id
        return thread_id, None, None, None

    def _handle_url_workflow(self, payload, thread_id, user):
        """Handle workflow for URL-based content"""
        source_id, url_meta, media_meta = self._setup_web_url_source(payload, thread_id, user)
        content =self._process_url_content(url_meta)
        media_markdown = get_media_content_url(media_meta)
        return BlogStateInput(
            input_url=payload["url"],
            input_content=content,
            post_types=payload.get("post_types", ["blog"]),
            thread_id=thread_id,
            media_markdown=media_markdown,
        ), source_id
    
    def _handle_topic_workflow(self, payload, thread_id, user):
        """Handle workflow for URL-based content"""
        reference_content = ''
        query=self._query_rewriter(payload['topic'],type='topic')
        urls=self.websearcher.search(query).get_all_urls()
        urls=self._relevant_search_selection(urls,query)

        source_id,url_meta = self._setup_topic_source(payload,urls ,thread_id, user)

        # reference_content=self._summarize_websearch_results(urls, query)
        for meta in url_meta:
            try:
                # url_meta = get_url_metadata(url)
                content = self._process_url_content(meta)
                reference_content += f"# Source 1: \n **Source URL:* {meta['original_url']} \n **Raw Content**:\n {content} \n\n"
            except Exception as e:
                logger.warning(f"Failed to process URL {meta['original_url']}: {str(e)}")
                continue

        return BlogStateInput(
            input_topic=payload["topic"],
            input_url='\n'.join(urls),
            input_content=reference_content,
            post_types=payload.get("post_types", ["blog"]),
            thread_id=thread_id
        ), source_id
    
    def _handle_reddit_workflow(self, payload, thread_id, user):
        """Handle workflow for reddit-based content"""
        reference_content = ''
        query=self._query_rewriter(payload['reddit_query'],type='reddit')
        urls=self.websearcher.search(query).get_all_urls()
        urls=self._relevant_search_selection(urls,query)

        # if payload.get("subreddit"):
        #     reddit_obj=self.reddit_searcher.search(payload['reddit_query'],subreddit=payload.get("subreddit"))
        # else:
        reddit_obj=[]
        for url in urls:
            reddit_obj.append(self.reddit_searcher.search(url)[0])

        # urls=self._relevant_reddit_post_selection(reddit_obj,payload['reddit_query'])

        #filter reddit_obj based on the selected urls
        # reddit_obj=[data for data in reddit_obj if data['url'] in urls]
    
        # reddit_summary=self.reddit_extracter.create_summary(reddit_obj)
        reddit_pre_summary=self.reddit_extracter._create_pre_summary(reddit_obj)

        source_id = self._setup_reddit_source(payload ,thread_id, user)


        return BlogStateInput(
            input_reddit=payload["reddit_query"],
            input_url='',
            input_content=reddit_pre_summary,
            post_types=payload.get("post_types", ["blog"]),
            thread_id=thread_id
        ), source_id
    

    def _query_rewriter(self, query,type=None):
        """Rewrite tweet text for queryable content"""

        if type=='reddit':
            rewriter_instructions = reddit_query_creator.format(user_query_short=query)
        elif type=='tweet':
            rewriter_instructions = twitter_query_creator.format(user_query_short=query)
        else:
            rewriter_instructions = query_creator.format(user_query_short=query)
        
        llm_response= self.llm.invoke(
            [
                HumanMessage(content=rewriter_instructions)
            ]
        )

        query_match = re.findall(r"<query>(.*?)</query>", llm_response, re.DOTALL)
        if query_match:
            return query_match[0].strip()
        
        return query

    def _handle_tweet_workflow(self, payload, thread_id, user):
        """Handle workflow for tweet-based content"""
        source_id, url_meta, media_meta,tweet_text = self._setup_tweet_source(payload, thread_id, user)
        reference_content, reference_link = get_tweet_reference_content(url_meta)
        media_markdown = get_tweet_media(media_meta)

        if not url_meta:
            reference_content = ''            
            query=self._query_rewriter(tweet_text,type='tweet')
            # first call llm to rewrite teweet text for searchable queries
            # second call the tool to research content based on the rewritten tweet text
            urls=self.websearcher.search(query).get_all_urls()
            urls=self._relevant_search_selection(urls,query)

            for url in urls:
                try:
                    url_meta = get_url_metadata(url)
                    content = self._process_url_content(url_meta)
                    reference_content += f"For Source URL: {url}, below is the content \n {content} \n\n"
                except Exception as e:
                    logger.warning(f"Failed to process URL {url}: {str(e)}")
                    continue
            # select appropriate urls from the research results
            # reference_content=''.join([f"URL: {url} \n {self.generic_converter.convert(url)} \n\n" for url in urls ])
            # use markdownit to convert the urls to markdown

            return BlogStateInput(
                input_url=reference_link,
                input_content=reference_content,
                input_topic=tweet_text,
                media_markdown=media_markdown,
                post_types=payload.get("post_types", ["blog"]),
                thread_id=thread_id,
            ), source_id

        return BlogStateInput(
            input_url=reference_link,
            input_content=reference_content,
            media_markdown=media_markdown,
            post_types=payload.get("post_types", ["blog"]),
            thread_id=thread_id,
        ), source_id

    def _generate_new_content(self, test_input, thread_id, source_id, payload, user):
        """Generate new content using graph workflow"""
        config = {"configurable": {"thread_id": thread_id}}
        result = self.graph.invoke(test_input, config=config)
        self._store_new_content(result, thread_id, source_id, payload, user)
        return result   

    def run_generic_workflow(self, payload, thread_id,user):
        """Universal handler for all workflow types with database integration"""
        logger.info(f"Starting generic workflow with payload type: {type(payload).__name__}")
        try:
            thread_id, source_id, url_meta, media_meta = self._initialize_workflow(payload,thread_id)
            logger.debug(f"Initialized workflow: thread_id={thread_id}, source_id={source_id}")

            # Handle existing thread with no feedback
            if payload.get("thread_id") and not payload.get("feedback"):
                logger.info("Handling existing thread without feedback")
                return BlogStateOutput(**self._handle_social_post_generation(thread_id, payload, user))
            
            # Handle feedback
            elif payload.get("feedback") and payload.get("thread_id"):
                logger.info(f"Handling feedback for thread {thread_id}")
                return BlogStateOutput(**self._handle_feedback(thread_id, payload))
            
            # Handle new content generation
            else:
                logger.info("Handling new content generation")
                if payload.get("url"):
                    logger.debug(f"Processing URL: {payload['url']}")
                    test_input, source_id = self._handle_url_workflow(payload, thread_id, user)
                elif payload.get("tweet_id"):
                    logger.debug(f"Processing tweet: {payload['tweet_id']}")
                    test_input, source_id = self._handle_tweet_workflow(payload, thread_id, user)
                elif payload.get("topic"):
                    logger.debug(f"Processing topic: {payload['topic']}")
                    test_input, source_id = self._handle_topic_workflow(payload, thread_id, user)
                elif payload.get("reddit_query"):
                    logger.debug(f"Processing reddit query: {payload['reddit_query']}")
                    test_input, source_id = self._handle_reddit_workflow(payload, thread_id, user)
                else:
                    logger.error("Invalid payload - missing required fields")
                    raise ValueError("Invalid payload - must contain url, tweet_id or feedback")

                result = self._generate_new_content(test_input, thread_id, source_id, payload, user)
                logger.info("Content generation completed successfully")
                return BlogStateOutput(**result)

        except Exception as e:
            logger.error(f"Error in workflow: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    def _validate_existing_content(self, source_id, payload):
        """Check if content already exists for given source"""
        existing_content = (
            supabase.table("content_sources")
            .select("*")
            .eq("source_id", source_id)
            .execute()
        )
        if existing_content.data:
            raise ValueError(f"Content already exists for this {payload.get('url', 'tweet')}")
        return True

    def _create_source_record(self, url, thread_id, source_type_name, user):
        """Create a new source record"""
        source_type = (
            supabase.table("source_types")
            .select("*")
            .eq("name", source_type_name)
            .execute()
        )
        source_data = {
            "source_type_id": source_type.data[0]["source_type_id"],
            "source_identifier": url,
            "batch_id": thread_id,
            "profile_id": user["id"]
        }
        source = supabase.table("sources").insert(source_data).execute()
        return source.data[0]["source_id"]

    def _handle_url_references(self, source_id, url_meta):
        """Handle URL reference storage"""
        url_ref_data = {
            "source_id": source_id,
            "url": url_meta["original_url"],
            "type": url_meta["type"],
            "domain": url_meta["domain"],
            "content_type": url_meta["content_type"],
            "file_category": url_meta["file_category"],
        }
        supabase.table("url_references").insert(url_ref_data).execute()

    def _handle_media_storage(self, source_id, media_meta):
        """Handle media storage"""
        if media_meta:
            for media in media_meta:
                media_data = {
                    "source_id": source_id,
                    "media_url": media["original_url"],
                    "media_type": media["type"],
                }
                supabase.table("media").insert(media_data).execute()

    def _setup_topic_source(self, payload,urls, thread_id, user):
        """Setup source records for web URL"""
        existing_source = (
            supabase.table("sources")
            .select("*")
            .eq("source_identifier", payload["topic"])
            .eq("profile_id", user["id"])
            .execute()
        )

        url_meta=[]
        if existing_source.data:
            source_id = existing_source.data[0]["source_id"]
            self._validate_existing_content(source_id, payload)
            for url in urls:
                meta= get_url_metadata(url)
                if meta:
                    url_meta.append(meta)
            return source_id,url_meta

        source_id = self._create_source_record(payload["topic"], thread_id, "topic", user)

        for url in urls:
            meta=get_url_metadata(url)
            if meta:
                url_meta.append(meta)
                self._handle_url_references(source_id, meta)
                
        return source_id, url_meta

    def _setup_reddit_source(self, payload, thread_id, user):
        """Setup source records for web URL"""
        existing_source = (
            supabase.table("sources")
            .select("*")
            .eq("source_identifier", payload["reddit_query"])
            .eq("profile_id", user["id"])
            .execute()
        )

        if existing_source.data:
            source_id = existing_source.data[0]["source_id"]
            self._validate_existing_content(source_id, payload)
            
            return source_id

        source_id = self._create_source_record(payload["reddit_query"], thread_id, "reddit", user)
                
        return source_id
    
    def _setup_web_url_source(self, payload, thread_id, user):
        """Setup source records for web URL"""
        existing_source = (
            supabase.table("sources")
            .select("*")
            .eq("source_identifier", payload["url"])
            .eq("profile_id", user["id"])
            .execute()
        )

        if existing_source.data:
            source_id = existing_source.data[0]["source_id"]
            self._validate_existing_content(source_id, payload)
            url_meta = get_url_metadata(payload["url"])
            media_meta = get_media_links(payload["url"])
            return source_id, url_meta, media_meta

        url_meta = get_url_metadata(payload["url"])
        media_meta = get_media_links(payload["url"])
        source_id = self._create_source_record(payload["url"], thread_id, "web_url", user)
        
        self._handle_url_references(source_id, url_meta)
        self._handle_media_storage(source_id, media_meta)
        
        return source_id, url_meta, media_meta

    def _setup_tweet_source(self, payload, thread_id, user):
        """Setup source records for tweet"""
        existing_source = (
            supabase.table("sources")
            .select("*")
            .eq("source_identifier", payload["tweet_id"])
            .eq("profile_id", user["id"])
            .execute()
        )

        if existing_source.data:
            source_id = existing_source.data[0]["source_id"]
            self._validate_existing_content(source_id, payload)
            tweet_data = self.fetch_urls_and_media(payload["tweet_id"])
            tweet_meta = self._fetch_content_metadata(source_id)
            tweet_text = [meta['value'] for meta in tweet_meta if meta.get("key",'')=='full_text']
            return source_id, tweet_data.get("urls", []), tweet_data.get("media", []),tweet_text[0]

        return None, None, None, None

    def _handle_social_post_generation(self, thread_id, payload, user):
        """Handle generation of social media posts"""
        content = (
            supabase.table("content")
            .select("*")
            .eq("thread_id", thread_id)
            .execute()
        )
        if not content.data:
            raise ValueError("No content found for thread_id")

        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(
            config,
            values={"post_types": payload.get("post_types", ["twitter", "linkedin"])},
        )
        result = self.graph.invoke(None, config=config, debug=True)

        self._store_social_content(thread_id, payload, result, user)
        return result

    def _handle_feedback(self, thread_id, payload):
        """Handle feedback processing"""
        # Check if content exists for thread_id
        existing_content = (
            supabase.table("content")
            .select("*")
            .eq("thread_id", thread_id)
            .execute()
        )
        
        if not existing_content.data:
            raise ValueError(f"No content found for thread_id: {thread_id}")

        config = {"configurable": {"thread_id": thread_id}}
        self.graph.update_state(
            config,
            values={
                "feedback": payload["feedback"],
                "post_types": payload.get("post_types", ["blog"]),
                "feedback_applied": False,
            },
        )
        result = self.graph.invoke(None, config)
        self.graph.update_state(config, values={"feedback": None})

        self._update_content_with_feedback(thread_id, payload, result)
        return result

    def _store_social_content(self, thread_id, payload, result, user):
        """Store generated social media content"""
        for post_type in payload.get("post_types", ["twitter", "linkedin"]):
            content_type = (
                supabase.table("content_types")
                .select("*")
                .eq("name", post_type)
                .execute()
            )
            existing_content = (
                supabase.table("content")
                .select("*")
                .eq("thread_id", thread_id)
                .eq("content_type_id", content_type.data[0]["content_type_id"])
                .execute()
            )

            if not existing_content.data:
                content_body = result.get(
                    "final_blog" if post_type == "blog" else f"{post_type}_post"
                )
                if content_body:
                    content_data = {
                        "profile_id": user["id"],
                        "content_type_id": content_type.data[0]["content_type_id"],
                        "body": content_body,
                        "status": "Draft",
                        "thread_id": thread_id,
                    }
                    supabase.table("content").insert(content_data).execute()

    def _update_content_with_feedback(self, thread_id, payload, result):
        """Update existing content with feedback"""
        for post_type in payload.get("post_types", ["blog", "twitter", "linkedin"]):
            content_body = result.get(
                "final_blog" if post_type == "blog" else f"{post_type}_post"
            )
            if content_body:
                content_type = (
                    supabase.table("content_types")
                    .select("*")
                    .eq("name", post_type)
                    .execute()
                )
                content_data = {"body": content_body, "status": "Draft"}
                supabase.table("content").update(content_data).eq(
                    "thread_id", thread_id
                ).eq(
                    "content_type_id", content_type.data[0]["content_type_id"]
                ).execute()

    def _store_new_content(self, result, thread_id, source_id, payload, user):
        """Store newly generated content"""
        try:
            for post_type in payload.get("post_types", ["blog"]):
                # Validate post type exists
                content_type_result = (
                    supabase.table("content_types")
                    .select("*")
                    .eq("name", post_type)
                    .execute()
                )
                
                if not content_type_result.data:
                    logging.error(f"Content type {post_type} not found")
                    continue

                # Clean and validate content
                blog_title = result.get("blog_title", "").strip() if post_type == "blog" else None
                blog_body = result.get("final_blog" if post_type == "blog" else f"{post_type}_post", "")
                
                if isinstance(blog_body, str):
                    blog_body = blog_body.strip()

                content_data = {
                    "profile_id": user["id"],
                    "content_type_id": content_type_result.data[0]["content_type_id"],
                    "title": blog_title,
                    "body": blog_body,
                    "status": "Draft",
                    "thread_id": thread_id,
                }

                # Insert content with error handling
                try:
                    content = supabase.table("content").insert(content_data).execute()
                    content_id = content.data[0]["content_id"]

                    # Store source reference if provided
                    if source_id:
                        content_source_data = {
                            "content_id": content_id,
                            "source_id": source_id,
                        }
                        supabase.table("content_sources").insert(content_source_data).execute()

                    # Store tags
                    if result:
                        self._store_tags(result, content_id)

                except Exception as e:
                    logging.error(f"Error storing content: {str(e)}")
                    raise Exception(f"Failed to store content: {str(e)}")

        except Exception as e:
            logging.error(f"Error in _store_new_content: {str(e)}")
            raise

    def _store_tags(self, result, content_id):
        """Store tags for content"""
        if result.get("tags"):
            for tag_name in result["tags"]:
                tag = supabase.table("tags").select("*").eq("name", tag_name).execute()
                if not tag.data:
                    tag = supabase.table("tags").insert({"name": tag_name}).execute()
                tag_id = tag.data[0]["tag_id"]

                content_tag_data = {
                    "content_id": content_id,
                    "tag_id": tag_id,
                }
                supabase.table("content_tags").insert(content_tag_data).execute()

    def _process_url_content(self, url_meta):
        """Helper to process URL content based on type"""
        # url_meta = utils.get_url_metadata(url)

        if url_meta["type"] == "html":
            return self.generic_converter.convert(url_meta['original_url']) #self.converter_factory.create_converter('generic').convert(url_meta['original_url'])
        elif url_meta["type"] == "pdf":
            return self.generic_converter.convert(url_meta['original_url']) #self.converter_factory.create_converter('generic').extract_pdf(input_file=url_meta["original_url"])
        elif url_meta["type"] == "arxiv":
            pdf_url=self.arxiv_extracter.extract(url_meta["original_url"])['url']
            return self.generic_converter.convert(pdf_url)
        elif url_meta["type"] == "github":
            readme_url=self.github_extracter.extract(url_meta["original_url"])['readme_url']
            return self.generic_converter.convert(readme_url)
        elif url_meta["type"] == "reddit":
            reddit_obj=self.reddit_extracter.extract(url_meta["original_url"])
            return reddit_obj['summary']
        else:
            return url_meta["content"]

        # Update state after generating posts

    def update_linkedin_post_status(self, state: BlogState):
        # Generate LinkedIn post
        return {"linkedin_post_generated": True}

    def update_tweet_post_status(self, state: BlogState):
        # Generate Twitter post
        return {"tweet_post_generated": True}

    def setup_workflow(self):
        # Add nodes
        self.builder.add_node("generate_blog_plan", self.generate_blog_plan)
        self.builder.add_node("write_section", self.write_section)
        self.builder.add_node("compile_final_blog", self.compile_final_blog)
        self.builder.add_node(
            "gather_completed_sections", self.gather_completed_sections
        )
        self.builder.add_node("write_final_sections", self.write_final_sections)
        self.builder.add_node("write_twitter_post", self.write_twitter_post)
        self.builder.add_node("write_linkedin_post", self.write_linkedin_post)
        # self.builder.add_node("generate_tags", self.generate_tags)
        self.builder.add_node("handle_feedback", self.handle_feedback)

        # Add basic flow edges
        self.builder.add_edge(START, "generate_blog_plan")
        self.builder.add_conditional_edges(
            "generate_blog_plan", self.initiate_section_writing, ["write_section"]
        )
        self.builder.add_edge("write_section", "gather_completed_sections")
        self.builder.add_conditional_edges(
            "gather_completed_sections",
            self.initiate_final_section_writing,
            ["write_final_sections"],
        )
        self.builder.add_edge("write_final_sections", "compile_final_blog")
        # self.builder.add_edge("compile_final_blog", "generate_tags")

        # Post-tags routing logic
        def route_after_tags(state: BlogState):
            if state.feedback:
                return "handle_feedback"
            if "linkedin" in state.post_types and not state.linkedin_post:
                return "write_linkedin_post"
            if "twitter" in state.post_types and not state.twitter_post:
                return "write_twitter_post"
            return END

        # Post-LinkedIn routing logic
        def route_after_linkedin(state: BlogState):
            if state.feedback:
                return "handle_feedback"
            if "twitter" in state.post_types and not state.twitter_post:
                return "write_twitter_post"
            return END

        # Post-Twitter routing logic
        def route_after_twitter(state: BlogState):
            if state.feedback:
                return "handle_feedback"
            if "linkedin" in state.post_types and not state.linkedin_post:
                return "write_linkedin_post"
            return END

        # Add routing edges
        self.builder.add_conditional_edges(
            "compile_final_blog",
            route_after_tags,
            ["write_linkedin_post", "write_twitter_post", "handle_feedback", END],
        )

        self.builder.add_conditional_edges(
            "write_linkedin_post",
            route_after_linkedin,
            ["write_twitter_post", "handle_feedback", END],
        )

        self.builder.add_conditional_edges(
            "write_twitter_post",
            route_after_twitter,
            ["write_linkedin_post", "handle_feedback", END],
        )

        # Feedback handling edge - routes back to appropriate node based on post type
        def route_after_feedback(state: BlogState):
            if state.feedback:
                return "handle_feedback"
            if "linkedin" in state.post_types and not state.linkedin_post:
                return "write_linkedin_post"
            if "twitter" in state.post_types and not state.twitter_post:
                return "write_twitter_post"
            return END

        self.builder.add_conditional_edges(
            "handle_feedback",
            route_after_feedback,
            ["handle_feedback", "write_linkedin_post", "write_twitter_post", END],
        )

        # Compile graph with interrupts after key steps
        graph = self.builder.compile(
            checkpointer=self.checkpointer,
            interrupt_after=[
                # "generate_tags",
                "compile_final_blog",
                "write_linkedin_post",
                "write_twitter_post",
            ],
        )
        return graph


if __name__ == "__main__":

    agent = AgentWorkflow()
    # Initial content generation from URL
    result = agent.run_generic_workflow(
        {
            "thread_id": "8f38abae-4085-41bd-bc23-022b5320313d",
            "url": "https://huggingface.co/Qwen/QVQ-72B-Preview",
            "post_types": ["linkedin"],
            "feedback": "Remove the introductory phrases and add more examples",
        }
    )
