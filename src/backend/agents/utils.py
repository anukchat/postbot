import time
from typing import Dict, List, Tuple, Union
import urllib
from agents.state import Section
from extraction.docintelligence import DocumentExtractor
import requests
import re
import logging
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

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

def parse_query_response(self, response: str) -> Tuple[str, str]:
    query = ""
    time_range = "none"
    for line in response.strip().split('\n'):
        if ":" in line:
            key, value = line.split(":", 1)
            key = key.strip().lower()
            value = value.strip()
            if "query" in key:
                query = self.clean_query(value)
            elif "time" in key or "range" in key:
                time_range = self.validate_time_range(value)
    return query, time_range
    
def perform_search(query: str, time_range: str) -> List[Dict]:
    if not query:
        return []

    from duckduckgo_search import DDGS
    max_retries = 3
    base_delay = 2  # Base delay in seconds

    for retry in range(max_retries):
        try:
            # Add delay that increases with each retry
            if retry > 0:
                delay = base_delay * (2 ** (retry - 1))  # Exponential backoff
                print(f"Rate limit hit. Waiting {delay} seconds before retry {retry + 1}/{max_retries}...")
                time.sleep(delay)

            with DDGS() as ddgs:
                try:
                    if time_range and time_range != 'none':
                        results = list(ddgs.text(query, timelimit=time_range, max_results=10))
                    else:
                        results = list(ddgs.text(query, max_results=10))
                    
                    # If we get here, search was successful
                    return [{'number': i+1, **result} for i, result in enumerate(results)]
                        
                except Exception as e:
                    if 'Ratelimit' in str(e):
                        if retry == max_retries - 1:
                            print(f"Final rate limit attempt failed: {str(e)}")
                            return []
                        continue  # Try again with delay
                    else:
                        print(f"Search error: {str(e)}")
                        return []

        except Exception as e:
            print(f"Outer error: {str(e)}")
            return []

    print(f"All retry attempts failed for query: {query}")
    return []

def select_relevant_pages(self, search_results: List[Dict], user_query: str) -> List[str]:
    prompt = f"""
        Given the following search results for the user's question: "{user_query}"
        Select the 2 most relevant results to scrape and analyze. Explain your reasoning for each selection.

        Search Results:
        {self.format_results(search_results)}

        Instructions:
        1. You MUST select exactly 2 result numbers from the search results.
        2. Choose the results that are most likely to contain comprehensive and relevant information to answer the user's question.
        3. Provide a brief reason for each selection.

        You MUST respond using EXACTLY this format and nothing else:

        <numbers>[Two numbers corresponding to the selected results]</numbers>
        """
    response_text=""## llm response
    parsed_response = parse_page_selection_response(response_text)
    selected_urls = [result['href'] for result in search_results if result['number'] in parsed_response]

    return selected_urls

def extract_content( html, url):

    # Use Markdownit 
    soup = BeautifulSoup(html, 'html.parser')

    # Remove unwanted elements
    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    # Extract title
    title = soup.title.string if soup.title else ""

    # Try to find main content
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')

    if main_content:
        paragraphs = main_content.find_all('p')
    else:
        paragraphs = soup.find_all('p')

    # Extract text from paragraphs
    text = ' '.join([p.get_text().strip() for p in paragraphs])

    # If no paragraphs found, get all text
    if not text:
        text = soup.get_text()

    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    # Extract and resolve links
    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

    return {
        "url": url,
        "title": title,
        "content": text[:2400],  # Limit to first 2400 characters
        "links": links[:10]  # Limit to first 10 links
    }

def parse_page_selection_response(response: str) -> Dict[str, Union[List[int], str]]:
    # Extract numbers between <numbers> tags using regex
    numbers_match = re.search(r'<numbers>([^<]+)</numbers>', response)
    # parsed = {
    #     'selected_results': [],
    #     'reasoning': ''
    # }
    
    if numbers_match:
        # Convert matched numbers to integers
        numbers = [int(n.strip()) for n in numbers_match.group(1).split()]
        return numbers

    return []