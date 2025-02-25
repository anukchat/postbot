from typing import Dict, List, Any, Optional
from datetime import datetime
from uuid import UUID
from .db.connection import DatabaseConnectionManager
from .db.datamodel import (
    Content, Source, Tag, URLReference, Media, ContentSource,
    ContentListItem, ContentListResponse,
    SourceListResponse, TemplateResponse,
    RedditResponse,
    ParameterResponse,
    ParameterValueResponse
)

db = DatabaseConnectionManager()

def format_content_list_item(content: Any) -> ContentListItem:
    """Format a single content item from repository to API response format"""
    session = db.get_session()
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
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e

def format_content_list_response(items: List[Any], total: int, page: int, size: int) -> ContentListResponse:
    """Format content list response"""
    session = db.get_session()
    try:
        formatted_items = [format_content_list_item(item) for item in items]
        session.commit()
        return ContentListResponse(
            items=formatted_items,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        session.rollback()
        raise e

def format_source(source: Any) -> Dict[str, Any]:
    """Format a single source object"""
    session = db.get_session()
    try:
        result = {
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
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e

def format_source_list_response(items: List[Any], total: int, page: int, size: int) -> SourceListResponse:
    """Format source list response"""
    session = db.get_session()
    try:
        formatted_items = [format_source(item) for item in items]
        session.commit()
        return SourceListResponse(
            items=formatted_items,
            total=total,
            page=page,
            size=size
        )
    except Exception as e:
        session.rollback()
        raise e

def format_template_parameter(parameter: Any) -> Dict[str, Any]:
    """Format a template parameter"""
    session = db.get_session()
    try:
        result = {
            "parameter_id": getattr(parameter, 'parameter_id', None),
            "name": getattr(parameter, 'name', ''),
            "display_name": getattr(parameter, 'display_name', ''),
            "description": getattr(parameter, 'description', None),
            "is_required": getattr(parameter, 'is_required', True),
            "value": format_parameter_value(parameter.value) if hasattr(parameter, 'value') else None
        }
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e

def format_parameter_value(value: Any) -> Dict[str, Any]:
    """Format a parameter value"""
    if not value:
        return None
    session = db.get_session()
    try:
        result = {
            "value_id": getattr(value, 'value_id', None),
            "value": getattr(value, 'value', ''),
            "display_order": getattr(value, 'display_order', 0)
        }
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e

def format_template_response(template: Any) -> TemplateResponse:
    """Format template response"""
    session = db.get_session()
    try:
        parameters = []
        if hasattr(template, 'parameters'):
            parameters = [format_template_parameter(param) for param in template.parameters]

        result = TemplateResponse(
            template_id=getattr(template, 'template_id', None),
            name=getattr(template, 'name', ''),
            description=getattr(template, 'description', None),
            template_type=getattr(template, 'template_type', ''),
            template_image_url=getattr(template, 'template_image_url', None),
            parameters=parameters,
            created_at=getattr(template, 'created_at', datetime.now()),
            updated_at=getattr(template, 'updated_at', datetime.now())
        )
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e

def format_parameter_response(parameter: Any) -> ParameterResponse:
    """Format parameter response"""
    session = db.get_session()
    try:
        values = []
        if hasattr(parameter, 'parameter_values'):
            values = [(value) for value in parameter.parameter_values]

        result = ParameterResponse(
            parameter_id=getattr(parameter, 'parameter_id', None),
            name=getattr(parameter, 'name', ''),
            display_name=getattr(parameter, 'display_name', ''),
            description=getattr(parameter, 'description', None),
            is_required=getattr(parameter, 'is_required', True),
            values=values,
            created_at=getattr(parameter, 'created_at', datetime.now()),
            updated_at=getattr(parameter, 'updated_at', datetime.now())
        )
        session.commit()
        return result
    except Exception as e:
        session.rollback()
        raise e