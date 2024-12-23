import logging
from pathlib import Path
import traceback
from docling.document_converter import DocumentConverter
import markdownify
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
    
    def extract_pdf(self, input_file, output_file):
        """
        Extract PDF content using docling
        
        Args:
            input_file (Path): Input PDF file path
            output_file (Path): Output markdown file path
        """
        try:
            
            # Extract markdown
            markdown_content =  self.converter.convert(str(input_file)).document.export_to_markdown()
            
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
    
    def extract_html(self, input_file, output_file):
        
        try:
            with open(input_file) as f:
                html_content = f.read()
                markdown_content=markdownify.markdownify(html_content)

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Write markdown content
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            logger.info(f"Successfully extracted markdown from {input_file}")
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

# def convert_pdfs_to_markdown():
#     """
#     Main execution method
#     """
#     extractor = DocumentExtractor()
    
#     # Process all supported document types
#     extractor.process_documents()

#     # Optionally, process a specific type
#     # extractor.process_documents('pdf')

#     # Example of adding a custom extraction method
#     # def custom_txt_extractor(input_file, output_file):
#     #     with open(input_file, 'r') as f:
#     #         content = f.read()
#     #     with open(output_file, 'w') as f:
#     #         f.write(content)
#     # 
#     # extractor.add_document_type('txt', custom_txt_extractor)



# if __name__ == "__main__":
    # convert_pdfs_to_markdown()