from abc import ABC, abstractmethod
import os
from googlesearch import search as google_search
from duckduckgo_search import DDGS
import time
from urllib.error import HTTPError
import praw

class Search(ABC):
    @abstractmethod
    def search(self, query, max_retries=3):
        pass

class WebSearch(Search):
    PROVIDERS = {
        'google': lambda query, num_results: list(google_search(query, num=num_results)),
        'duckduckgo': lambda query, num_results: list(DDGS().text(query, max_results=num_results))
    }

    def __init__(self, provider='google', num_results=10):
        """
        Initialize web search with specified provider
        :param provider: Search provider ('google' or 'duckduckgo')
        :param num_results: Number of results to return
        """
        self.provider = provider.lower()
        self.num_results = num_results
        self.results = []
        
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Provider {provider} not supported. Use one of: {', '.join(self.PROVIDERS.keys())}")
        
    def search(self, query, max_retries=3):
        """
        Execute search using selected provider
        :param query: Search query string
        :param max_retries: Maximum number of retries on rate limit
        :return: self for method chaining
        """
        for attempt in range(max_retries):
            try:
                self.results = self.PROVIDERS[self.provider](query, self.num_results)
                return self
            except HTTPError as e:
                if e.code == 429 and attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))  # Exponential backoff
                else:
                    raise
        self.results = self.PROVIDERS[self.provider](query, self.num_results)
        return self

    def get_results(self):
        """Get all search results"""
        return self.results

    def get_results_count(self):
        """Get number of results"""
        return len(self.results)

    def get_result(self, index):
        """Get single result by index"""
        if 0 <= index < len(self.results):
            return self.results[index]
        raise IndexError("Result index out of range")

    def get_all_urls(self):
        """Get all result URLs"""
        if self.provider == 'google':
            return self.results
        return [result['href'] for result in self.results]

    def get_all_titles(self):
        """Get all result titles"""
        if self.provider == 'google':
            return None  # Google search doesn't provide titles
        return [result['title'] for result in self.results]

class RedditSearch(Search):

    def __init__(self):
        """Initialize Reddit API client"""

        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret= os.getenv('REDDIT_CLIENT_SECRET')
        user_agent= os.getenv('REDDIT_USER_AGENT')
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.results = []

    def search(self, query, max_retries=3, subreddit=None, limit=10):
        """Search Reddit posts"""
        for attempt in range(max_retries):
            try:
                if query.startswith(('https://www.reddit.com/', 'https://reddit.com/')):
                    # Handle Reddit URL
                    submission = self.reddit.submission(url=query)
                    self.results = [{
                        'title': submission.title,
                        'url': submission.url,
                        'score': submission.score,
                        'text': submission.selftext,
                        'author': str(submission.author),
                        'subreddit': submission.subreddit.display_name
                    }]
                else:
                    # Handle regular search query
                    if subreddit:
                        posts = self.reddit.subreddit(subreddit).search(query, limit=limit)
                    else:
                        posts = self.reddit.subreddit('all').search(query, limit=limit)
                    
                    self.results = [{
                        'title': post.title,
                        'url': post.url,
                        'score': post.score,
                        'text': post.selftext,
                        'author': str(post.author),
                        'subreddit': post.subreddit.display_name
                    } for post in posts]
                return self
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(5 * (attempt + 1))
                else:
                    raise

    def get_results(self):
        """Get all search results"""
        return self.results

def main():
    # Create an instance and use instance method
    # searcher = WebSearch(provider='duckduckgo', num_results=5)
    # results = searcher.search("CUDA Deep dive")
    # print(f"Total results: {results.get_results_count()}")
    # print(f"URLS: {results.get_all_urls()}")
    # Test RedditSearch
    reddit_searcher = RedditSearch()
    # Search by query
    results = reddit_searcher.search("Python programming", limit=3)
    print("\nReddit Search Results:")
    for result in results.get_results():
        print(f"\nTitle: {result['title']}")
        print(f"Subreddit: r/{result['subreddit']}")
        print(f"Score: {result['score']}")
        print(f"URL: {result['url']}")

    # Search by Reddit URL
    url_results = reddit_searcher.search("https://www.reddit.com/r/LocalLLaMA/comments/1i82ba3/deepseek_r1_review_from_casual_user/")
    print("\nReddit URL Search Result:")
    if url_results.get_results():
        post = url_results.get_results()[0]
        print(f"Title: {post['title']}")
        print(f"Author: u/{post['author']}")
        print(f"Text: {post['text'][:200]}...")

if __name__ == "__main__":
    main()
