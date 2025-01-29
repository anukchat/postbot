from abc import ABC, abstractmethod
import os
import time
from urllib.error import HTTPError
import praw
from langchain_community.tools import DuckDuckGoSearchResults, BraveSearch
from langchain_community.utilities import SerpAPIWrapper,GoogleSerperAPIWrapper,DuckDuckGoSearchAPIWrapper
import json

from src.backend.extraction.factory import ExtracterRegistry

class Search(ABC):
    @abstractmethod
    def search(self, query, max_retries=3):
        pass

class WebSearch(Search):
    PROVIDERS = {
        'google': lambda: GoogleSerperAPIWrapper(k=15),
        'serpapi': lambda: SerpAPIWrapper(),
        'duckduckgo': lambda: DuckDuckGoSearchResults(output_format="list", num_results=15)
    }

    def __init__(self, provider='duckduckgo', num_results=15):
        """
        Initialize web search with specified provider
        :param provider: Search provider ('google', 'serpapi', or 'duckduckgo')
        :param num_results: Number of results to return
        """
        self.provider = provider.lower()
        self.num_results = num_results
        self.results = []
        
        if self.provider not in self.PROVIDERS:
            raise ValueError(f"Provider {provider} not supported. Use one of: {', '.join(self.PROVIDERS.keys())}")
        
        self.search_tool = self.PROVIDERS[self.provider]()

    def search(self, query, max_retries=3):
        """
        Execute search using selected provider
        :param query: Search query string
        :param max_retries: Maximum number of retries on rate limit
        :return: self for method chaining
        """
        for attempt in range(max_retries):
            try:

                if self.provider in ['duckduckgo']:
                    search_results = self.search_tool.invoke(query)
                else:
                    search_results =self.search_tool.results(query)
                
                # Parse results based on provider
                if self.provider in ['google', 'serpapi']:
                    self.results = search_results['organic']
                else:  # duckduckgo
                    self.results = search_results
                    
                return self
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise e
        return self

    def get_results(self):
        """Get all search results"""
        return self.results

    def get_all_urls(self):
        """Get all result URLs"""
        if self.provider in ['google', 'serpapi']:
            return [result['link'] for result in self.results]
        return [result['link'] for result in self.results]  # DuckDuckGo format

    def get_all_titles(self):
        """Get all result titles"""
        if self.provider in ['google', 'serpapi']:
            return [result['title'] for result in self.results]
        return [result['title'] for result in self.results]  # DuckDuckGo format

class RedditSearch(Search):

    def __init__(self):
        """Initialize Reddit API client and extractor"""
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret= os.getenv('REDDIT_CLIENT_SECRET')
        user_agent= os.getenv('REDDIT_USER_AGENT')
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )
        self.extractor=ExtracterRegistry.get_extractor("reddit")
        self.results = []

    def search(self, query, max_retries=3, subreddit=None, limit=10):
        """Search Reddit posts and extract content"""
        for attempt in range(max_retries):
            try:
                if query.startswith(('https://www.reddit.com/', 'https://reddit.com/')):
                    # Handle Reddit URL
                    submission = self.reddit.submission(url=query)
                    extracted_content = self.extractor.extract(query,skip_llm=True)
                    self.results = [{
                        'title': submission.title,
                        'url': submission.url,
                        'subreddit': submission.subreddit.display_name,
                        'score': submission.score,
                        'num_comments': submission.num_comments,
                        'content': extracted_content.get('content', ''),
                        # 'summary': extracted_content.get('summary', ''),
                        'top_comments': extracted_content.get('top_comments', [])
                    }]
                else:
                    # Handle keyword search
                    if subreddit:
                        submissions = self.reddit.subreddit(subreddit).search(query, limit=limit)
                    else:
                        submissions = self.reddit.subreddit('all').search(query, limit=limit)

                    self.results = []
                    for submission in submissions:
                        extracted_content = self.extractor.extract(f"https://reddit.com{submission.permalink}",skip_llm=True)
                        self.results.append({
                            'title': submission.title,
                            'url': submission.url,
                            'subreddit': submission.subreddit.display_name,
                            'score': submission.score,
                            'num_comments': submission.num_comments,
                            'content': extracted_content.get('content', ''),
                            # 'summary': extracted_content.get('summary', ''),
                            'top_comments': extracted_content.get('top_comments', [])
                        })
                    
                return self.results

            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(2 ** attempt)

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
