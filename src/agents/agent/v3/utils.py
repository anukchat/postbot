

from src.agents.state import Section
from src.extractors.docintelligence import DocumentExtractor
import requests

extractor = DocumentExtractor()

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