import time
from typing import Dict, List, Tuple, Union
import urllib
from src.backend.agents.state import Section
from src.backend.extraction.docintelligence import DocumentExtractor
import requests
import re
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
import re

from src.backend.extraction.factory import ConverterRegistry, ExtracterRegistry

logger = logging.getLogger(__name__)
extractor = DocumentExtractor()
extractor_factory = ExtracterRegistry()
converter_factory= ConverterRegistry()


pdf_extractor = extractor_factory.get_extractor('pdf', 'default')

def process_url_content(url_meta):
    """Helper to process URL content based on type"""
    # url_meta = utils.get_url_metadata(url)
    
    if url_meta['type'] == "html":
        return extractor.extract_html(html_content=url_meta["content"])
    elif url_meta['type'] == "pdf":
        return extractor.extract_pdf(input_file=url_meta['url'])
    elif url_meta['type'] == "arxiv":
        return extractor.extract_arxiv_pdf(url_meta['url'])
    elif url_meta['type'] == "github":
        return extractor.extract_github_readme(url_meta['url'])
    else:
        return url_meta["content"]

def get_tweet_reference_content(tweet_urls):
        
    reference_content=""
    reference_link=""
    media_markdown = ""
    # Process URLs
    if tweet_urls:
        for url in tweet_urls:
            if url["type"]=="html":
                response = requests.get(url['url'])
                if response.status_code == 200:
                    url['content'] = response.text
                else:
                    url['content'] = "" 
            else:    
                url['content'] = ""
                
            reference_content += process_url_content(url)
            reference_link += url["url"]
            
        reference_content += process_url_content(url)
        reference_link += url["url"]

    return reference_content, reference_link

def get_tweet_media(media_list):
    media_markdown = ""
    if media_list:
        for media in media_list:
            if media["media_type"] in ["photo","image"]:
                media_markdown += f"![]({media['media_url']})\n\n"
            if media["media_type"] == "video":
                media_markdown += (
                    f"<video src=\"{media['media_url']}\" controls/>\n\n"
                )
    return media_markdown

def get_media_content_url(media_meta):
    
    # reference_content=""
    media_markdown = ""      
    # media_markdown = ""
    if media_meta:
        for media in media_meta:
            if media["type"] in ["photo","image"]:
                media_markdown += f"![{media['alt_text']}]({media['original_url']})\n\n"
            if media["type"] == "video":
                media_markdown += (
                    f"<video src=\"{media['original_url']}\" controls/>\n\n"
                )
    
    return media_markdown

def format_sections(sections: list[Section]) -> str:
    """ Format a list of sections into a string """
    formatted_str = ""
    for idx, section in enumerate(sections, 1):
        formatted_str += f"""
        {'='*60}
        Section {idx}: {section.name}
        {'='*60}
        Description:
        {section.description}
        Main body: 
        {section.main_body}
        Content:
        {section.content if section.content else '[Not yet written]'}
        """
    return formatted_str

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
            # Document Types
            'pdf': {
                'condition': path.endswith('.pdf'),
                'category': 'document'
            },
                        # Academic and Research
            'arxiv': {
                'condition': 'arxiv.org' in domain,
                'category': 'document'
            },    
            # Social Media
            'tweet': {
                'condition': ('twitter.com' in domain or 'x.com' in domain) and '/status/' in path,
                'category': 'metadata'
            },
            'reddit': {
                'condition': 'reddit.com' in domain,
                'category': 'metadata'
            },
            
            # Web Content
            'html': {
                'condition': path.endswith('.html') or not path.endswith(('.pdf', '.ipynb')),
                'category': 'webpage'
            },
            'github': {
                'condition': 'github.com' in domain and ('/blob/' not in path or '/tree/' not in path or '/trending' not in path or '/explore' not in path or '/topics' not in path),   
                'category': 'repo'
            },
            'github_code': {
                'condition': 'github.com' in domain and ('/blob/' in path or '/tree/' in path),
                'category': 'code'
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
        # headers = headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        # }
        # headers.update({
        #     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        #     'Accept-Language': 'en-US,en;q=0.5',
        #     'Referer': parsed_url.scheme + '://' + parsed_url.netloc
        # })
        
        # # Download content with enhanced error handling
        # response = requests.get(
        #     url, 
        #     headers=headers, 
        #     timeout=15, 
        #     allow_redirects=True,
        #     stream=True
        # )
        
        # Raise exception for bad status codes
        # response.raise_for_status()
        
        # Detect content type
        # content_type = response.headers.get('Content-Type', '').lower()

        # Check if content is a redirect HTML response
        # if 'html' in content_type:
        #     content = response.content
        #     soup = BeautifulSoup(content, 'html.parser')
        #     redirect_url = soup.find('meta', attrs={'http-equiv': 'refresh'})
        #     if redirect_url:
        #         url = redirect_url.get('content').split('URL=')[1]
        #         # Check if the redirected URL is to Twitter
        #         if 'twitter.com' in redirect_url:
        #             logger.info(f"Redirect to Twitter detected for {url}, ignoring.")
        #             return None
        #         else:
        #             response = requests.get(
        #                 url, 
        #                 headers=headers, 
        #                 timeout=15, 
        #                 allow_redirects=True,
        #                 stream=True
        #             )
        #             response.raise_for_status()

        #     #detect url_type
        #     url_type = classify_url(url)

        #     content_type = response.headers.get('Content-Type', '').lower()
        #         # # Insert into media table
        #         # for media in tweet["media"]:
        #         #     supabase_client.table('media').insert({
        #         #         "media_id": str(uuid.uuid4()),
        #         #         "source_id": source_id,
        #         #         "media_url": media["original_url"],
        #         #         "media_type": media["type"],
        #         #         "created_at": datetime.now().isoformat()
        #         #     }).execute()

        #     # content_type = response.headers.get('Content-Type', '').lower()

        #     return {"original_url": url, "content":response.content,"content_type": content_type, "type": url_type['type'], "domain": url_type['domain'], "file_category": url_type['category']}
            
        # else:
        url_type = classify_url(url)            # # Create a temporary file
        return {"original_url": url, "content_type": url_type['type'], "type": url_type['type'], "domain": url_type['domain'], "file_category": url_type['category']}
   
    except Exception as e:
        logger.warning(f"Error downloading URL content: {e}")
        return None

# def clean_json_string(json_string):
#     # Fix invalid backslashes by replacing single \ with double \\ (except valid escapes)
#     json_string = re.sub(r'(?<!\\)\\(?![\"\\/bfnrt])', r'\\\\', json_string)
#     return json_string

# def safe_json_loads(json_string):
#     try:
#         json_string = clean_json_string(json_string)
#         return json.loads(json_string)
#     except json.JSONDecodeError as e:
#         print("JSON Decode Error:", e)
#         return None