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
from langchain_core.messages import HumanMessage, SystemMessage
from psycopg import Connection
from supabase import Client

# from src.agents import configuration
from src.agents.llm import get_gemini
from src.agents.prompts import (
    default_blog_structure,
    blog_planner_instructions,
    main_body_section_writer_instructions,
    intro_conclusion_instructions,
    linkedin_post_instructions,
    twitter_post_instructions,
    tags_generator,
)
from src.agents.state import BlogState, BlogStateInput, BlogStateOutput, SectionState
from src.agents.utils import *
from src.db.supabaseclient import supabase_client
from src.extractors.docintelligence import DocumentExtractor

supabase: Client = supabase_client()
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
supabase: Client = supabase_client()


class AgentWorkflow:

    def __init__(self):
        self.llm = get_gemini()
        self.builder = StateGraph(
            BlogState,
            input=BlogStateInput,
            output=BlogStateOutput
            # config_schema=configuration.Configuration,
        )
        dsn = os.getenv("SUPABASE_POSTGRES_DSN", "")
        connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }
        conn = Connection.connect(dsn, **connection_kwargs)
        self.checkpointer = PostgresSaver(conn)
        self.graph = self.setup_workflow()
        self.extractor = DocumentExtractor()

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
        match = re.search(pattern, report_sections.content)

        if match:
            parsed = json.loads(match.group(1))
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

        section.content = section_content.content
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
        section.content = section_content.content

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
        completed_sections = {s.name: s.content for s in state.completed_sections}

        for section in sections:
            section.content = completed_sections[section.name]

        all_sections = "\n\n".join([s.content for s in sections])
        blog_title = re.findall(r"^#\s+(.*)$", all_sections, re.MULTILINE)[0]
        return {"final_blog": all_sections, "blog_title": blog_title}

    def write_twitter_post(self, state: BlogState):
        """Write the Twitter post"""
        final_blog = state.final_blog
        twitter_post = self.llm.invoke([
            SystemMessage(content=twitter_post_instructions.format(final_blog=final_blog)),
            HumanMessage(content="Generate a Twitter post based on the provided article")
        ])
        return {"twitter_post": twitter_post.content}

    def write_linkedin_post(self, state: BlogState):
        """Write the LinkedIn post"""
        final_blog = state.final_blog
        linkedin_post = self.llm.invoke([
            SystemMessage(content=linkedin_post_instructions.format(final_blog=final_blog)),
            HumanMessage(content="Generate a LinkedIn post based on the provided article")
        ])
        return {"linkedin_post": linkedin_post.content}

    def generate_tags(self, state: BlogState):
        """Generate tags for the blog"""
        linkedin_post = state.final_blog

        # Cleaner version
        result = self.llm.invoke([
            SystemMessage(content=tags_generator.format(linkedin_post=linkedin_post)),
            HumanMessage(content="Generate tags for the blog.")
        ])

        tags_match = re.findall(r"<tags>(.*?)</tags>", result.content, re.DOTALL)
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
                "final_blog": modified_content.content,
                "feedback_applied": True,
                "feedback": None,
            }
        elif "twitter" in state.post_types:
            return {
                "twitter_post": modified_content.content,
                "feedback_applied": True,
                "feedback": None,
            }
        elif "linkedin" in state.post_types:
            return {
                "linkedin_post": modified_content.content,
                "feedback_applied": True,
                "feedback": None,
            }
        else:
            return state

    def fetch_urls_and_media(self, tweet_id):
        try:
            # Step 1: Get the source_id for the given tweet_id
            source_response = (
                supabase.table("sources")
                .select("source_id")
                .eq("source_identifier", tweet_id)
                .execute()
            )

            if not source_response.data:
                return {"error": f"No source found for tweet_id: {tweet_id}"}

            source_id = source_response.data[0]["source_id"]

            # Step 2: Fetch all URLs associated with the source_id
            urls_response = (
                supabase.table("url_references")
                .select("*")
                .eq("source_id", source_id)
                .execute()
            )

            urls = urls_response.data

            # Step 3: Fetch all media associated with the source_id
            media_response = (
                supabase.table("media").select("*").eq("source_id", source_id).execute()
            )

            media = media_response.data

            # Step 4: Combine URLs and media into a single JSON response
            response = {
                "tweet_id": tweet_id,
                "source_id": source_id,
                "urls": urls,
                "media": media,
            }

            return response

        except Exception as e:
            return {"error": f"Error fetching data: {e}"}

    def run_generic_workflow(self, payload):
        """Universal handler for all workflow types with database integration"""
        try:
            # Start database transaction
            thread_id = payload.get("thread_id") or str(uuid.uuid4())

            # 1. Initial Database Setup
            def setup_initial_records(payload):
                if payload.get("url"):
                    # Check if source already exists for this URL
                    existing_source = (
                        supabase.table("sources")
                        .select("*")
                        .eq("source_identifier", payload["url"])
                        .execute()
                    )

                    if existing_source.data:
                        # Check if content exists for this source
                        source_id = existing_source.data[0]["source_id"]
                        existing_content = (
                            supabase.table("content_sources")
                            .select("*")
                            .eq("source_id", source_id)
                            .execute()
                        )

                        if existing_content.data:
                            raise ValueError("Content already exists for this URL")

                        # Use existing source if no content exists
                        url_meta = get_url_metadata(payload["url"])
                        media_meta = get_media_links(payload["url"])
                        return source_id, url_meta, media_meta

                    # Create new source if it doesn't exist
                    source_type = (
                        supabase.table("source_types")
                        .select("*")
                        .eq("name", "web_url")
                        .execute()
                    )
                    url_meta = get_url_metadata(payload["url"])
                    media_meta = get_media_links(payload["url"])

                    source_data = {
                        "source_type_id": source_type.data[0]["source_type_id"],
                        "source_identifier": payload["url"],
                        "batch_id": thread_id,
                    }
                    source = supabase.table("sources").insert(source_data).execute()
                    source_id = source.data[0]["source_id"]

                    # Insert URL reference
                    url_ref_data = {
                        "source_id": source_id,
                        "url": url_meta["original_url"],
                        "type": url_meta["type"],
                        "domain": url_meta["domain"],
                        "content_type": url_meta["content_type"],
                        "file_category": url_meta["file_category"],
                    }
                    supabase.table("url_references").insert(url_ref_data).execute()

                    # Insert media if available
                    if media_meta:
                        for media in media_meta:
                            media_data = {
                                "source_id": source_id,
                                "media_url": media["original_url"],
                                "media_type": media["type"],
                            }
                            supabase.table("media").insert(media_data).execute()

                    return source_id, url_meta, media_meta

                elif payload.get("tweet_id"):
                    # Check if source already exists for this tweet
                    existing_source = (
                        supabase.table("sources")
                        .select("*")
                        .eq("source_identifier", payload["tweet_id"])
                        .execute()
                    )

                    if existing_source.data:
                        # Check if content exists for this source
                        source_id = existing_source.data[0]["source_id"]
                        existing_content = (
                            supabase.table("content_sources")
                            .select("*")
                            .eq("source_id", source_id)
                            .execute()
                        )

                        if existing_content.data:
                            raise ValueError("Content already exists for this tweet")

                        # Use existing source if no content exists
                        tweet_data = self.fetch_urls_and_media(payload["tweet_id"])
                        # Handle cases where tweet may not have urls or media
                        url_data = tweet_data.get("urls", [])
                        media_data = tweet_data.get("media", [])

                        return source_id, url_data, media_data

                    # Create new source if it doesn't exist
                    source_type = (
                        supabase.table("source_types")
                        .select("*")
                        .eq("name", "twitter")
                        .execute()
                    )
                    tweet_data = self.fetch_urls_and_media(payload["tweet_id"])

                    source_data = {
                        "source_type_id": source_type.data[0]["source_type_id"],
                        "source_identifier": payload["tweet_id"],
                        "batch_id": thread_id,
                    }
                    source = supabase.table("sources").insert(source_data).execute()
                    source_id = source.data[0]["source_id"]

                    # Insert URL references
                    if tweet_data.get("urls"):
                        for url in tweet_data["urls"]:
                            url_ref_data = {
                                "source_id": source_id,
                                "url": url["original_url"],
                                "type": url["type"],
                                "domain": url["domain"],
                                "content_type": url.get("content_type"),
                                "file_category": url.get("file_category"),
                            }
                            supabase.table("url_references").insert(
                                url_ref_data
                            ).execute()

                    # Insert media
                    if tweet_data.get("media"):
                        for media in tweet_data["media"]:
                            media_data = {
                                "source_id": source_id,
                                "media_url": media["original_url"],
                                "media_type": media["type"],
                            }
                            supabase.table("media").insert(media_data).execute()

                    return (
                        source_id,
                        tweet_data.get("urls", []),
                        tweet_data.get("media", []),
                    )

                return None, None, None

            # 2. Content Processing and State Management
            test_input = None
            source_id = None
            url_meta = None
            media_meta = None

            # Case 1: Thread exists but no feedback (Social post generation)
            if payload.get("thread_id") and not payload.get("feedback"):
                # Fetch existing content
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
                    values={
                        "post_types": payload.get("post_types", ["twitter", "linkedin"])
                    },
                )
                result = self.graph.invoke(None, config=config, debug=True)

                # Update existing content in the database
                for post_type in payload.get("post_types", ["twitter", "linkedin"]):
                    content_type = (
                        supabase.table("content_types")
                        .select("*")
                        .eq("name", post_type)
                        .execute()
                    )
                    # Check if content exists for this type
                    existing_content = (
                        supabase.table("content")
                        .select("*")
                        .eq("thread_id", thread_id)
                        .eq("content_type_id", content_type.data[0]["content_type_id"])
                        .execute()
                    )

                    if not existing_content.data:
                        # Insert new content record for this type
                        content_body = result.get(
                            "final_blog" if post_type == "blog" else f"{post_type}_post"
                        )
                        if content_body:
                            content_data = {
                                "content_type_id": content_type.data[0][
                                    "content_type_id"
                                ],
                                "body": content_body,
                                "status": "Draft",
                                "thread_id": thread_id,
                            }
                            supabase.table("content").insert(content_data).execute()
            # Case 2: Feedback handling
            elif payload.get("feedback") and payload.get("thread_id"):
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

                # Update existing content in the database
                for post_type in payload.get(
                    "post_types", ["blog", "twitter", "linkedin"]
                ):
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

            # Case 3: New content generation
            else:
                source_id, url_meta, media_meta = setup_initial_records(payload)

                if payload.get("url"):
                    content = self._process_url_content(url_meta)
                    media_markdown = get_media_content_url(media_meta)
                    test_input = BlogStateInput(
                        input_url=payload["url"],
                        input_content=content,
                        post_types=payload.get("post_types", ["blog"]),
                        thread_id=thread_id,
                        media_markdown=media_markdown,
                    )
                elif payload.get("tweet_id"):
                    # tweet = self.fetch_urls_and_media(payload["tweet_id"])
                    reference_content, reference_link = get_tweet_reference_content(
                        url_meta
                    )
                    media_markdown = get_tweet_media(media_meta)
                    test_input = BlogStateInput(
                        input_url=reference_link,
                        input_content=reference_content,
                        media_markdown=media_markdown,
                        post_types=payload.get("post_types", ["blog"]),
                        thread_id=thread_id,
                    )

                if not test_input:
                    raise ValueError(
                        "Invalid payload - must contain url, tweet_id or feedback"
                    )

                config = {"configurable": {"thread_id": thread_id}}
                result = self.graph.invoke(test_input, config=config)

                # 3. Store Generated Content
                def store_content(result, thread_id, source_id):
                    # Get content type ID
                    for post_type in payload.get("post_types", ["blog"]):
                        content_type = (
                            supabase.table("content_types")
                            .select("*")
                            .eq("name", post_type)
                            .execute()
                        )

                        content_data = {
                            "content_type_id": content_type.data[0]["content_type_id"],
                            "title": (
                                result.get("blog_title")
                                if post_type == "blog"
                                else None
                            ),
                            "body": result.get(
                                "final_blog"
                                if post_type == "blog"
                                else f"{post_type}_post"
                            ),
                            "status": "Draft",
                            "thread_id": thread_id,
                        }

                        if payload.get("profile_id"):
                            content_data["profile_id"] = payload["profile_id"]

                        content = (
                            supabase.table("content").insert(content_data).execute()
                        )
                        content_id = content.data[0]["content_id"]

                        # Link content to source
                        if source_id:
                            content_source_data = {
                                "content_id": content_id,
                                "source_id": source_id,
                            }
                            supabase.table("content_sources").insert(
                                content_source_data
                            ).execute()

                        # Store tags if available
                        if result.get("tags"):
                            for tag_name in result["tags"]:
                                # Create or get tag
                                tag = (
                                    supabase.table("tags")
                                    .select("*")
                                    .eq("name", tag_name)
                                    .execute()
                                )
                                if not tag.data:
                                    tag = (
                                        supabase.table("tags")
                                        .insert({"name": tag_name})
                                        .execute()
                                    )
                                tag_id = tag.data[0]["tag_id"]

                                # Link content to tag
                                content_tag_data = {
                                    "content_id": content_id,
                                    "tag_id": tag_id,
                                }
                                supabase.table("content_tags").insert(
                                    content_tag_data
                                ).execute()

                store_content(result, thread_id, source_id)

            return BlogStateOutput(**result)

        except Exception as e:
            logger.error(f"Error in workflow: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def _process_url_content(self, url_meta):
        """Helper to process URL content based on type"""
        # url_meta = utils.get_url_metadata(url)

        if url_meta["type"] == "html":
            return self.extractor.extract_html(html_content=url_meta["content"])
        elif url_meta["type"] == "pdf":
            return self.extractor.extract_pdf(input_file=url_meta["original_url"])
        elif url_meta["type"] == "arxiv":
            return self.extractor.extract_arxiv_pdf(url_meta["original_url"])
        elif url_meta["type"] == "github":
            return self.extractor.extract_github_readme(url_meta["original_url"])
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
        self.builder.add_node("generate_tags", self.generate_tags)
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
        self.builder.add_edge("compile_final_blog", "generate_tags")

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
            "generate_tags",
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
                "generate_tags",
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
