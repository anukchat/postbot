import logging
import os
from pathlib import Path
import re
import traceback
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
import html2text
import markdownify
import requests
import urllib
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DocumentExtractor:
    """
    Extensible document extraction framework
    """
    def __init__(self, 
                 input_base_dir='tweet_collection', 
                 output_base_dir='tweet_collection'):
        """
        Initialize document extractor
        
        Args:
            input_base_dir (str): Base input directory
            output_base_dir (str): Base output directory
        """
        self.input_base_dir = Path(input_base_dir)
        self.output_base_dir = Path(output_base_dir)
        
        # Supported document types and their extraction strategies
        self.document_types = {
            'pdf': self.extract_pdf,
            'arxiv': self.extract_pdf,
            # 'github':self.extract_html,
            'html':self.extract_html
            # Easily extensible for other document types
            # 'docx': self.extract_docx,
            # 'txt': self.extract_txt,
        }
        self.converter= DocumentConverter()
    
    def extract_pdf(self, input_file, output_file=None):
        """
        Extract PDF content using docling
        
        Args:
            input_file (Path): Input PDF file path
            output_file (Path): Output markdown file path
        """
        try:
            markdown_content =  self.converter.convert(str(input_file)).document.export_to_markdown()
            if output_file is None:
                # Extract markdown
                return markdown_content
            else:
                # Ensure output directory exists
                output_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Write markdown content
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                
                logger.info(f"Successfully extracted markdown from {input_file}")
                return True
        
        except Exception as e:
            logger.error(f"Error extracting PDF {input_file}: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def extract_html(self, input_file=None, output_file=None, html_content=None):  
        try:

            # Extract markdown
            if html_content:
                markdown_content=markdownify.markdownify(html_content)
                if not output_file:
                    return markdown_content
                else:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    return True
            else:
                with open(input_file) as f:
                    html_content = f.read()
                    markdown_content=markdownify.markdownify(html_content)
                if not output_file:
                    return markdown_content
                else:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    return True
        except Exception as e:
            logger.error(f"Error extracting html {input_file}: {e}")
            logger.debug(traceback.format_exc())
            return False

    def process_documents(self, document_type=None):
        """
        Process documents of specified or all supported types
        
        Args:
            document_type (str, optional): Specific document type to process
        """
        # If no specific type provided, process all supported types
        if document_type is None:
            document_types_to_process = self.document_types.keys()
        else:
            document_types_to_process = [document_type]
        
        # Process each document type
        for doc_type in document_types_to_process:
            # Construct input and output paths
            input_dir = self.input_base_dir / doc_type
            output_dir = self.output_base_dir / doc_type / 'markdown'
            
            # Create output directory
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if input directory exists
            if not input_dir.exists():
                logger.warning(f"Input directory not found: {input_dir}")
                continue
            
            # Process each file in the input directory
            for input_file in input_dir.glob('*'):

                print(f"Converting to markdown for file: {input_file}")
                # Skip directories
                if input_file.is_dir():
                    continue
                
                # Generate output filename
                output_file = output_dir / f"{input_file.stem}.md"
                
                # Extract document
                extraction_method = self.document_types.get(doc_type)
                if extraction_method:
                    extraction_method(input_file, output_file)
    
    def add_document_type(self, doc_type, extraction_method):
        """
        Add a new document type extraction method
        
        Args:
            doc_type (str): Document type identifier
            extraction_method (callable): Method to extract content
        """
        self.document_types[doc_type] = extraction_method

    def extract_arxiv_pdf(self,url, output_file=None):
        """
        Extract PDF content from an arXiv URL and convert it to Markdown using the docling library.
        
        Args:
            url (str): URL to arXiv abstract page (e.g., https://arxiv.org/abs/2312.01700).
            output_file (Path): Output markdown file path.
        
        Returns:
            str: Markdown content if successful, False otherwise.
        """
        try:
            # Construct the PDF URL from the arXiv abstract page URL
            if not url.endswith('.pdf'):
                paper_id = url.split('/')[-1]
                pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
            else:
                pdf_url = url
            
            # Download the PDF content
            pdf_response = requests.get(pdf_url, timeout=10)
            pdf_response.raise_for_status()  # Raise an exception for HTTP errors
            
            
            # Convert PDF to Markdown using the docling library
            markdown_content = self.converter.convert(pdf_url).document.export_to_markdown()
            
            # Save markdown content
            if output_file:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
            
            # Clean up temporary file
            # temp_pdf_path.unlink()
            
            return markdown_content
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while accessing {url}: {e}")
        except Exception as e:
            logger.error(f"Error processing {url}: {e}")
            logger.debug(traceback.format_exc())
        
        return False

    def extract_github_readme(self,repo_url):
        """
        Extracts the markdown content of the README file from a GitHub repository URL.

        :param repo_url: The URL of the GitHub repository.
        :return: The markdown content of the README file.
        """
        try:
            # Extract owner and repo name from the URL
            parts = repo_url.strip('/').split('/')
            owner = parts[-2]
            repo = parts[-1]

            # GitHub API URL to fetch the README
            api_url = f"https://api.github.com/repos/{owner}/{repo}/readme"

            # Make a request to the GitHub API
            response = requests.get(api_url, headers={"Accept": "application/vnd.github.v3+json"})
            response.raise_for_status()

            # Get the download URL for the README
            download_url = response.json()['download_url']

            # Fetch the README content
            readme_response = requests.get(download_url)
            readme_response.raise_for_status()

            # Initialize HTML to Markdown converter
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.body_width = 0  # Disable line wrapping
            h.unicode_snob = True  # Preserve unicode characters

            # Convert README content to markdown
            markdown_content = h.handle(readme_response.text)

            return markdown_content

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching README from {repo_url}: {e}")
            return None