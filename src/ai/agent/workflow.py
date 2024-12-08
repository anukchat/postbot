import os
from typing import Dict, Any, TypedDict
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import uuid
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    """
    Represents the state of the blog generation workflow
    """
    tweet: Dict[str, Any]
    tweet_type: str
    tags: list
    blog_style: str
    blog_content: str
    references: Dict[str, Any]
    status: str
    publication_schedule: Dict[str, Any]

class BlogWorkflow:
    def __init__(self, openai_api_key=os.environ["GROQ_API_KEY"]):
        """
        Initialize the blog generation workflow
        
        Args:
            openai_api_key (str, optional): OpenAI API key
        """
        self.llm = ChatOpenAI(
            model="llama-3.3-70b-versatile", 
            temperature=0.5, 
            api_key=openai_api_key,
            base_url="https://api.groq.com/openai/v1/"
        )
        
        # Define workflow graph
        self.workflow = StateGraph(AgentState)
        self.setup_workflow()
    
    def tweet_classifier(self, state: AgentState) -> Dict:
        """
        Classify tweet type and generate tags
        
        Args:
            state (AgentState): Current workflow state
        
        Returns:
            Dict: Updated state with tweet type and tags
        """
        classify_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Classify the tweet type and generate relevant tags.
            
            Classification Options:
            - Technical
            - Research
            - NonTechnical
            - AI
            - NonAI
            
            Provide:
            1. Tweet Type
            2. Relevant Tags (max 5)
            """),
            ("human", "{tweet}")
        ])
        
        chain = classify_prompt | self.llm
        result = chain.invoke({"tweet": state['tweet']})
        
        # Parse result
        tweet_type = result.content.split('\n')[0].strip()
        tags = result.content.split('\n')[1:] if len(result.content.split('\n')) > 1 else []
        
        return {
            "tweet_type": tweet_type,
            "tags": tags
        }
    
    def blog_recommendation(self, state: AgentState) -> Dict:
        """
        Recommend whether to create a blog post
        
        Args:
            state (AgentState): Current workflow state
        
        Returns:
            Dict: Updated state with blog creation recommendation
        """
        recommend_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Analyze the tweet and determine if it warrants a blog post.
            
            Considerations:
            - Novelty of content
            - Potential reader interest
            - Depth of information
            
            Provide:
            1. Recommendation (Yes/No)
            2. Reasoning
            3. Suggested Blog Style
            """),
            ("human", "{tweet_type} tweet with tags: {tags}")
        ])
        
        chain = recommend_prompt | self.llm
        result = chain.invoke({
            "tweet_type": state['tweet_type'], 
            "tags": state['tags']
        })
        
        # Parse result
        recommendation = result.content.split('\n')[0].strip()
        blog_style = result.content.split('\n')[2].strip() if len(result.content.split('\n')) > 2 else 'technical'
        
        return {
            "blog_style": blog_style,
            "status": 'SystemBlogStarted' if recommendation.lower() == 'yes' else 'BlogCreationDiscarded'
        }
    
    def blog_generator(self, state: AgentState) -> Dict:
        """
        Generate blog content
        
        Args:
            state (AgentState): Current workflow state
        
        Returns:
            Dict: Updated state with blog content
        """
        generate_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Generate a comprehensive blog post based on:
            - Tweet Type: {tweet_type}
            - Tags: {tags}
            - Style: {blog_style}
            
            Include:
            - Engaging introduction
            - Detailed content
            - References
            - Conclusion
            """),
            ("human", "{tweet}")
        ])
        
        chain = generate_prompt | self.llm
        result = chain.invoke({
            "tweet": state['tweet'],
            "tweet_type": state['tweet_type'],
            "tags": state['tags'],
            "blog_style": state['blog_style']
        })
        
        return {
            "blog_content": result.content,
            "status": 'SystemBlogsGenerated'
        }
    
    def human_review(self, state: AgentState) -> Dict:
        """
        Trigger human review process
        
        Args:
            state (AgentState): Current workflow state
        
        Returns:
            Dict: Updated state after human review
        """
        # In a real implementation, this would trigger a human review interface
        return {
            "status": 'HumanBlogsEdited'
        }
    
    def scheduling(self, state: AgentState) -> Dict:
        """
        Schedule blog post
        
        Args:
            state (AgentState): Current workflow state
        
        Returns:
            Dict: Updated state with scheduling information
        """
        schedule_prompt = ChatPromptTemplate.from_messages([
            ("system", """
            Recommend optimal publishing schedule based on:
            - Content type
            - Tags
            - Current trends
            
            Provide:
            1. Recommended date
            2. Best time of day
            3. Potential platforms
            """),
            ("human", "{tweet_type} blog with tags: {tags}")
        ])
        
        chain = schedule_prompt | self.llm
        result = chain.invoke({
            "tweet_type": state['tweet_type'], 
            "tags": state['tags']
        })
        
        # Generate unique blog post ID
        blog_id = str(uuid.uuid4())
        
        return {
            "publication_schedule": {
                "blog_id": blog_id,
                "recommended_date": result.content.split('\n')[0].strip(),
                "best_time": result.content.split('\n')[1].strip(),
                "platforms": result.content.split('\n')[2].strip().split(',')
            },
            "status": 'HumanBlogsScheduled'
        }
    
    def setup_workflow(self):
        """
        Set up the workflow graph
        """
        self.workflow.add_node("tweet_classifier", self.tweet_classifier)
        self.workflow.add_node("blog_recommendation", self.blog_recommendation)
        self.workflow.add_node("blog_generator", self.blog_generator)
        self.workflow.add_node("human_review", self.human_review)
        self.workflow.add_node("scheduling", self.scheduling)
        
        # Add START to first node
        self.workflow.add_edge("__start__", "tweet_classifier")
        
        # Define workflow edges
        self.workflow.add_edge("tweet_classifier", "blog_recommendation")
        self.workflow.add_edge("blog_recommendation", "blog_generator")
        self.workflow.add_edge("blog_generator", "human_review")
        self.workflow.add_edge("human_review", "scheduling")
        self.workflow.add_edge("scheduling", END)
        
        # Compile the workflow
        self.compiled_workflow = self.workflow.compile()
    
    def run_workflow(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete blog generation workflow
        
        Args:
            tweet (Dict): Tweet data to process
        
        Returns:
            Dict: Final workflow state
        """
        initial_state = {"tweet": tweet}
        result = self.compiled_workflow.invoke(initial_state)
        return result

def main():
    """
    Example usage of the blog workflow
    """
    # Sample tweet data
    sample_tweet = {
        "text": "Exciting new breakthrough in AI language models...",
        "author": "@AIResearcher",
        "url": "https://twitter.com/example/status/123456"
    }
    
    workflow = BlogWorkflow()
    result = workflow.run_workflow(sample_tweet)
    print(result)

if __name__ == "__main__":
    main() 