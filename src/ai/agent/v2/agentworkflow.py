import os
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from fastapi import HTTPException, Depends
import uuid
from datetime import datetime
import re
from db.sql import get_tweet_by_id, BlogStyleTypes, get_db
from langgraph.checkpoint.postgres import PostgresSaver

# from langgraph.checkpoint import
# from sqlalchemy import create_engine
# from sqlalchemy.orm import Session
# from db.sql import get_connection_pool
load_dotenv()
from ai.service import (
    get_gemini,
    get_ollama_model,
    get_openai_compatible_model,
    get_openrouter_model,
)
import ast
import pypandoc
import markdownify
import json

from psycopg import Connection

# Create a global checkpointer instance
DB_URI = "postgresql://postbot:postbot12345@localhost/post_bot?sslmode=disable"
connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}
conn = Connection.connect(DB_URI, **connection_kwargs)
checkpointer = PostgresSaver(conn)


class AgentState(TypedDict):
    """Extended state to include thread messages and human intervention flags"""

    tweet: Dict
    # tweet_type: list[str] | None
    tags: list
    blog_style: str
    blog_title:str
    blog_content: str
    status: str
    publication_schedule: Dict[str, Any]
    messages: list[BaseMessage]  # Thread messages
    # approval_to_generate: bool
    approval_to_publish: bool
    agent_id: str


class BlogWorkflow:
    def __init__(self):
        self.llm = get_gemini()

        # Define workflow graph
        self.workflow = StateGraph(AgentState)

        # Use the global checkpointer
        self.checkpointer = checkpointer
        checkpointer.setup()
        self.graph = self.setup_workflow(self.checkpointer)

        # Store active workflows
        self.active_workflows = {}

    def read_prompt(self, prompt_file, **kwargs):

        file_path = os.path.join("src/ai/prompts", prompt_file)
        with open(file_path, "r") as f:
            prompt = f.read()

        prompt = prompt.format(**kwargs)

        return prompt

    def run_workflow(self, payload, agent_id: str) -> Dict[str, Any]:
        """Synchronous workflow execution"""
        # get old checkpoint if exists
        config = {"configurable": {"thread_id": agent_id}}

        checkpoint = checkpointer.get(config)

        # get tweet data using tweet_id
        tweet = get_tweet_by_id(payload["tweet_id"])

        if checkpoint is None:
            state = AgentState(
                tweet=tweet,
                status="WorkflowInitialized",
                agent_id=agent_id,
                messages=[],
                blog_style=payload["blog_style"],
            )
            result = self.graph.invoke(state, config)
        else:
            # read style_mapping.json
            # {'approval_to_generate':payload["feedback"]['approval_to_generate'],
            self.graph.update_state(
                config, values={"blog_style": payload["blog_style"]}
            )
            result = self.graph.invoke(None, config)

        return result

    def tweet_classifier(self, state: AgentState) -> Dict:
        """Classify the tweet and reference content to check if it is elgible for blog generation"""

        if state["tweet"]["urls"]:
            state["status"] = "ReadyForBlogGeneration"
        else:
            state["status"] = "NoBlogGenerationRequired"

        # state["status"] = "TweetClassified"

        return state

    def blog_ask_from_human(self, state: AgentState) -> Dict:
        """Ask user if they want to create a blog post"""

        # if state["approval_to_generate"]:
        state["status"] = "StyleSelection"  # Update the status for blog generation
        # else:
        #     state["status"] = "EndWorkflow"  # Set status to await further feedback

        return state

    def style_selection(self, state: AgentState) -> Dict:
        """Ask user to select a blog style"""
        # styles = ["Academic", "Conversational", "Technical", "Narrative", "Professional"]
        # config = {"configurable": {"thread_id": state['agent_id']}}
        # state["blog_style"]=sstate["blog_style"]#.graph.update_state(config,values={'blog_style':'Academic'})
        # state['blog_style']="Academic"
        state["status"] = "StyleSelection"

        return state

    def blog_generator(self, state: AgentState) -> Dict:
        """Enhanced blog generator with media and reference handling"""
        reference_content = ""
        reference_link = ""
        github_readme = ""

        # Process URLs
        for url in state["tweet"]["urls"]:
            if url["file_category"] in ["document", "repo", "webpage"]:
                # Read markdown/PDF content
                with open(url["downloaded_path_md"], "r") as f:
                    reference_content = f.read()
                reference_link = url["original_url"]
            else:
                pass                
        media_markdown = ""
        if state["tweet"].get("media"):
            for media in state["tweet"]["media"]:
                if media["type"] == "photo":
                    media_markdown += (
                        f"<img src={media['final_url']}/>\n\n"
                    )
                if media["type"] == "video":
                    media_markdown += (
                        f"<video src={media['final_url']} controls />\n\n"
                    )

        blog_style = get_blog_style(
            state["blog_style"]
        )  # Use the new function to get the blog style

        # with open(os.path.join("src/ai/agent/styles",selected_style)) as f:
        #     style_prompt=f.read()
        # style_prompt=
        # Update prompt to include GitHub README and media
        prompt = self.read_prompt(
            "blog_generator1.txt",
            style_prompt=blog_style[0].style_prompt,
            # types=", ".join(state["tweet_type"]),
            tweet=state["tweet"]["full_text"],
            article=reference_content,
            media=media_markdown,
            references=reference_link,
        )
        if reference_content != "":
            state["messages"].append(HumanMessage(content=prompt))
            result = self.llm.invoke(state["messages"])
            state["messages"].append(result)

            blog_content = re.findall(r"<blog>(.*?)</blog>", result.content, re.DOTALL)[
                0
            ]
            blog_content = blog_content.replace("\\n", "\n")
            blog_title=re.findall(r"^#\s+(.*)",blog_content,re.DOTALL)[0]
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
            state["tags"] = tags
            state["blog_content"] = blog_content
            state["blog_title"]=blog_title
            state["status"] = "BlogGenerated"
        else:
            state["tags"] = []
            state["blog_content"] = ""
            state["blog_title"]=""
            state["status"] = "NoBlogGenerated"

        return state

    # def get_style_prompt(style):
    #     return BlogStyles.read(get_db(),style=style)

    def end_workflow(self, state: AgentState) -> Dict:
        """End the workflow"""
        state["messages"].append(
            HumanMessage(content="The workflow has ended. Thank you!")
        )
        return state

    def setup_workflow(self, checkpointer):
        """Setup the workflow with nodes and edges"""
        self.workflow.add_node("tweet_classifier", self.tweet_classifier)
        # self.workflow.add_node("blog_ask_from_human", self.blog_ask_from_human)
        self.workflow.add_node("style_selection", self.style_selection)
        self.workflow.add_node("blog_generator", self.blog_generator)
        self.workflow.add_node("end_workflow", self.end_workflow)

        self.workflow.add_edge("__start__", "tweet_classifier")
        # self.workflow.add_edge("tweet_classifier", "style_selection")
        self.workflow.add_conditional_edges(
            "tweet_classifier",
            lambda x: (
                "style_selection" if x["status"] == "ReadyForBlogGeneration" else END
            ),
        )
        self.workflow.add_edge("style_selection", "blog_generator")
        self.workflow.add_edge("blog_generator", END)

        # graph = self.workflow.compile(checkpointer=checkpointer,interrupt_after=["tweet_classifier"])
        graph = self.workflow.compile(checkpointer=checkpointer)
        return graph


def get_blog_style(style_name):
    """
    Retrieve a blog style by its name.

    :param style_name: The name of the blog style to retrieve.
    :return: The blog style object or a default style if not found.
    """
    db_gen = get_db()  # Get the database session generator
    session = next(db_gen)  # Extract a session from the generator

    try:
        # Attempt to retrieve the blog style
        blog_style = BlogStyleTypes.read(session, style=style_name)
        if not blog_style:
            # Handle the case where no style is found
            print(f"No blog style found for '{style_name}'. Returning default style.")
            return BlogStyleTypes.read(session, style="Academic")  # Return a default style
        return blog_style
    except Exception as e:
        raise e  # Reraise any exceptions for further handling
    finally:
        db_gen.close()  # Ensure the generator is closed


def get_workflow() -> BlogWorkflow:
    """Dependency to get a BlogWorkflow instance."""
    return BlogWorkflow()


def main():
    """
    Example usage of the blog workflow
    """
    # Sample tweet data
    sample_tweet = {
        "text": "Exciting new breakthrough in AI language models...",
        "author": "@AIResearcher",
        "url": "https://twitter.com/example/status/123456",
    }

    workflow = BlogWorkflow()
    result = workflow.run_workflow(sample_tweet)
    print(result)


if __name__ == "__main__":
    main()
