
import requests
from src.backend.clients.github import GithubClient
from src.backend.extraction.base import BaseExtractor


class GithubExtractor(BaseExtractor):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"extractors.github.{config_name}")

    def _setup_extractor(self):
        # Initialize text extraction specific setup using self.config.class_params
        pass
        
    
    def extract(self, source: str, **method_params) -> dict:
        params = self.merge_method_params(method_params)
        
        # Extract owner and repo from URL
        parts = source.strip('/').split('/')
        owner = parts[-2]
        repo = parts[-1]
        
        # Initialize GitHub client
        
        # Get README content
        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        response = requests.get(readme_url, headers={"Accept": "application/vnd.github.v3+json"})
        response.raise_for_status()
        
        if not response:
            raise ValueError(f"Could not fetch README for {source}")
            
        download_url = response.json()['download_url']
        
        return {
            "type": "github",
            "path": source,
            "owner": owner,
            "repo": repo,
            "readme_url": download_url
        }
