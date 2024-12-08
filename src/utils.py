import pandas as pd
import logging
import json
import ast
import urllib
import mimetypes

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

def detect_file_type(self, file_path=None, content=None, url=None, content_type=None):
        """
        Detect file type using multiple methods
        
        Args:
            file_path (str, optional): Path to the file
            content (bytes, optional): File content
            url (str, optional): URL of the content
            content_type (str, optional): HTTP content type header
        
        Returns:
            dict: Detected file type information
        """
        # Initialize type detection results
        file_type_info = {
            'mime_type': 'application/octet-stream',
            'extension': '.bin',
            'category': 'unknown'
        }

        try:
            # Prioritize different type detection methods
            
            # 1. HTTP Content-Type header
            if content_type:
                mime_type = content_type.split(';')[0].strip().lower()
                file_type_info['mime_type'] = mime_type
            
            # 2. Magic library MIME type detection
            if self.mime and content:
                try:
                    mime_type = self.mime.from_buffer(content)
                    if mime_type:
                        file_type_info['mime_type'] = mime_type
                except Exception as e:
                    logger.warning(f"MIME type detection error: {e}")
            
            # 3. URL-based detection
            if url:
                # Detect from URL extension
                parsed_url = urllib.parse.urlparse(url)
                url_path = parsed_url.path
                guessed_type, guessed_ext = mimetypes.guess_type(url_path)
                
                if guessed_type:
                    file_type_info['mime_type'] = guessed_type
                if guessed_ext:
                    file_type_info['extension'] = guessed_ext
            
            # 4. File path-based detection
            if file_path:
                guessed_type, guessed_ext = mimetypes.guess_type(file_path)
                if guessed_type:
                    file_type_info['mime_type'] = guessed_type
                if guessed_ext:
                    file_type_info['extension'] = guessed_ext
            
            # Categorize file types
            mime_type = file_type_info['mime_type']
            if 'image' in mime_type:
                file_type_info['category'] = 'image'
                file_type_info['extension'] = self._get_image_extension(mime_type)
            elif 'video' in mime_type:
                file_type_info['category'] = 'video'
                file_type_info['extension'] = self._get_video_extension(mime_type)
            elif 'audio' in mime_type:
                file_type_info['category'] = 'audio'
                file_type_info['extension'] = self._get_audio_extension(mime_type)
            elif 'text' in mime_type:
                file_type_info['category'] = 'text'
                file_type_info['extension'] = self._get_text_extension(mime_type)
            elif 'application/pdf' in mime_type:
                file_type_info['category'] = 'pdf'
                file_type_info['extension'] = '.pdf'
            
            return file_type_info
        
        except Exception as e:
            logger.warning(f"File type detection error: {e}")
            return file_type_info
