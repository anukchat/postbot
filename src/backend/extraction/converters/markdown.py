from markitdown import MarkItDown
from pathlib import Path
import markdownify
from typing import Dict, Any

from src.backend.extraction.base import BaseConverter

class HTMLConverter(BaseConverter):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"converters.html.{config_name}")
    
    def _setup_converter(self):
        # No setup needed for markdownify
        pass
        
    def convert(self, input_file: Path, **custom_params) -> str:
        with open(input_file, 'r') as f:
            html = f.read()
        params = self.merge_method_params(custom_params)
        return markdownify.markdownify(html, **params)

class PDFConverter(BaseConverter):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"converters.pdf.{config_name}")
    
    def _setup_converter(self):
        """Initialize MarkItDown with class params"""
        self.converter = MarkItDown(**self.config.class_params)
        
    def convert(self, input_file: Path, **custom_params) -> str:
        params = self.merge_method_params(custom_params)
        result = self.converter.convert(str(input_file), **params)
        return result.text_content
    
class GenericConverter(BaseConverter):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"converters.generic.{config_name}")
    
    def _setup_converter(self):
        """Initialize MarkItDown with class params"""
        self.converter = MarkItDown(**self.config.class_params)
        
    def convert(self, input_file: Path, **custom_params) -> str:
        params = self.merge_method_params(custom_params)
        result = self.converter.convert(str(input_file), **params)
        return result.text_content