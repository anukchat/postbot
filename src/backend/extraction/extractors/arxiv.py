
import tempfile
import requests
from src.backend.extraction.base import BaseExtractor


class ArxivExtractor(BaseExtractor):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"extractors.arxiv.{config_name}")

    def _setup_extractor(self):
        # Initialize text extraction specific setup using self.config.class_params
        pass
        
    def _extract_paper_id(self, url: str) -> str:
        """Extract paper ID from arxiv URL."""
        if url.endswith('.pdf'):
            return url.split('/')[-1].replace('.pdf', '')
        return url.split('/')[-1]

    def _construct_pdf_url(self, paper_id: str) -> str:
        """Construct PDF URL from paper ID."""
        return f"https://arxiv.org/pdf/{paper_id}.pdf"

    def extract(self, source: str, **method_params) -> dict:
        params = self.merge_method_params(method_params)
        try:
            paper_id = self._extract_paper_id(source)
            pdf_url = self._construct_pdf_url(paper_id)
            
            return {"type": "arxiv", "url": pdf_url}
            
        except Exception as e:
            raise Exception(f"Failed to extract PDF from arXiv: {str(e)}")
