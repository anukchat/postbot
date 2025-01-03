import os
import sys
import logging
from pathlib import Path
from extractors.twitter import TweetMetadataCollector
# from extractors.arxiv import download_pdfs_from_arxiv
from extractors.docintelligence import DocumentExtractor
# from extractors.github import extract_github_readme


import os
import urllib.parse
import requests
from bs4 import BeautifulSoup
import urllib3
import urllib
# from util import extract_pdf_to_markdown
from docling import DocumentConverter

import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tweet_collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

import os
import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import logging
import html2text

def extract_github_readme():
    input_folder = 'tweet_collection/github'
    output_folder = 'tweet_collection/github/markdown'
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
        print(f"Extracting github readme from {filename}")
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
                        output_filename = os.path.splitext(filename)[0] + '.md'
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

def tweets_meta_collector(recent_k=50):
    """
    Main execution method for tweet metadata collection
    """
    # Create data and output directories if they don't exist
    Path('data').mkdir(exist_ok=True)
    Path('tweet_collection').mkdir(exist_ok=True)

    # Find the most recent Twitter Bookmarks CSV
    try:
        csv_files = list(Path('data').glob('twitter-Bookmarks-*.csv'))
        
        if not csv_files:
            logger.error("No Twitter Bookmarks CSV files found in 'data/' directory.")
            print("Error: Please place your Twitter Bookmarks CSV in the 'data/' directory.")
            print("Filename should start with 'twitter-Bookmarks-'")
            sys.exit(1)
        
        # Select the most recent CSV file
        csv_path = max(csv_files, key=os.path.getctime)
        logger.info(f"Processing CSV file: {csv_path}")

    except Exception as e:
        logger.error(f"Error finding CSV file: {e}")
        sys.exit(1)

    try:
        # Read tweet data
        tweets_df = read_tweet_data(csv_path,recent_k)
        
        # Initialize metadata collector
        collector = TweetMetadataCollector()
        
        # Process tweets
        processed_tweets = collector.process_tweet_collection(tweets_df)
        
        # Print summary
        print(f"Processed {len(processed_tweets)} tweets")
        print(f"Metadata saved to {collector.dirs['metadata'] / 'processed_tweets.json'}")
        print(f"Detailed logs in tweet_collector.log")
    
    except Exception as e:
        logger.error(f"Unexpected error in main execution: {e}")
        print(f"Error: {e}")
        sys.exit(1)

def read_tweet_metadata(tweet_id):
    file_path="tweet_collection/metadata/comprehensive_metadata.json"
    df=pd.read_json(file_path)

def read_tweet_data(csv_path, recent_k=None):
    """
    Read tweet data from a CSV file.
    
    Args:
        csv_path (str): Path to the CSV file.
        recent_k (int, optional): Number of most recent tweets to return. 
                                  If None, returns all tweets.
    
    Returns:
        pd.DataFrame: DataFrame containing tweet data.
    """
    # Read the entire CSV
    df = pd.read_csv(csv_path)
    
    # Sort by created_at in descending order to get most recent tweets first
    df['created_at'] = pd.to_datetime(df['created_at'])
    df_sorted = df.sort_values('created_at', ascending=False)
    
    # Return recent_k tweets if specified, otherwise return all
    if recent_k is not None:
        return df_sorted.head(recent_k)
    
    return df_sorted

def download_pdfs_from_arxiv():
    input_folder = 'tweet_collection/arxiv'
    output_folder = 'tweet_collection/arxiv'

    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through HTML files in the input folder
    for filename in os.listdir(input_folder):
        print(f"Downloading pdfs from arxiv {filename}")
        if filename.endswith('.html'):
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'r') as file:
                soup = BeautifulSoup(file, 'html.parser')
                pdf_links = soup.find_all('a', href=True)

                for link in pdf_links:
                    if 'pdf' in link['href']:
                        pdf_url = link['href']
                        pdf_name = os.path.basename(pdf_url)
                        pdf_path = os.path.join(output_folder, filename.replace(".html",".pdf"))

                        # Download the PDF
                        response = requests.get(urllib.parse.urljoin("https://arxiv.org/",pdf_url))
                        with open(pdf_path, 'wb') as pdf_file:
                            pdf_file.write(response.content)
                            print(f'Downloaded: {pdf_name}')

def process_from_arxiv_pdf(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    pdf_links = soup.find_all('a', href=True)

    for link in pdf_links:
        if 'pdf' in link['href']:
            pdf_url = link['href']
            pdf_name = os.path.basename(pdf_url)

            # Download the PDF content
            pdf_response = requests.get(urllib.parse.urljoin("https://arxiv.org/", pdf_url))
            pdf_content = pdf_response.content

            # Convert PDF to markdown using DocumentConverter from docling
            converter = DocumentConverter()
            markdown_content = converter.convert(pdf_content).document.export_to_markdown()

            # Save the markdown content to a file
            markdown_path = os.path.join('tweet_collection/arxiv', pdf_name.replace('.pdf', '.md'))
            with open(markdown_path, 'w') as md_file:
                md_file.write(markdown_content)
                print(f'Converted to Markdown: {markdown_path}')

if __name__ == "__main__":
    extractor = DocumentExtractor()
    
    # Process all supported document types
    
    tweets_meta_collector(recent_k=40)
    download_pdfs_from_arxiv()
    extract_github_readme()

    extractor.process_documents()
