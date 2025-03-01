from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID
from ..db.connection import DatabaseConnectionManager
from .datamodel import (
    Content, Source, Tag, TemplateParameter, TemplateParameterValue, URLReference, Media, ContentSource,
    ContentListItem, ContentListResponse,
    SourceListResponse, TemplateResponse,
    RedditResponse
)

db = DatabaseConnectionManager()

def format_content_list_item(content: Any) -> ContentListItem:
    """Format a single content item from repository to API response format"""
   
    try:
        # Get content type
        content_type = content.content_type.name if hasattr(content, 'content_type') else None
        
        # Format data
        result = ContentListItem(
            id=str(getattr(content, 'content_id', '')),
            thread_id=str(getattr(content, 'thread_id', '')),
            source_identifier=next(
                (source.source_identifier
                for source in getattr(content, 'sources', [])
                if source and hasattr(source, 'source_identifier')),
                ""
            ),
            title=getattr(content, 'title', ''),
            content=getattr(content, 'body', ''),
            tags=[tag.name for tag in getattr(content, 'tags', []) if hasattr(tag, 'name')],
            createdAt=str(getattr(content, 'created_at', datetime.now())),
            updatedAt=str(getattr(content, 'updated_at', datetime.now())),
            status=getattr(content, 'status', ''),
            twitter_post=getattr(content, 'body', '') if content_type == "twitter_post" else "",
            linkedin_post=getattr(content, 'body', '') if content_type == "linkedin_post" else "",
            urls=[],
            media=[],
            source_type=next(
                (source.source_type.name
                for source in getattr(content, 'sources', [])
                if source and hasattr(source, 'source_type')),
                None
            )
        )
        
        return result
    except Exception as e:
        
        raise e

def format_content_list_response(items: List[Any], total: int, page: int, size: int) -> ContentListResponse:
    """Format content list response"""
   
    try:
        formatted_items = [format_content_list_item(item) for item in items]
        
        return ContentListResponse(
            items=formatted_items,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        
        raise e

def format_source(source: Any) -> Dict[str, Any]:
    """Format a single source object"""
   
    try:
        result = {
            "source_id": getattr(source, 'source_id', ''),
            "source_identifier": getattr(source, 'source_identifier', ''),
            "source_type": getattr(source.source_type, 'name', '') if hasattr(source, 'source_type') else '',
            "url_references": [
                {
                    "url": getattr(ref, 'url', ''),
                    "type": getattr(ref, 'type', ''),
                    "domain": getattr(ref, 'domain', '')
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
        
        return result
    except Exception as e:
        
        raise e

def format_source_list_response(items: List[Any], total: int, page: int, size: int) -> SourceListResponse:
    """Format source list response"""
   
    try:
        formatted_items = [format_source(item) for item in items]
        
        return SourceListResponse(
            items=formatted_items,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        
        raise e

def format_template_parameter(parameter: Any) -> Dict[str, Any]:
    """Format a template parameter"""
    try:
        # Create a valid TemplateParaßmeterValue instance if value exists
        parameter_values = []
        if hasattr(parameter, 'values'):
            parameter_values = [format_parameter_value(value) for value in parameter.values]

        result = TemplateParameter(
            parameter_id=getattr(parameter, 'parameter_id', ''),
            name=getattr(parameter, 'name', ''),
            display_name=getattr(parameter, 'display_name', ''),
            description=getattr(parameter, 'description', ''),
            is_required=getattr(parameter, 'is_required', True),
            created_at=getattr(parameter, 'created_at', datetime.now()),
            values=parameter_values  # This will be None if no value exists
        )
        return result
    except Exception as e:
        raise e

def format_parameter_value(value: Any) -> Dict[str, Any]:
    """Format a parameter value"""
    if not value:
        return None

    try:
        result = TemplateParameterValue(
            value_id=getattr(value, 'value_id', None),
            value=getattr(value, 'value', ''),
            display_order=getattr(value, 'display_order', 0),
            created_at=getattr(value, 'created_at', datetime.now())
        )

        return result
    except Exception as e:
        raise e

def format_template_response(template: Any) -> TemplateResponse:
    """Format template response"""
    try:
        parameters = []
        if hasattr(template, 'parameters'):
            parameters = [format_template_parameter(param) for param in template.parameters]
            # Filter out any None values
            parameters = [p for p in parameters if p is not None]

        result = TemplateResponse(
            template_id=getattr(template, 'template_id', None),
            name=getattr(template, 'name', ''),
            description=getattr(template, 'description', ""),
            template_type=getattr(template, 'template_type', ''),
            template_image_url=getattr(template, 'template_image_url', ""),
            parameters=parameters,
            created_at=getattr(template, 'created_at', datetime.now()),
            updated_at=getattr(template, 'updated_at', datetime.now())
        )
        return result
    except Exception as e:
        raise e

def format_parameter_response(parameter: Any) -> TemplateParameter:
    """Format parameter response"""
   
    try:
        values = []
        if hasattr(parameter, 'parameter_values'):
            values = [(value) for value in parameter.parameter_values]

        result = TemplateParameter(
            parameter_id=getattr(parameter, 'parameter_id', ''),
            name=getattr(parameter, 'name', ''),
            display_name=getattr(parameter, 'display_name', ''),
            description=getattr(parameter, 'description', ''),
            is_required=getattr(parameter, 'is_required', True),
            values=values,
            created_at=getattr(parameter, 'created_at', datetime.now()),
        )
        
        return result
    except Exception as e:
        
        raise e