
from typing import List
from src.backend.extraction.base import BaseExtractor


class HtmlExtractor(BaseExtractor):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"extractors.html.{config_name}")

    def _setup_extractor(self):
        # Initialize text extraction specific setup using self.config.class_params
        pass
        
        
    def extract(self, source: str, **method_params) -> dict:
        params = self.merge_method_params(method_params)
        # Implement image extraction logic
        return {"type": "html", "path": source}
    
    def create_summary(self, summary_obj: List[dict], **method_params) -> str:
        pass
