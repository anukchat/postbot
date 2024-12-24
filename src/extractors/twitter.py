import os
import sys
import pandas as pd
import requests
import logging
import json
import re
import urllib.parse
from pathlib import Path
import hashlib
import ast
import mimetypes
import magic
import time
from bs4 import BeautifulSoup 
from utils import *
from db.sql import store_tweet_data

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

class TweetMetadataCollector:
    def __init__(self, output_base_dir='tweet_collection'):
        """
        Initialize the metadata collector
        
        Args:
            output_base_dir (str): Base directory for storing collected data
        """
        # Create base output directories
        self.base_dir = Path(output_base_dir)
        self.dirs= {
                # Code and Development Platforms
                'github': self.base_dir/'github',
                'github_code': self.base_dir/'github_code',
                'gitlab_code': self.base_dir/'gitlab',
                'bitbucket_code': self.base_dir/'bitbucket',                
                # Jupyter and Notebook Platforms
                'jupyter_notebook': self.base_dir/'jupyter_notebook',                
                # Document Types
                'pdf': self.base_dir/'pdf',
                'google_docs':self.base_dir/'google_docs',                
                # Media and Hosting Platforms
                'youtube': self.base_dir/'youtube',
                'vimeo': self.base_dir/'vimeo',                
                # Academic and Research
                'arxiv': self.base_dir/'arxiv',
                # Web Content
                'html': self.base_dir/'html',                
                # Social Media
                'tweet': self.base_dir/'tweet',
                'urls': self.base_dir / 'urls',
                'media': self.base_dir / 'media',
                'metadata': self.base_dir / 'metadata',
                'text': self.base_dir / 'text'
        }
        
        # Create directories
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Request headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Ensure magic library is available for MIME type detection
        try:
            self.mime = magic.Magic(mime=True)
        except Exception as e:
            logger.warning(f"Could not initialize MIME type detection: {e}")
            self.mime = None

    def preprocess_url(self, url):
        """
        Preprocess and validate URL before processing
        
        Args:
            url (str): Raw URL string
        
        Returns:
            str: Cleaned and validated URL, or None if invalid
        """
        if not isinstance(url, str):
            return None
        
        # # Remove newline and whitespace characters
        # url = url.replace('\n', '').replace('\r', '').strip()
        
        # Remove any trailing punctuation
        # url = url.rstrip('.,;:!?)]}')
        
        # Remove escape sequences
        url = url.replace('\\n', '').replace('\\r', '').replace('\\"', '').replace("\\'", '')
        
        # Remove newline and whitespace characters
        url = url.replace('\n', '').replace('\r', '').strip()

        # Ensure protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Decode URL-encoded characters
        try:
            url = urllib.parse.unquote(url)
        except Exception:
            logger.warning(f"Could not decode URL: {url}")
        
        # Validate URL structure
        try:
            parsed_url = urllib.parse.urlparse(url)
            
            # Check for valid scheme and netloc
            if not all([parsed_url.scheme, parsed_url.netloc]):
                logger.warning(f"Invalid URL structure: {url}")
                return None
            
            # Reconstruct URL to ensure proper formatting
            cleaned_url = urllib.parse.urlunparse((
                parsed_url.scheme,
                parsed_url.netloc,
                urllib.parse.quote(parsed_url.path),
                urllib.parse.quote(parsed_url.params),
                urllib.parse.quote(parsed_url.query, safe='=&'),
                parsed_url.fragment
            ))
            
            return cleaned_url
        
        except Exception as e:
            logger.warning(f"URL preprocessing error for {url}: {e}")
            return None

    def extract_urls(self, text):
        """
        Extract unique and expanded URLs from tweet text
        
        Args:
            text (str): Tweet text
        
        Returns:
            list: Unique, expanded URLs
        """
        if not isinstance(text, str):
            return []
        
        # Clean and normalize text
        cleaned_text = text.replace('\\n', ' ').replace('\r', ' ')
        
        # Comprehensive URL extraction patterns
        url_patterns = [
            # Standard HTTP/HTTPS URLs
            r'https?://[^\s<>"\']+',
            
            # URLs without protocol
            r'www\.[^\s<>"\']+',
            
            # Complex URL pattern with more robust matching
            r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/[^\s<>"\']*)?'
        ]
        
        # Combine and extract URLs
        urls = []
        for pattern in url_patterns:
            urls.extend(re.findall(pattern, cleaned_text))
        
        # Preprocess and filter URLs
        processed_urls = []
        seen_urls = set()
        
        for url in urls:
            # Preprocess URL
            processed_url = self.preprocess_url(url)
            
            # Expand non-Twitter URLs
            if processed_url:
                try:
                    # More robust URL expansion with timeout and error handling
                    response = requests.head(
                        processed_url, 
                        headers=self.headers, 
                        allow_redirects=True, 
                        timeout=5
                    )
                    expanded_url = response.url
                    processed_url = self.preprocess_url(expanded_url)
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Could not expand URL {processed_url}: {e}")
            
            # Add unique, valid non-Twitter URLs
            if processed_url and processed_url not in seen_urls:
                processed_urls.append(processed_url)
                seen_urls.add(processed_url)
        
        return processed_urls

    def _get_image_extension(self, mime_type):
        """Get appropriate image extension"""
        image_extensions = {
            'image/jpeg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'
        }
        return image_extensions.get(mime_type, '.jpg')

    def _get_video_extension(self, mime_type):
        """Get appropriate video extension"""
        video_extensions = {
            'video/mp4': '.mp4',
            'video/mpeg': '.mpeg',
            'video/quicktime': '.mov',
            'video/webm': '.webm'
        }
        return video_extensions.get(mime_type, '.mp4')

    def _get_audio_extension(self, mime_type):
        """Get appropriate audio extension"""
        audio_extensions = {
            'audio/mpeg': '.mp3',
            'audio/wav': '.wav',
            'audio/ogg': '.ogg',
            'audio/webm': '.webm'
        }
        return audio_extensions.get(mime_type, '.mp3')

    def _get_text_extension(self, mime_type):
        """Get appropriate text extension"""
        text_extensions = {
            'text/html': '.html',
            'text/plain': '.txt',
            'text/markdown': '.md',
            'application/json': '.json',
            'application/xml': '.xml'
        }
        return text_extensions.get(mime_type, '.txt')

    def download_url_content(self, url,tweet_id, index):
        """
        Download content from a URL with enhanced file type detection
        
        Args:
            url (str): URL to download
            index (int): Index for file naming
        
        Returns:
            dict: Metadata about downloaded content
        """
        # Validate URL before processing
        if not url:
            logger.warning(f"Empty URL at index {index}")
            return None
        
        try:
            # Additional URL validation
            parsed_url = urllib.parse.urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                logger.warning(f"Invalid URL structure: {url}")
                return None
            
            
            # Custom headers to handle different content types
            headers = self.headers.copy()
            headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': parsed_url.scheme + '://' + parsed_url.netloc
            })
            
            # Download content with enhanced error handling
            try:
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

                # Read content for type detection
                content = response.content
                # Check if content is a redirect HTML response
                if 'html' in content_type:
                    soup = BeautifulSoup(content, 'html.parser')
                    redirect_url = soup.find('meta', attrs={'http-equiv': 'refresh'})
                    if redirect_url:
                        redirect_url = redirect_url.get('content').split('URL=')[1]
                        # Check if the redirected URL is to Twitter
                        if 'twitter.com' in redirect_url:
                            logger.info(f"Redirect to Twitter detected for {url}, ignoring.")
                            return None
                    else:
                        logger.info(f"No reference to external content for {url}, ignoring.")
                        return None
                    
                # Initialize tweet_metadata if not already defined
                if 'tweet_metadata' not in locals():
                    tweet_metadata = {}

                url = redirect_url
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=15, 
                    allow_redirects=True,
                    stream=True
                )

                response.raise_for_status()

                #detect url_type
                url_type = self.classify_url(redirect_url)

                if url_type['category']=="code":
                    tweet_metadata['code_reference_url'] = redirect_url
                if url_type['category']=="repo":
                    content=response.content
                    tweet_metadata['content'] = content.decode('utf-8', errors='ignore')
                if url_type['category']=='document':
                    content = response.content
                    tweet_metadata['content'] = content.decode('utf-8', errors='ignore')
                if url_type['category']=='webpage' and not url_type['domain']=='github.com':
                    content = response.content
                    tweet_metadata['content'] = content.decode('utf-8', errors='ignore')

                content_type = response.headers.get('Content-Type', '').lower()


                                    # Detect file type
                # file_type = self.detect_file_type(url=redirect_url)
                if 'html' in content_type:
                    file_extension='.html'
                elif 'pdf' in content_type:
                    file_extension='.pdf'
                else:
                    file_extension='.txt'

                if not url_type['category']=='code':
                    
                    # Generate unique filename
                    url_hash = hashlib.md5(redirect_url.encode()).hexdigest()[:10]
                    filename = f"{url_type['type']}_{url_hash}_{index}{file_extension}"
                    # Determine save directory
                    save_dir = self.dirs.get(url_type['type'])
                    print(filename)
                    
                    # if file_extension==".pdf":
                    file_path_md = os.path.join(save_dir,"markdown",f"{url_type['type']}_{url_hash}_{index}.md")
                    # else:
                    #     file_path_md=""
                    
                    # # Determine save directory
                    # save_dir = self.dirs.get(url_type['type'])
                    # print(filename)

                    # Full file path
                    file_path = os.path.join(save_dir,filename)
                    
                    # Download strategy handling
                    if url_type['category'] in ['document','repo','webpage']:
                        # Save raw content for code repositories
                        with open(file_path, 'wb') as f:
                            f.write(content)
                    else:
                        pass
                else:
                    file_path=""
                    file_path_md=""
                
                return {
                    'tweet_id':tweet_id,
                    'index':index,
                    'original_url': url,
                    'downloaded_path': str(file_path),
                    'downloaded_path_md':str(file_path_md),
                    'type': url_type['type'],
                    'domain': url_type['domain'],
                    'content_type': file_extension,
                    'file_category': url_type['category'],
                    'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Download error for {url}: {e}")
                return None
        
        except Exception as e:
            logger.error(f"Unexpected error processing {url}: {e}")
            return None

    def process_media(self,tweet_id ,media_str):
        """
        Process media from tweet with robust parsing and handling
        
        Args:
            media_str (str): Media information from tweet
        
        Returns:
            list: Processed media metadata
        """
        # Safely parse media string
        media_list = safe_json_loads(media_str, [])
        
        processed_media = []
        for media in media_list:
            try:
                # Download media
                media_type = media.get('type', 'unknown')
                media_url =  media.get('original')
                
                if not media_url:
                    continue
                
                # Determine media storage strategy
                if 'twitter.com' in media_url or 't.co' in media_url or 'x.com' in media_url:
                    # Store as tweet image
                    media_dir = self.dirs['media'] / 'tweet_images'
                else:
                    # Store as reference media
                    media_dir = self.dirs['media'] / 'reference_media'
                
                # Create directory if it doesn't exist
                media_dir.mkdir(parents=True, exist_ok=True)
                
                # Generate unique filename
                media_hash = hashlib.md5(media_url.encode()).hexdigest()[:10]
                filename = f"{media_type}_{media_hash}"
                
                # Determine file extension
                ext = {
                    'video': '.mp4',
                    'image': '.jpg',
                    'photo': '.jpg'
                }.get(media_type, '.bin')
                
                # Full file path
                file_path = media_dir / f"{filename}{ext}"
                
                # Download media with redirect handling
                try:
                    # Initial request
                    response = requests.get(media_url, headers=self.headers, timeout=15, allow_redirects=True)
                    response.raise_for_status()
                    
                    # Check for redirects or content type
                    final_url = response.url
                    content_type = response.headers.get('Content-Type', '').lower()
                    
                    # Validate and save media
                    if response.status_code == 200 and ('image' in content_type or 'video' in content_type):
                        with open(file_path, 'wb') as f:
                            f.write(response.content)
                        
                        # Collect media metadata
                        processed_media.append({
                            'tweet_id':tweet_id,
                            'type': media_type,
                            'original_url': media_url,
                            'final_url': final_url,
                            'downloaded_path': str(file_path),
                            'content_type': content_type,
                            'thumbnail': media.get('thumbnail'),
                            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        })
                        
                        logger.info(f"Successfully downloaded media: {file_path}")
                    else:
                        logger.warning(f"Invalid media content from {media_url}")
                
                except requests.RequestException as e:
                    logger.error(f"Error downloading media {media_url}: {e}")
            
            except Exception as e:
                logger.error(f"Unexpected error processing media {media}: {e}")
        
        return processed_media

    def process_media_without_saving(self, tweet_id,media_str):

         # Safely parse media string
        media_list = safe_json_loads(media_str, [])
        
        processed_media = []
        for media in media_list:
            try:
                # Download media
                media_type = media.get('type', 'unknown')
                media_url =  media.get('original')
                
                if not media_url:
                    continue

                processed_media.append({
                            'tweet_id':tweet_id,
                            'type': media_type,
                            'original_url': media_url,
                            'final_url': media_url,
                            'downloaded_path': '',
                            'content_type': '',
                            'thumbnail': media.get('thumbnail'),
                            'downloaded_at': time.strftime('%Y-%m-%d %H:%M:%S')
                        })

            except Exception as e:
                logger.error(f"Unexpected error processing media {media}: {e}")

        return processed_media
        
    def extract_tweet_metadata(self, tweet_row):
        """
        Extract comprehensive metadata from a tweet
        
        Args:
            tweet_row (pd.Series): Single tweet row
        
        Returns:
            dict: Comprehensive tweet metadata
        """
        # Core Tweet Metadata
        tweet_metadata = {
            # Basic Tweet Information
            'tweet_id': str(tweet_row['id']),
            'created_at': tweet_row['created_at'],
            'full_text': tweet_row['full_text'],
            'language': tweet_row.get('lang', 'unknown'),
            
            # Engagement Metrics
            'favorite_count': int(tweet_row['favorite_count']),
            'retweet_count': int(tweet_row['retweet_count']),
            'bookmark_count': int(tweet_row['bookmark_count']),
            'quote_count': int(tweet_row['quote_count']),
            'reply_count': int(tweet_row['reply_count']),
            'views_count': int(tweet_row['views_count']),
            
            # User Information
            'screen_name': tweet_row['screen_name'],
            'user_name': tweet_row['name'],
            'profile_image_url': tweet_row['profile_image_url'],
            
            # Content Extraction Targets
            'urls': [],
            'media': [],
            
            # Additional Metadata
            'is_retweet': tweet_row.get('retweeted', False),
            'is_quote': tweet_row.get('is_quote_status', False),
            'possibly_sensitive': tweet_row.get('possibly_sensitive', False)
        }
        
        # Extract and process URLs
        urls = self.extract_urls(tweet_row['full_text'])
        tweet_metadata['urls'] = [
            self.download_url_content(url, str(tweet_row['id']),index) 
            for index, url in enumerate(urls)
            if self.download_url_content(url,str(tweet_row['id']), index)
        ]
        
        # Process Media
        # tweet_metadata['media'] = self.process_media(str(tweet_row['id']),tweet_row['media'])
        tweet_metadata['media']=self.process_media_without_saving(str(tweet_row['id']),tweet_row['media'])
        
        return tweet_metadata

    def process_tweet_collection(self, tweets_df):
        """
        Process entire tweet collection and generate comprehensive metadata
        
        Args:
            tweets_df (pd.DataFrame): DataFrame of tweets
        
        Returns:
            list: List of processed tweet metadata
        """
        processed_tweets = []
        
        for _, tweet_row in tweets_df.iterrows():
            try:
                tweet_metadata = self.extract_tweet_metadata(tweet_row)
                processed_tweets.append(tweet_metadata)
                
                logger.info(f"Processed tweet: {tweet_metadata['tweet_id']}")
                # Optional: Save individual tweet metadata
                # tweet_metadata_path = self.dirs['metadata'] / f"{tweet_metadata['tweet_id']}_metadata.json"
                # with open(tweet_metadata_path, 'w') as f:
                #     json.dump(tweet_metadata, f, indent=2)
            
            except Exception as e:
                logger.error(f"Error processing tweet {tweet_row['id']}: {e}")
        
        # Save comprehensive metadata
        logger.info("Saving metadata file")
        comprehensive_metadata_path = self.dirs['metadata'] / 'comprehensive_metadata.json'
        # Convert Timestamp objects to string format
        for tweet in processed_tweets:
            if 'created_at' in tweet and isinstance(tweet['created_at'], pd.Timestamp):
                tweet['created_at'] = tweet['created_at'].isoformat()  # Convert to ISO format
        
        store_tweet_data(processed_tweets)

        # Save the processed tweets to database from sql.py
        with open(comprehensive_metadata_path, 'w') as f:
            json.dump(processed_tweets, f, indent=2)
        
        return processed_tweets

    def classify_url(self, url):
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
