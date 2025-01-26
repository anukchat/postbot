from markitdown import MarkItDown
from pathlib import Path
import markdownify
from typing import Dict, Any

from src.backend.extraction.base import BaseConverter
import requests

class HTMLConverter(BaseConverter):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"converters.html.{config_name}")
    
    def _setup_converter(self):
        # No setup needed for markdownify
        pass
        
    def convert(self, input: str, **custom_params) -> str:
        import os.path

        # Check if input is URL
        if input.startswith(('http://', 'https://')):
            response = requests.get(input)
            html = response.text
        # Check if input is a file path
        elif os.path.isfile(input):
            with open(input, 'r') as f:
                html = f.read()
        # Treat as HTML string
        else:
            html = input
            
        params = self.merge_method_params(custom_params)
        return markdownify.markdownify(html, **params)

class PDFConverter(BaseConverter):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"converters.pdf.{config_name}")
    
    def _setup_converter(self):
        """Initialize MarkItDown with class params"""
        self.converter = MarkItDown(**self.config.class_params)
        
    def convert(self, input_file: str, **custom_params) -> str:
        params = self.merge_method_params(custom_params)
        result = self.converter.convert(str(input_file), **params)
        return result.text_content
    
class GenericConverter(BaseConverter):
    def __init__(self, config_name: str = "default"):
        super().__init__(f"converters.generic.{config_name}")
    
    def _setup_converter(self):
        """Initialize MarkItDown with class params"""
        self.converter = MarkItDown(**self.config.class_params)
        
    def convert(self, input_file: str, **custom_params) -> str:
        params = self.merge_method_params(custom_params)
        result = self.converter.convert(str(input_file), **params)
        return result.text_content