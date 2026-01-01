import json
import re
import logging
import pyshorteners

logger = logging.getLogger(__name__)


def clean_json_string(json_string):
    # Fix invalid backslashes by replacing single \ with double \\ (except valid escapes)
    json_string = re.sub(r'(?<!\\)\\(?![\"\\/bfnrt])', r'\\\\', json_string)
    return json_string

def safe_json_loads(json_string):
    try:
        json_string = clean_json_string(json_string)
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e}")
        return None


def shorten_link(url):
    try:
        s = pyshorteners.Shortener()
        shortened_url = s.tinyurl.short(url)
        return shortened_url
    except Exception as e:
        logger.error(f"Error shortening URL: {e}")
        return url