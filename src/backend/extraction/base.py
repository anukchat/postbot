from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, List
from src.backend.config import Config, ConfigLoader

class BaseExtractor(ABC):
    def __init__(self, config_path: str):
        """Initialize extractor with configuration path
        Args:
            config_path: dot notation path to config (e.g. "extractors.text.default")
        """
        self.loader = ConfigLoader()
        self.config = self.loader.get_config(config_path)
        self._setup_extractor()
    
    @abstractmethod
    def _setup_extractor(self):
        """Initialize the extractor with class params"""
        pass
        
    @abstractmethod
    def extract(self, source: str, **method_params) -> dict:
        """Extract data from the source"""
        pass

    @abstractmethod
    def create_summary(self, summary_obj: List[dict], **method_params) -> str:
        """Create a summary from the extracted data"""
        pass
    
    def merge_method_params(self, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge default method params with custom params"""
        params = self.config.method_params.copy()
        params.update(custom_params)
        return params

class BaseConverter(ABC):
    def __init__(self, config_path: str):
        self.loader = ConfigLoader()
        self.config = self.loader.get_config(config_path)
        self._setup_converter()
    
    @abstractmethod
    def _setup_converter(self):
        """Initialize converter with class params"""
        raise NotImplementedError
        
    def merge_method_params(self, custom_params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge default method params with custom params"""
        params = self.config.method_params.copy()
        params.update(custom_params)
        return params

    @abstractmethod
    def convert(self, input_file: str, **custom_params) -> str:
        """Convert input file to markdown"""
        raise NotImplementedError