import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import logging
import html2text

input_folder = 'tweet_collection/github'
output_folder = 'tweet_collection/github/markdown'

def extract_github_readme():
    """
    Extract README markdown from GitHub repository HTML pages
    
    Args:
        input_folder (str): Path to folder containing GitHub HTML files
        output_folder (str): Path to save extracted README markdown files
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Initialize HTML to Markdown converter
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = False
    h.body_width = 0  # Disable line wrapping
    h.unicode_snob = True  # Preserve unicode characters

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.html'):
            file_path = os.path.join(input_folder, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    soup = BeautifulSoup(file, 'html.parser')
                    
                    # Find README content
                    readme_content = None
                    
                    # Method 1: Look for README div with specific class
                    readme_div = soup.find('div', class_=re.compile(r'(readme|markdown-body)'))
                    if readme_div:
                        readme_content = readme_div
                    
                    # Method 2: Find article or main content with README
                    if not readme_content:
                        readme_article = soup.find('article', class_=re.compile(r'(readme|markdown)'))
                        if readme_article:
                            readme_content = readme_article
                    
                    # Method 3: Fallback to finding markdown content
                    if not readme_content:
                        markdown_content = soup.find_all(['div', 'article'], 
                                                        class_=re.compile(r'markdown|readme'))
                        if markdown_content:
                            readme_content = markdown_content[0]
                    
                    # Save README if content found
                    if readme_content:
                        # Generate output filename
                        output_filename = os.path.splitext(filename)[0] + '_README.md'
                        output_path = os.path.join(output_folder, output_filename)
                        
                        # Convert HTML to Markdown
                        markdown_content = h.handle(str(readme_content))
                        
                        # Write README to markdown file
                        with open(output_path, 'w', encoding='utf-8') as output_file:
                            output_file.write(markdown_content)
                        
                        logger.info(f'Extracted README for {filename}: {output_filename}')
                    else:
                        logger.warning(f'No README found in {filename}')
            
            except Exception as e:
                logger.error(f'Error processing {filename}: {e}')

def main():
    """
    Main execution method
    """
    input_folder = 'tweet_collection/github'
    output_folder = 'tweet_collection/github/markdown'
    
    extract_github_readme(input_folder, output_folder)

if __name__ == "__main__":
    main()
