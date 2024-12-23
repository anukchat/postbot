import os
import uuid
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from langgraph.graph import StateGraph, END

class Tweet(BaseModel):
    id: str
    text: str
    author: str

class WorkflowState(BaseModel):
    tweet: Tweet
    tweet_types: Optional[List[str]] = None
    blog_style: Optional[str] = None
    blog_content: Optional[str] = None
    status: str = "initialized"
    agent_id: str = str(uuid.uuid4())
    user_confirmation: Optional[bool] = None
    selected_style: Optional[str] = None

class BlogWorkflowManager:
    def __init__(self):
        self.active_workflows: Dict[str, WorkflowState] = {}
        
        # Initialize workflow graph
        self.workflow_graph = StateGraph(WorkflowState)
        self.setup_workflow()
    
    def setup_workflow(self):
        # Define workflow nodes
        self.workflow_graph.add_node("classify_tweet", self.classify_tweet)
        self.workflow_graph.add_node("confirm_blog_generation", self.confirm_blog_generation)
        self.workflow_graph.add_node("select_blog_style", self.select_blog_style)
        self.workflow_graph.add_node("generate_blog", self.generate_blog)
        
        # Define workflow edges
        self.workflow_graph.set_entry_point("classify_tweet")
        
        # Conditional routing
        self.workflow_graph.add_conditional_edges(
            "classify_tweet",
            lambda state: "confirm_blog_generation" if state.tweet_types else END
        )
        
        self.workflow_graph.add_conditional_edges(
            "confirm_blog_generation",
            lambda state: "select_blog_style" if state.user_confirmation else END
        )
        
        self.workflow_graph.add_edge("select_blog_style", "generate_blog")
        self.workflow_graph.add_edge("generate_blog", END)
        
        # Compile workflow
        self.compiled_workflow = self.workflow_graph.compile()
    
    def classify_tweet(self, state: WorkflowState) -> WorkflowState:
        # Tweet classification logic (could use LLM or predefined rules)
        state.tweet_types = ["Technology", "AI"]
        state.status = "classified"
        return state
    
    def confirm_blog_generation(self, state: WorkflowState) -> WorkflowState:
        # This method will be triggered after user confirmation
        # The actual confirmation happens via a separate API endpoint
        state.status = "awaiting_confirmation"
        return state
    
    def select_blog_style(self, state: WorkflowState) -> WorkflowState:
        # This method will be triggered after user selects style
        # The actual style selection happens via a separate API endpoint
        state.status = "style_selection"
        return state
    
    def generate_blog(self, state: WorkflowState) -> WorkflowState:
        # Simulate blog generation
        state.blog_content = f"Blog about {state.tweet.text} in {state.selected_style} style"
        state.status = "blog_generated"
        return state
    
    def get_workflow_state(self, agent_id: str) -> WorkflowState:
        return self.active_workflows.get(agent_id)
    
    async def run_workflow(self, tweet: Tweet):
        # Create initial state
        initial_state = WorkflowState(tweet=tweet)
        
        # Store the workflow state
        self.active_workflows[initial_state.agent_id] = initial_state
        
        # Run the workflow
        result = await self.compiled_workflow.ainvoke(initial_state)
        
        return result

# FastAPI Application
app = FastAPI()

# Global workflow manager
workflow_manager = BlogWorkflowManager()

@app.post("/start_workflow")
async def start_workflow(tweet: Tweet):
    """Initiate the blog generation workflow"""
    try:
        result = await workflow_manager.run_workflow(tweet)
        return {
            "status": "workflow_started",
            "agent_id": result.agent_id,
            "tweet_types": result.tweet_types
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/confirm_blog_generation/{agent_id}")
async def confirm_blog_generation(agent_id: str, confirm: bool):
    """User confirms whether to generate a blog"""
    # Retrieve the workflow state
    state = workflow_manager.get_workflow_state(agent_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update the state with user confirmation
    state.user_confirmation = confirm
    
    if confirm:
        # Continue workflow
        result = await workflow_manager.compiled_workflow.ainvoke(state)
        return {
            "status": "confirmed",
            "next_step": "select_style"
        }
    else:
        return {
            "status": "cancelled",
            "message": "Blog generation cancelled by user"
        }

@app.post("/select_blog_style/{agent_id}")
async def select_blog_style(agent_id: str, style: str):
    """User selects blog generation style"""
    # Retrieve the workflow state
    state = workflow_manager.get_workflow_state(agent_id)
    
    if not state:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Validate style
    valid_styles = ["Academic", "Conversational", "Technical", "Narrative", "Professional"]
    if style not in valid_styles:
        raise HTTPException(status_code=400, detail="Invalid style selected")
    
    # Update the state with selected style
    state.selected_style = style
    
    # Continue workflow
    result = await workflow_manager.compiled_workflow.ainvoke(state)
    
    return {
        "status": "style_selected",
        "blog_content": result.blog_content
    }

# Example usage would look like:
# 1. POST /start_workflow  (with tweet data)
# 2. POST /confirm_blog_generation/{agent_id}  (user confirms)
# 3. POST /select_blog_style/{agent_id}  (user selects style)