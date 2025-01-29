from src.backend.extraction.base import BaseExtractor
from typing import Dict, Any, List
import praw
import os
from src.backend.clients.llm import LLMClient, HumanMessage

class RedditExtractor(BaseExtractor):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"extractors.reddit.{config_name}")
        self.reddit = praw.Reddit(
            client_id=os.environ.get('REDDIT_CLIENT_ID'),
            client_secret=os.environ.get('REDDIT_CLIENT_SECRET'),
            user_agent=os.environ.get('REDDIT_USER_AGENT')
        )
        self.llm = LLMClient()

    def _setup_extractor(self):
        # Initialize text extraction specific setup using self.config.class_params
        pass

    def extract(self, source: str, **method_params) -> Dict[str, Any]:
        params = self.merge_method_params(method_params)
        submission = self.reddit.submission(url=source)
        
        # Extract full content
        content = self._extract_submission(submission)
        
        # Create summary prompt
        summary_prompt = f"""
        Summarize the following Reddit post and its top comments into a detailed, well-structured summary:

        **Post Title:** {content['title']}
        **Post Content:** {content['selftext']}
        
        **Top Comments:** 
        {self._format_comments(content['comments'][:10])}
        
        The summary should be structured as follows:
        1. **Main Points from the Post:** Clearly outline the key ideas, questions, or arguments presented in the post. Include any relevant context or examples provided by the author.
        2. **Insights from Top Comments:** Highlight the most significant points, counterpoints, or additional information shared by commenters. Include diverse perspectives and notable replies.
        3. **Themes of the Discussion:** Provide an overview of recurring themes, debates, or consensus points that emerge from the discussion.
        4. **Tone and Sentiment:** Briefly describe the tone of the discussion (e.g., supportive, critical, humorous, contentious).
        5. **Actionable Takeaways (if any):** Summarize practical suggestions, advice, or conclusions drawn from the conversation.
        
        Ensure the summary is clear, concise, and captures the essence of the post and the discussion. Avoid unnecessary details but include enough depth for a comprehensive understanding.
        """

        if method_params.get("skip_llm", False):
            return {
                "type": "reddit",
                "content": content['selftext'],
                "title": content['title'],
                "author": content['author'],
                "subreddit": submission.subreddit.display_name,
                "score": content['score'],
                "top_comments": content['comments'][:10],
                "summary": "Summary generation skipped."
            }
        
        # Generate summary using LLM
        summary = self.llm.invoke([HumanMessage(content=summary_prompt)])

        return {
            "type": "reddit",
            "content": content['selftext'],
            "title": content['title'],
            "author": content['author'],
            "subreddit": submission.subreddit.display_name,
            "score": content['score'],
            "top_comments": content['comments'][:10],
            "summary": summary
        }

    def _extract_submission(self, submission) -> Dict[str, Any]:
        return {
            "title": submission.title,
            "author": submission.author.name if submission.author else "[deleted]",
            "created_utc": submission.created_utc,
            "num_comments": submission.num_comments,
            "score": submission.score,
            "upvote_ratio": submission.upvote_ratio,
            "selftext": submission.selftext,
            "comments": self._extract_comments(submission.comments)
        }

    def _extract_comments(self, comments, max_depth: int = 5, depth: int = 0) -> List[Dict[str, Any]]:
        if depth >= max_depth:
            return []
            
        extracted_comments = []
        comments.replace_more(limit=3)  # Load additional comments
        
        for comment in comments[:10]:  # Get top 5 comments
            try:
                if not comment.author:
                    continue
                    
                comment_data = {
                    "author": comment.author.name,
                    "score": comment.score,
                    "body": comment.body,
                    "replies": self._extract_comments(comment.replies, max_depth, depth + 1)
                }
                extracted_comments.append(comment_data)
            except Exception:
                continue
                
        return extracted_comments

    def _format_comments(self, comments: List[Dict]) -> str:
        formatted = []
        for comment in comments:
            formatted.append(f"Comment by {comment['author']} (Score: {comment['score']}): {comment['body']}")
        return "\n\n".join(formatted)

    def create_summary(self, reddit_data:List[dict]) -> str:
        
        #loop through the reddit data and create a summary with schema :,content: str, title: str, comments: List[str]
        
        pre_summary_prompt = self._create_pre_summary(reddit_data)
        
        summary_prompt = f"""
        Summarize the following Reddit posts and its top comments into a detailed, well-structured summary:

        {pre_summary_prompt}
        
        The summary should be structured as follows:
        1. **Main Points from different Posts:** Clearly outline the key ideas, questions, or arguments presented in the various post. Include any relevant context or examples provided by the authors.
        2. **Insights from Top Comments:** Highlight the most significant points from each post, counterpoints, or additional information shared by commenters. Include diverse perspectives and notable replies.
        3. **Themes of the Discussion:** Provide an overview of recurring themes, debates, or consensus points that emerge from various discussions.
        4. **Actionable Takeaways (if any):** Summarize practical suggestions, advice, or conclusions drawn from the various conversations.
        
        Ensure the summary is clear, concise, and captures the essence of the post and the discussion. Include enough depth for a comprehensive understanding.
        """

        summary = self.llm.invoke([HumanMessage(content=summary_prompt)])

        return summary

    def _create_pre_summary(self, reddit_data):
        pre_summary_prompt=""
        for data in reddit_data:
            content = data['content']
            title = data['title']
            comments = data['top_comments']
            pre_summary_prompt += f"""
                **Post Title:** {title}
                **Post Content:** {content}
                **Top Comments:** 
                {self._format_comments(comments)}
                -----------------------------------------
            """
            
        return pre_summary_prompt