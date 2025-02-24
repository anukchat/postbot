from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID
from .db.datamodel import (
    Content, Source, Tag, URLReference, Media, ContentSource,
    # Response models
    ContentListItem, ContentListResponse,
    SourceListResponse, TemplateResponse,
    RedditResponse,
    ParameterResponse,
    ParameterValueResponse
)

def format_content_list_item(content: Any) -> ContentListItem:
    """Format a single content item from repository to API response format"""
    # Get content type
    content_type = content.content_type.name if hasattr(content, 'content_type') else None
    
    # Get source identifier from first content source
    source_identifier = next(
        (source.source_identifier
        for source in getattr(content, 'sources', [])
        if source and hasattr(source, 'source_identifier')),
        ""
    )
    
    # Format tags
    tags = [tag.name for tag in getattr(content, 'tags', []) 
            if hasattr(tag, 'name')]
    
    # Format URLs from source (only for blog content)
    urls = []
    if content_type == "blog":
        for source in getattr(content, 'sources', []):
            if hasattr(source, 'url_references'):
                urls.extend([{
                    "url": getattr(ref, 'url', ''),
                    "type": getattr(ref, 'type', None),
                    "domain": getattr(ref, 'domain', None)
                } for ref in source.url_references])
    
    # Format media from source (only for blog content)
    media = []
    if content_type == "blog":
        for source in getattr(content, 'sources', []):
            if hasattr(source, 'media'):
                media.extend([{
                    "url": getattr(m, 'media_url', ''),
                    "type": getattr(m, 'media_type', '')
                } for m in source.media])

    # Get source type
    source_type = next(
        (source.source_type.name
        for source in getattr(content, 'sources', [])
        if source and hasattr(source, 'source_type')),
        None
    )

    return ContentListItem(
        id=str(getattr(content, 'content_id', '')),
        thread_id=str(getattr(content, 'thread_id', '')),
        source_identifier=source_identifier,
        title=getattr(content, 'title', ''),
        content=getattr(content, 'body', ''),
        tags=tags,
        createdAt=str(getattr(content, 'created_at', datetime.now())),
        updatedAt=str(getattr(content, 'updated_at', datetime.now())),
        status=getattr(content, 'status', ''),
        twitter_post=getattr(content, 'body', '') if content_type == "twitter_post" else "",
        linkedin_post=getattr(content, 'body', '') if content_type == "linkedin_post" else "",
        urls=urls,
        media=media,
        source_type=source_type
    )

def format_content_list_response(
    items: List[Any], 
    total: int,
    page: int,
    size: int
) -> ContentListResponse:
    """Format content list response"""
    formatted_items = [format_content_list_item(item) for item in items]
    return ContentListResponse(
        items=formatted_items,
        total=total,
        page=page,
        size=size
    )

def format_source(source: Any) -> Dict[str, Any]:
    """Format a single source object"""
    return {
        "source_id": getattr(source, 'source_id', None),
        "source_identifier": getattr(source, 'source_identifier', None),
        "source_type": getattr(source.source_type, 'name', None) if hasattr(source, 'source_type') else None,
        "url_references": [
            {
                "url": getattr(ref, 'url', ''),
                "type": getattr(ref, 'type', None),
                "domain": getattr(ref, 'domain', None)
            }
            for ref in getattr(source, 'url_references', [])
        ],
        "media": [
            {
                "media_url": getattr(m, 'media_url', ''),
                "media_type": getattr(m, 'media_type', '')
            }
            for m in getattr(source, 'media', [])
        ],
        "created_at": getattr(source, 'created_at', datetime.now()),
        "updated_at": getattr(source, 'updated_at', datetime.now())
    }

def format_source_list_response(
    items: List[Any],
    total: int,
    page: int,
    size: int
) -> SourceListResponse:
    """Format source list response"""
    formatted_items = [format_source(item) for item in items]
    return SourceListResponse(
        items=formatted_items,
        total=total,
        page=page,
        size=size
    )

def format_template_parameter(parameter: Any) -> Dict[str, Any]:
    """Format a template parameter"""
    return {
        "parameter_id": getattr(parameter, 'parameter_id', None),
        "name": getattr(parameter, 'name', ''),
        "display_name": getattr(parameter, 'display_name', ''),
        "description": getattr(parameter, 'description', None),
        "is_required": getattr(parameter, 'is_required', True),
        "value": format_parameter_value(parameter.value) if hasattr(parameter, 'value') else None
    }

def format_parameter_value(value: Any) -> Dict[str, Any]:
    """Format a parameter value"""
    if not value:
        return None
    return {
        "value_id": getattr(value, 'value_id', None),
        "value": getattr(value, 'value', ''),
        "display_order": getattr(value, 'display_order', 0)
    }

def format_template_response(template: Any) -> TemplateResponse:
    """Format template response"""
    parameters = []
    if hasattr(template, 'parameters'):
        parameters = [format_template_parameter(param) for param in template.parameters]

    return TemplateResponse(
        template_id=getattr(template, 'template_id', None),
        name=getattr(template, 'name', ''),
        description=getattr(template, 'description', None),
        template_type=getattr(template, 'template_type', ''),
        template_image_url=getattr(template, 'template_image_url', None),
        parameters=parameters,
        created_at=getattr(template, 'created_at', datetime.now()),
        updated_at=getattr(template, 'updated_at', datetime.now())
    )

def format_parameter_response(parameter: Any) -> ParameterResponse:
    """Format parameter response"""
    values = []
    if hasattr(parameter, 'parameter_values'):
        values = [format_parameter_value_response(value) for value in parameter.parameter_values]

    return ParameterResponse(
        parameter_id=getattr(parameter, 'parameter_id', None),
        name=getattr(parameter, 'name', ''),
        display_name=getattr(parameter, 'display_name', ''),
        description=getattr(parameter, 'description', None),
        is_required=getattr(parameter, 'is_required', True),
        values=values,
        created_at=getattr(parameter, 'created_at', datetime.now()),
        updated_at=getattr(parameter, 'updated_at', datetime.now())
    )

def format_parameter_value_response(value: Any) -> ParameterValueResponse:
    """Format parameter value response"""
    return ParameterValueResponse(
        value_id=getattr(value, 'value_id', None),
        value=getattr(value, 'value', ''),
        display_order=getattr(value, 'display_order', 0),
        created_at=getattr(value, 'created_at', datetime.now())
    )

def format_reddit_response(data: Any, error: Optional[str] = None) -> RedditResponse:
    """Format Reddit API response"""
    return RedditResponse(
        data=data,
        status="error" if error else "success",
        error=error
    )