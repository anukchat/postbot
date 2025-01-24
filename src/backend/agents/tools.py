from googlesearch import search as google_search
from duckduckgo_search import DDGS
import time
from urllib.error import HTTPError

class WebSearch:
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


def main():
    # Create an instance and use instance method
    searcher = WebSearch(provider='duckduckgo', num_results=5)
    results = searcher.search("CUDA Deep dive")
    print(f"Total results: {results.get_results_count()}")
    print(f"URLS: {results.get_all_urls()}")

if __name__ == "__main__":
    main()
