from typing import Type, Dict, Any
from pathlib import Path
from .base import BaseConverter, BaseExtractor

class Registry:
    """Base registry class"""
    _registry: Dict[str, Type[Any]] = {}

    @classmethod
    def register(cls, name: str, component_class: Type[Any]):
        """Register a component if not already registered"""
        if name not in cls._registry:
            cls._registry[name] = component_class

    @classmethod
    def unregister(cls, name: str):
        """Unregister a component"""
        cls._registry.pop(name, None)
        
    @classmethod
    def get(cls, name: str, config_name: str = "default") -> Any:
        """Get a component instance with specific configuration"""
        if name not in cls._registry:
            raise ValueError(f"No {cls.__name__} registered for {name}")
        component_class = cls._registry[name]
        return component_class(config_name)

class ExtracterRegistry(Registry):
    """Registry for extractors"""
    _registry: Dict[str, Type[BaseExtractor]] = {}

    @classmethod
    def get_extractor(cls, extractor_type: str, config_name: str = "default") -> BaseExtractor:
        return cls.get(extractor_type, config_name)

class ConverterRegistry(Registry):
    """Registry for converters"""
    _registry: Dict[str, Type[BaseConverter]] = {}

    @classmethod
    def get_converter(cls, converter_type: str, config_name: str = "default") -> BaseConverter:
        return cls.get(converter_type, config_name)

# Remove the factory classes entirely and use registry classes directly

# Usage examples:
# text_extractor = ExtractorRegistry.get_extractor('text', 'default')
# image_extractor = ExtractorRegistry.get_extractor('image', 'thumbnail')
#
# pdf_converter = ConverterRegistry.get_converter('pdf', 'fast')
# html_converter = ConverterRegistry.get_converter('html', 'minimal')

# Usage examples:
# factory = ExtractorFactory()
# text_extractor = factory.create_extractor('text', 'default')
# image_extractor = factory.create_extractor('image', 'thumbnail')
#
# factory = ConverterFactory()
# pdf_converter = factory.create_converter('pdf', 'fast')
# html_converter = factory.create_converter('html', 'minimal')