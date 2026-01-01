import re
import logging
from src.backend.extraction.base import BaseExtractor
from typing import Dict, Any, List
import praw
import os
from src.backend.clients.llm import LLMClient, HumanMessage
from src.backend.utils.general import safe_json_loads
import json

logger = logging.getLogger(__name__)

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

    def get_trending_topics(self, limit: int = 10, subreddits: List[str] = None) -> Dict[str, Any]:
        """
        Fetch trending topics from specified subreddits or r/all
        
        Args:
            limit: Number of trending posts to fetch per subreddit
            subreddits: List of subreddit names to check. If None, checks r/all
        
        Returns:
            Dictionary containing trending topics and their metadata
        """
        trending_data = {}
        
        if subreddits is None:
            # Get trending from r/all
            hot_posts = self.reddit.subreddit('all').hot(limit=limit)
            trending_data['all'] = self._process_trending_posts(hot_posts)
        else:
            # Get trending from specific subreddits
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    hot_posts = subreddit.hot(limit=limit)
                    trending_data[subreddit_name] = self._process_trending_posts(hot_posts)
                except Exception as e:
                    logger.error(f"Error fetching trending from r/{subreddit_name}: {str(e)}")
                    trending_data[subreddit_name] = []
        
        return trending_data

    def _extract_reddit_posts(self,data):
        subreddit_key = list(data.keys())[0]  # Get the dynamic subreddit key
        posts = data[subreddit_key]
        
        output = [
            {
                "title": post["title"],
                "url": post["url"],
                "score": post["score"],
                "num_comments": post["num_comments"],
                "subreddit": post["subreddit"]
            }
            for post in posts
        ]
        
        return output
    
    def suggest_trending_titles(self, reddit_object, limit: int = 10) -> Dict[str, Any]:
        """
        Suggest trending blog po
        
        Args:
            limit: Number of blog posts to suggest
            
        Returns:
            Dictionary containing trending blog posts and their metadata
        """
        try:
            reddit_object=self._extract_reddit_posts(reddit_object)

            content_ideas_prompt = f"""Given a list of top Reddit discussions, generate engaging and insightful content ideas based on the most upvoted and discussed posts. Each idea should extend the original discussion, providing additional value, fresh perspectives, or deep technical insights.

            ### **Input Format**
            The input will be a JSON object containing multiple Reddit posts with the following attributes:
                        
            - **title**: The title of the Reddit post  
            - **url**: Link to the discussion  
            - **score**: Number of upvotes  
            - **num_comments**: Total comments  
            - **subreddit**: Name of the subreddit  

            **Example Input:**
            ```json
            [
                {{
                    "title": "OpenAI is hiding the actual thinking tokens in o3-mini",
                    "url": "https://reddit.com/r/LocalLLaMA/comments/1ikh3vz/",
                    "score": 464,
                    "num_comments": 123,
                    "subreddit": "LocalLLaMA"
                }}
            ]
            ```

            ### **Task**
            For each Reddit post, generate **2-3 engaging content ideas** that:  
            - Go beyond the original discussion and add new insights.  
            - Appeal to a technical audience (developers, AI enthusiasts, researchers).  
            - Cover various formats such as **deep dives, explainer threads, case studies, comparisons, infographics, and video scripts**.  
            - Address different perspectives: technical deep dives, ethical concerns, industry impact, practical applications, and future trends.  
            - Ensure originality and uniqueness.  

            ### **Expected Output Format**  
            Return a JSON object with a `"content_ideas"` list, where each entry corresponds to a suggested content topic that can be researched upon.

            ### **Example Output:**  
            ```json
            {{
                "content_ideas": [
                    "The Mystery of Thinking Tokens: How OpenAI’s o3-mini Processes Information",
                    "Transparency in AI: Should Model Internals Be Fully Visible?",
                    "Are AI Models Becoming Black Boxes? Understanding OpenAI’s o3-mini",
                    "Optimizing Prompt Strategies for Models with Hidden Computation",
                    "The Ethics of AI Transparency: What We Deserve to Know About AI Models"
                ]
            }}
            ```

            ### **Additional Considerations:**  
            - Prioritize posts with high engagement (comments-to-upvotes ratio).  
            - Focus on AI, ML, and technology topics.  
            - Ensure the content ideas are diverse yet relevant to the original discussion.  
            - Make sure to follow the provided schema from example output.  

            🚀 Now, generate **content ideas** based on the given data.  

            {reddit_object}
            """


            posts = self.llm.invoke([HumanMessage(content=content_ideas_prompt)])

            pattern = r"```json\n([\s\S]*?)\n```"
            match = re.search(pattern, posts)

            if match:
                parsed = safe_json_loads(match.group(1))
            else:
                parsed = {"content_ideas": []}
            
            # Return in proper format matching RedditSuggestionsResponse
            return {
                'category': 'blogs',
                'content_ideas': parsed.get('content_ideas', []),
                'trending_blogs': [obj['title'] for obj in reddit_object]
            }
            
        except Exception as e:
            logger.error(f"Error fetching trending blogs: {str(e)}")
            return {
                'category': 'blogs',
                'content_ideas': [],
                'trending_blogs': [obj['title'] for obj in reddit_object],
                'error': str(e)
            }
        
    def get_trending_discussions(self, category: str = 'all', timeframe: str = 'day', limit: int = 10) -> Dict[str, Any]:
        """
        Fetch trending discussion posts based on category and timeframe
        
        Args:
            category: Category to fetch from ('all', 'technology', 'science', etc.)
            timeframe: Time period ('hour', 'day', 'week', 'month', 'year', 'all')
            limit: Number of posts to fetch
            
        Returns:
            Dictionary containing trending discussions
        """
        try:
            subreddit = self.reddit.subreddit(category)
            
            # Get discussion-oriented posts
            if timeframe == 'day':
                posts = subreddit.top('day', limit=limit)
            else:
                posts = getattr(subreddit, timeframe)(limit=limit)
            
            discussions = []
            for post in posts:
                # Filter for discussion-type posts
                if (post.is_self and 
                    post.num_comments > 10 and  # Has meaningful discussion
                    not post.over_18):  # SFW content only
                    
                    discussion_data = {
                        'title': post.title,
                        'url': f"https://reddit.com{post.permalink}",
                        'author': post.author.name if post.author else '[deleted]',
                        'subreddit': post.subreddit.display_name,
                        'score': post.score,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'is_original_content': post.is_original_content,
                        'upvote_ratio': post.upvote_ratio
                    }
                    discussions.append(discussion_data)
            
            return {
                'category': category,
                'timeframe': timeframe,
                'discussions': discussions
            }
            
        except Exception as e:
            logger.error(f"Error fetching trending discussions: {str(e)}")
            return {
                'category': category,
                'timeframe': timeframe,
                'discussions': [],
                'error': str(e)
            }

    def _process_trending_posts(self, posts) -> List[Dict[str, Any]]:
        """
        Process Reddit posts into a structured format
        """
        trending_posts = []
        
        for post in posts:
            if not post.over_18:  # Skip NSFW content
                trending_posts.append({
                    "title": post.title,
                    "url": f"https://reddit.com{post.permalink}",
                    "score": post.score,
                    "num_comments": post.num_comments,
                    "subreddit": post.subreddit.display_name,
                    "created_utc": post.created_utc,
                    "selftext": post.selftext[:500] if post.selftext else ""  # Truncate long text
                })
        
        return trending_posts

    def get_active_subreddits(self, category: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most active subreddits for a given category
        
        Args:
            category: Optional category filter
            limit: Number of subreddits to return
            
        Returns:
            List of active subreddits with their metadata
        """
        try:
            if category:
                # Use the search function to find related subreddits
                subreddits = self.reddit.subreddits.search(category, limit=limit)
            else:
                # Get popular subreddits
                subreddits = self.reddit.subreddits.popular(limit=limit)
            
            active_subs = []
            for sub in subreddits:
                if not sub.over18:  # Filter out NSFW subreddits
                    sub_data = {
                        'name': sub.display_name,
                        'title': sub.title,
                        'description': sub.public_description,
                        'subscribers': sub.subscribers,
                        'active_users': sub.active_user_count,
                        'url': f"https://reddit.com{sub.url}",
                        'created_utc': sub.created_utc
                    }
                    active_subs.append(sub_data)
            
            return active_subs
            
        except Exception as e:
            logger.error(f"Error fetching active subreddits: {str(e)}")
            return []