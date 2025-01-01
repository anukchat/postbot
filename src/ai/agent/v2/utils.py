

from ai.agent.v2.state import Section


def get_reference_content(tweet):
        
    reference_content=""
    reference_link=""
    media_markdown = ""
    # Process URLs
    for url in tweet["urls"]:
        if url["file_category"] in ["document", "repo", "webpage"]:
            # Read markdown/PDF content
            with open(url["downloaded_path_md"], "r") as f:
                reference_content += f.read()
            reference_link += url["original_url"]
        else:
            pass                
    # media_markdown = ""
    if tweet.get("media"):
        for media in tweet["media"]:
            if media["type"] == "photo":
                media_markdown += f"![]({media['original_url']})\n\n"
            if media["type"] == "video":
                media_markdown += (
                    f"<video src=\"{media['final_url']}\" controls/>\n\n"
                )
    
    return reference_content, reference_link, media_markdown
        
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