import os
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# Agent State
class AgentState(BaseModel):
    tweet: str = ""
    tweet_category: str = ""
    selected_style: str = ""
    draft_blog: str = ""
    status: str = "pending"
    human_feedback: str = ""

# LangGraph Agent Implementation
class TweetToBlogAgent:
    def __init__(self):

        self.model = ChatOpenAI(
            model="llama-3.3-70b-versatile", 
            temperature=0.5,
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1/"
        )
        
    def classify_tweet(self, state: AgentState) -> AgentState:
        """Classify the tweet category"""
        response = self.model.invoke([
            HumanMessage(content=f"Classify the following tweet into one of these categories: News, Technology, Personal, Entertainment, Sports, Politics\n\nTweet: {state.tweet}")
        ])
        state.tweet_category = response.content
        return state
    
    def request_style_selection(self, state: AgentState) -> AgentState:
        """Prepare for human style selection"""
        state.status = "style_selection_required"
        return state
    
    def generate_blog(self, state: AgentState) -> AgentState:
        """Generate blog draft based on tweet and selected style"""
        style_prompt = f"Write a blog post in {state.selected_style} style about the following tweet: {state.tweet}"
        response = self.model.invoke([
            HumanMessage(content=style_prompt)
        ])
        state.draft_blog = response.content
        state.status = "draft_generated"
        return state
    
    def request_human_review(self, state: AgentState) -> AgentState:
        """Prepare draft for human review"""
        state.status = "review_required"
        return state
    
    def publish_blog(self, state: AgentState) -> AgentState:
        """Publish blog after human approval"""
        if state.human_feedback.lower() == "approve":
            # In a real scenario, you'd integrate with a blog publishing platform
            print(f"Blog Published: {state.draft_blog}")
            state.status = "published"
        else:
            state.status = "rejected"
        return state

    def build_graph(self):
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("classify_tweet", self.classify_tweet)
        workflow.add_node("request_style_selection", self.request_style_selection)
        workflow.add_node("generate_blog", self.generate_blog)
        workflow.add_node("request_human_review", self.request_human_review)
        workflow.add_node("publish_blog", self.publish_blog)
        
        # Add edges
        workflow.add_edge("classify_tweet", "request_style_selection")
        workflow.add_edge("request_style_selection", "generate_blog")
        workflow.add_edge("generate_blog", "request_human_review")
        workflow.add_edge("request_human_review", "publish_blog")
        
        workflow.set_entry_point("classify_tweet")
        workflow.add_conditional_edges(
            "publish_blog",
            lambda state: state.status,
            {
                "published": END,
                "rejected": "request_human_review"
            }
        )
        
        return workflow.compile()

# FastAPI WebSocket Server
class WebSocketServer:
    def __init__(self):
        self.app = FastAPI()
        self.agent = TweetToBlogAgent()
        self.graph = self.agent.build_graph()
        
        @self.app.websocket("/process")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            try:
                while True:
                    # Receive initial tweet
                    data = await websocket.receive_json()
                    
                    # Initialize agent state
                    state = AgentState(tweet=data['tweet'])
                    
                    # Run through graph
                    current_state = state
                    # config = {"recursion_limit": 50}  # Optional configuration
                    for state in self.graph.stream(current_state):
                        current_state = AgentState(**state)
                        # current_state = node['state']
                        
                        # Send status updates via WebSocket
                        await websocket.send_json({
                            "status": current_state.status,
                            "tweet_category": current_state.tweet_category,
                            "draft_blog": current_state.draft_blog
                        })
                        
                        # Handle human interaction points
                        if current_state.status == "style_selection_required":
                            await websocket.send_json({
                                "status": "awaiting_style_selection",
                                "tweet_category": current_state.tweet_category
                            })
                            # Wait for human style selection
                            style_data = await websocket.receive_json()
                            current_state.selected_style = style_data['selected_style']
                        
                        if current_state.status == "review_required":
                            await websocket.send_json({
                                "status": "awaiting_review",
                                "draft_blog": current_state.draft_blog
                            })
                            # Wait for human review
                            review_data = await websocket.receive_json()
                            current_state.human_feedback = review_data['feedback']
                    
                    # Final publication status
                    await websocket.send_json({
                        "status": current_state.status,
                        "message": "Blog process completed"
                    })
                    
            except WebSocketDisconnect:
                print("WebSocket connection closed")

    def run(self, host="localhost", port=8000):
        uvicorn.run(self.app, host=host, port=port)


if __name__ == "__main__":
    server = WebSocketServer()
    server.run()