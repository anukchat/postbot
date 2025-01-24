
from src.backend.extraction.base import BaseExtractor


class ResearchExtractor(BaseExtractor):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"extractors.research.{config_name}")

    def _setup_extractor(self):
        # Initialize text extraction specific setup using self.config.class_params
        pass
        
        
    def extract(self, source: str, **method_params) -> dict:
        params = self.merge_method_params(method_params)
        # Implement image extraction logic
        return {"type": "image", "path": source}
