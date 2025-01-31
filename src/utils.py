from datetime import datetime
import re
from urllib.parse import urlparse
import uuid
import pandas as pd
import logging
import json
import ast
import urllib
import mimetypes
import requests
from bs4 import BeautifulSoup 
import tempfile
import os

from dotenv import load_dotenv

# Load environment variables
load_dotenv()
from supabase import create_client, Client


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


def supabase_client():
    # Initialize the Supabase client
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    return create_client(supabase_url, supabase_key)

def safe_json_loads(json_str, default=None):
    """
    Safely parse JSON or string-represented list/dict
    
    Args:
        json_str: Input string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed data or default
    """
    if pd.isna(json_str) or not isinstance(json_str, str):
        return default
    
    try:
        # Try JSON parsing first
        return json.loads(json_str.replace("'", '"'))
    except json.JSONDecodeError:
        try:
            # Fallback to ast.literal_eval for string representations
            return ast.literal_eval(json_str)
        except (ValueError, SyntaxError):
            logger.warning(f"Could not parse: {json_str}")
            return default

def safe_convert_to_list(value, default=None):
    """
    Convert value to list safely
    
    Args:
        value: Input value to convert
        default: Default value if conversion fails
    
    Returns:
        list: Converted list
    """
    if default is None:
        default = []
    
    if pd.isna(value):
        return default
    
    try:
        # If it's already a list, return it
        if isinstance(value, list):
            return value
        
        # Try parsing as JSON or string representation
        parsed = safe_json_loads(str(value), default)
        return parsed if isinstance(parsed, list) else default
    
    except Exception as e:
        logger.warning(f"Could not convert to list: {value}. Error: {e}")
        return default

def safe_convert_to_dict(value, default=None):
    """
    Convert value to dictionary safely
    
    Args:
        value: Input value to convert
        default: Default value if conversion fails
    
    Returns:
        dict: Converted dictionary
    """
    if default is None:
        default = {}
    
    if pd.isna(value):
        return default
    
    try:
        # If it's already a dict, return it
        if isinstance(value, dict):
            return value
        
        # Try parsing as JSON or string representation
        parsed = safe_json_loads(str(value), default)
        return parsed if isinstance(parsed, dict) else default
    
    except Exception as e:
        logger.warning(f"Could not convert to dict: {value}. Error: {e}")
        return default

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

def classify_url(url):
    """
    Classify URL type with enhanced detection and error handling
    
    Args:
        url (str): URL to classify
    
    Returns:
        dict: Detailed URL classification
    """
    try:
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc.lower()
        path = parsed_url.path.lower()

        # Comprehensive URL type classification
        url_types = {
            # Code and Development Platforms
            'github_code': {
                'condition': 'github.com' in domain and ('/blob/' in path or '/tree/' in path),
                'category': 'code'
            },
            'github': {
                'condition': 'github.com' in domain and ('/blob/' not in path or '/tree/' not in path),
                'category': 'repo'
            },
            'gitlab_code': {
                'condition': 'gitlab.com' in domain and ('/blob/' in path or '/tree/' in path),
                'category': 'code'
            },
            'bitbucket_code': {
                'condition': 'bitbucket.org' in domain and '/src/' in path,
                'category': 'code'
            },
            
            # Jupyter and Notebook Platforms
            'jupyter_notebook': {
                'condition': (
                    'nbviewer.jupyter.org' in domain or 
                    '.ipynb' in path or 
                    'colab.research.google.com' in domain or
                    'kaggle.com/notebooks' in domain
                ),
                'category': 'code'
            },
            
            # Document Types
            'pdf': {
                'condition': path.endswith('.pdf'),
                'category': 'document'
            },
            'google_docs': {
                'condition': 'docs.google.com' in domain,
                'category': 'document'
            },
            
            # Media and Hosting Platforms
            'youtube': {
                'condition': ('youtube.com' in domain or 'youtu.be' in domain) and ('/watch' in path or '/v/' in path),
                'category': 'video'
            },
            'vimeo': {
                'condition': 'vimeo.com' in domain,
                'category': 'video'
            },
            
            # Academic and Research
            'arxiv': {
                'condition': 'arxiv.org' in domain,
                'category': 'document'
            },
            
            # Web Content
            'html': {
                'condition': path.endswith('.html') or not path.endswith(('.pdf', '.ipynb')),
                'category': 'webpage'
            },
            
            # Social Media
            'tweet': {
                'condition': ('twitter.com' in domain or 'x.com' in domain) and '/status/' in path,
                'category': 'metadata'
            }
        }
        
        # Find the first matching type with most specific conditions
        matched_type = next(
            (k for k, v in url_types.items() if v['condition']), 
            'unknown'
        )
        
        # Log unrecognized URL types
        if matched_type == 'unknown':
            logger.info(f"Unrecognized URL type: {url}")
        
        return {
            'type': matched_type,
            'domain': domain,
            'path': path,
            'category': url_types.get(matched_type, {}).get('category', 'unknown')
        }
    
    except Exception as e:
        logger.error(f"Error classifying URL {url}: {e}")
        return {
            'type': 'unknown',
            'domain': '',
            'path': '',
            'category': 'error'
        }
      
def get_url_metadata(url):
    """
    Download content from a URL 
    Args:
        url (str): URL to download
        index (int): Index for file naming
    
    Returns:
        dict: Metadata about downloaded content
    """

    try:
        # Additional URL validation
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.warning(f"Invalid URL structure: {url}")
            return None
        
        
        # Custom headers to handle different content types
        headers = headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': parsed_url.scheme + '://' + parsed_url.netloc
        })
        
        # Download content with enhanced error handling
        response = requests.get(
            url, 
            headers=headers, 
            timeout=15, 
            allow_redirects=True,
            stream=True
        )
        
        # Raise exception for bad status codes
        response.raise_for_status()
        
        # Detect content type
        content_type = response.headers.get('Content-Type', '').lower()

        # Check if content is a redirect HTML response
        if 'html' in content_type:
            content = response.content
            soup = BeautifulSoup(content, 'html.parser')
            redirect_url = soup.find('meta', attrs={'http-equiv': 'refresh'})
            if redirect_url:
                url = redirect_url.get('content').split('URL=')[1]
                # Check if the redirected URL is to Twitter
                if 'twitter.com' in redirect_url:
                    logger.info(f"Redirect to Twitter detected for {url}, ignoring.")
                    return None
                else:
                    response = requests.get(
                        url, 
                        headers=headers, 
                        timeout=15, 
                        allow_redirects=True,
                        stream=True
                    )
                    response.raise_for_status()

            #detect url_type
            url_type = classify_url(url)

            content_type = response.headers.get('Content-Type', '').lower()
                # # Insert into media table
                # for media in tweet["media"]:
                #     supabase_client.table('media').insert({
                #         "media_id": str(uuid.uuid4()),
                #         "source_id": source_id,
                #         "media_url": media["original_url"],
                #         "media_type": media["type"],
                #         "created_at": datetime.now().isoformat()
                #     }).execute()

            # content_type = response.headers.get('Content-Type', '').lower()

            return {"original_url": url, "content":response.content,"content_type": content_type, "type": url_type['type'], "domain": url_type['domain'], "file_category": url_type['category']}
            
        else:
            url_type = classify_url(url)            # # Create a temporary file
            return {"original_url": url, "content":response.content,"content_type": content_type, "type": url_type['type'], "domain": url_type['domain'], "file_category": url_type['category']}
   
    except Exception as e:
        logger.warning(f"Error downloading URL content: {e}")
        return None

def get_media_links(url):
    """
    Extracts clean media links (images, videos, audio) from a web URL.

    :param url: The URL of the web page.
    :return: A list of dictionaries containing media type, original URL, and final URL.
    """
    try:
        # Fetch the web page content
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        soup = BeautifulSoup(response.text, 'html.parser')

        # Define patterns for media file extensions
        image_pattern = re.compile(r'\.(jpg|jpeg|png|gif|bmp|webp|svg)$', re.IGNORECASE)
        video_pattern = re.compile(r'\.(mp4|webm|ogg|mov|avi|mkv)$', re.IGNORECASE)
        audio_pattern = re.compile(r'\.(mp3|wav|ogg|flac|aac)$', re.IGNORECASE)

        # List to store media links
        media_links = []

        for tag in soup.find_all(['img', 'video', 'audio', 'source', 'a']):
            media_url = None
            media_type = None
            alt_text = None

            if tag.name == 'img' and tag.get('src'):
                media_url = tag['src']
                alt_text = tag.get('alt', '')
                if image_pattern.search(media_url) and not re.search(r'profile|avatar|logo', media_url, re.IGNORECASE):
                    media_type = 'image'
            elif tag.name == 'video' and tag.get('src'):
                media_url = tag['src']
                if video_pattern.search(media_url):
                    media_type = 'video'
            elif tag.name == 'audio' and tag.get('src'):
                media_url = tag['src']
                if audio_pattern.search(media_url):
                    media_type = 'audio'
            elif tag.name == 'source' and tag.get('src'):
                media_url = tag['src']
                if video_pattern.search(media_url):
                    media_type = 'video'
                elif audio_pattern.search(media_url):
                    media_type = 'audio'
            elif tag.name == 'a' and tag.get('href'):
                media_url = tag['href']
                if image_pattern.search(media_url) and not re.search(r'profile|avatar|logo', media_url, re.IGNORECASE):
                    media_type = 'image'
                elif video_pattern.search(media_url):
                    media_type = 'video'
                elif audio_pattern.search(media_url):
                    media_type = 'audio'

            if media_url and media_type:
                # Check if the URL is absolute
                parsed_url = urlparse(media_url)
                if parsed_url.scheme and parsed_url.netloc:
                    media_links.append({
                        'type': media_type,
                        'original_url': media_url,
                        'alt_text': alt_text
                    })

        # Remove duplicates
        unique_media_links = []
        seen_urls = set()
        for media in media_links:
            if media['original_url'] not in seen_urls:
                unique_media_links.append(media)
                seen_urls.add(media['original_url'])

        return unique_media_links

    except requests.exceptions.RequestException as e:
        print(f"Error fetching the URL: {e}")
        return None
    
def insert_content(supabase, processed_tweets):
    """
    Process a batch of tweets and save comprehensive metadata
    
    Args:
        processed_tweets (list): List of processed tweet metadata
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Function to get source_type_id by name
    def get_source_type_id(source_type_name):
        result = supabase.table('source_types').select('source_type_id').eq('name', source_type_name).execute()
        if result.data:
            return result.data[0]['source_type_id']
        else:
            raise ValueError(f"Source type '{source_type_name}' not found in source_types table.")


    # Insert data into Supabase tables
    try:
        # Get source_type_id for 'twitter'
        source_type_id = get_source_type_id('twitter')
        batch_id = str(uuid.uuid4())
        for tweet in processed_tweets:
            # Insert into sources table
            source_id = str(uuid.uuid4())
            supabase.table('sources').insert({
                "source_id": source_id,
                "source_type_id": source_type_id,  # Use source_type_id instead of type
                "source_identifier": tweet["tweet_id"],
                "batch_id": batch_id,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }).execute()

            # Insert into metadata table (full_text as metadata)
            supabase.table('source_metadata').insert({
                "metadata_id": str(uuid.uuid4()),
                "source_id": source_id,
                "key": "full_text",
                "value": tweet["full_text"],
                "created_at": datetime.now().isoformat()
            }).execute()

            # Insert into url_references table
            for url in tweet["urls"]:
                supabase.table('url_references').insert({
                    "url_reference_id": str(uuid.uuid4()),
                    "source_id": source_id,
                    "url": url["original_url"],
                    "type": url["type"],
                    "domain": url["domain"],
                    "content_type": url["content_type"],
                    "file_category": url["file_category"],
                    "created_at": datetime.now().isoformat()
                }).execute()

            # Insert into media table
            for media in tweet["media"]:
                supabase_client.table('media').insert({
                    "media_id": str(uuid.uuid4()),
                    "source_id": source_id,
                    "media_url": media["original_url"],
                    "media_type": media["type"],
                    "created_at": datetime.now().isoformat()
                }).execute()

        print("Data inserted successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")
