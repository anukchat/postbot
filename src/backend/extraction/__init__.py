from src.backend.extraction.extractors.reddit import RedditExtractor
from src.backend.extraction.extractors.arxiv import ArxivExtractor
from src.backend.extraction.extractors.image import ImageExtractor
from src.backend.extraction.extractors.text import TextExtractor
from src.backend.extraction.extractors.pdf import PdfExtractor
from src.backend.extraction.extractors.html import HtmlExtractor
from src.backend.extraction.extractors.arxiv import ArxivExtractor
from src.backend.extraction.extractors.image import ImageExtractor
from src.backend.extraction.extractors.twitter import TwitterExtractor
from src.backend.extraction.extractors.github import GithubExtractor

from .factory import ExtracterRegistry, ConverterRegistry

from src.backend.extraction.converters.markdown import PDFConverter, HTMLConverter, GenericConverter

def register_extractors():
    """Register all extractors if not already registered"""
    extractors = {
        'text': TextExtractor,
        'image': ImageExtractor,
        'pdf': PdfExtractor,
        'html': HtmlExtractor,
        'arxiv': ArxivExtractor,
        'image': ImageExtractor,
        'twitter': TwitterExtractor,
        'github': GithubExtractor,
        'reddit': RedditExtractor,
    }
    
    for name, extractor_class in extractors.items():
        if name not in ExtracterRegistry._registry:
            ExtracterRegistry.register(name, extractor_class)


def register_converters():
    """Register all converters if not already registered"""
    converters = {
        'pdf': PDFConverter,
        'html': HTMLConverter,
        'generic': GenericConverter
    }
    
    for name, converter_class in converters.items():
        if name not in ConverterRegistry._registry:
            ConverterRegistry.register(name, converter_class)


# Auto-register extractors
register_extractors()

# Auto-register converters
register_converters()
