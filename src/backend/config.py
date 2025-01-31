from dataclasses import dataclass, field
from typing import Dict, Any, List
import yaml
import os
from functools import reduce

@dataclass
class Config:
    name: str
    path: str  # Full path like "extractors.pdf.default"
    class_params: Dict[str, Any] = field(default_factory=dict)
    method_params: Dict[str, Any] = field(default_factory=dict)

class ConfigLoader:
    def __init__(self, config_path: str = None):
        if config_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'config.yaml')
        
        with open(config_path, 'r') as f:
            self.config_data = yaml.safe_load(f)

    def _get_by_path(self, path: str) -> dict:
        """Get configuration using dot notation path"""
        try:
            result = reduce(lambda d, key: d[key], path.split('.'), self.config_data)
            print(f"Config data at path '{path}': {result}")
            return result
        except (KeyError, TypeError):
            available = self.list_configs()
            raise ValueError(f"Configuration path '{path}' not found. Available paths: {available}")

    def get_config(self, path: str) -> Config:
        """
        Get configuration by path using dot notation
        Example paths: 
            - extractors.pdf.default
            - llm.chat
            - processors.image.thumbnail
        """
        config_data = self._get_by_path(path)
        if not isinstance(config_data, dict):
            raise ValueError(f"Invalid configuration at path '{path}'")

        return Config(
            name=path.split('.')[-1],
            path=path,
            class_params=config_data.get('class_params', {}),
            method_params=config_data.get('method_params', {})
        )

    def list_configs(self, prefix: str = "") -> List[str]:
        """List all available configuration paths with given prefix"""
        def _collect_paths(d: dict, current_path: str = "") -> List[str]:
            paths = []
            for k, v in d.items():
                new_path = f"{current_path}.{k}" if current_path else k
                if isinstance(v, dict):
                    if 'class_params' in v or 'method_params' in v:
                        paths.append(new_path)
                    else:
                        paths.extend(_collect_paths(v, new_path))
            return paths

        paths = _collect_paths(self.config_data)
        if prefix:
            paths = [p for p in paths if p.startswith(prefix)]
        return paths

# Usage examples:
# loader = ConfigLoader()
# pdf_config = loader.get_config("extractors.pdf.default")
# image_config = loader.get_config("processors.image.thumbnail")
# llm_config = loader.get_config("llm.chat")