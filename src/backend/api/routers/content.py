from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.backend.api.datamodel import BlogResponse, Content, ContentUpdate, ContentListResponse, ContentListItem, SaveContentRequest, ScheduleContentRequest, GeneratePostRequestModel
from src.backend.db.repositories import ContentRepository, ProfileRepository, ContentTypeRepository, TemplateRepository
from src.backend.api.dependencies import get_current_user_profile, get_workflow
from uuid import UUID
import json
import uuid
from typing import Dict, Any, Optional
from fastapi import Query
from src.backend.agents.blogs import AgentWorkflow
from src.backend.utils.logger import setup_logger
from src.backend.api.formatters import format_content_list_response, format_content_list_item
from fastapi.responses import StreamingResponse

logger = setup_logger(__name__)

router = APIRouter(tags=["Content"])

# Repositories
content_repository = ContentRepository()
profile_repository = ProfileRepository()
content_type_repository = ContentTypeRepository()
template_repository = TemplateRepository()


# Update content endpoints to use profile_id
@router.post("/content", response_model=Content)
async def create_content(
    content_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        content_data["profile_id"] = current_user.profile_id
        return content_repository.create(content_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

#TODO: Define response model for generate
@router.post("/content/generate", response_model=BlogResponse)
async def generate_generic_blog(
    payload: GeneratePostRequestModel,
    workflow: AgentWorkflow = Depends(get_workflow),
    current_user: dict = Depends(get_current_user_profile),
):
    """Initiate the workflow with the provided data."""
    try:
        thread_id = payload.thread_id or str(uuid.uuid4())
        # Get template and parameters if template_id is provided
        payload_dict = payload.model_dump()

        if payload.template_id:
            template_data=template_repository.get_template_with_parameters(UUID(payload.template_id), UUID(current_user.profile_id))
            payload_dict["template"] = template_data
            # payload = GeneratePostRequestModel(**payload_dict)
        # Check generation limit        
        limit_response = await check_generation_limit(current_user.profile_id)
        logger.info(f"Generation limit check: {limit_response}")
        
        if limit_response['generations_used'] >= limit_response['max_generations']:
            logger.warning(f"Generation limit reached for user {current_user['id']}")
            raise HTTPException(status_code=403, detail="Generation limit reached for this thread")

        # Proceed with generation
        logger.debug("Starting workflow execution")
        result = workflow.run_generic_workflow(payload_dict, thread_id, current_user)
        logger.debug("Workflow execution completed")

        # Increment generation count
        await increment_generation_count(current_user.profile_id)

        return result
    except HTTPException as e:
        logger.error(f"HTTP Exception in generate_generic_blog: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in generate_generic_blog: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

async def check_generation_limit(profile_id: UUID) -> Dict:
    """Check the generation limit for a specific profile."""
    profile_data = profile_repository.get_with_generation_limits(profile_id)
    if not profile_data:
        raise HTTPException(status_code=404, detail="Profile not found")

    return {
        "tier": profile_data["role"],
        "max_generations": profile_data["generation_limit"],
        "generations_used": profile_data["generations_used"]
    }

async def increment_generation_count(profile_id: UUID):
    """Increment the generation count for a profile."""
    try:
        success = profile_repository.increment_generation_count(profile_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to increment generation count")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to increment generation count: {str(e)}")    

@router.post("/content/generate/stream", response_class=StreamingResponse)
async def stream_generic_blog(
    payload: GeneratePostRequestModel,
    workflow: AgentWorkflow = Depends(get_workflow),
    current_user: dict = Depends(get_current_user_profile),
):
    """Stream workflow execution in real-time"""
    try:
        thread_id = payload.thread_id or str(uuid.uuid4())
        payload_dict = payload.model_dump()
        
        if payload.template_id:
            template_data = template_repository.get_template_with_parameters(UUID(payload.template_id), UUID(current_user.profile_id))
            payload_dict["template"] = template_data

        # Check generation limit
        limit_response = await check_generation_limit(current_user.profile_id)
        if limit_response['generations_used'] >= limit_response['max_generations']:
            raise HTTPException(status_code=403, detail="Generation limit reached")

        # Return streaming response
        return StreamingResponse(
            workflow.stream_generic_workflow(payload_dict, thread_id, current_user),
            media_type="text/event-stream",
            headers={
                "Content-Disposition": f"attachment; filename={thread_id}.stream",
                "X-Thread-ID": thread_id
            }
        )
    except HTTPException as e:
        logger.error(f"HTTP Exception in stream_generic_blog: {str(e)}")
        raise e
    except Exception as e:
        logger.error(f"Unexpected error in stream_generic_blog: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/content/filter", response_model=ContentListResponse)
async def filter_content(
    skip: int = 0,
    limit: int = 10,
    filters: str = Query(None, description="JSON string containing filters"),
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        # Parse the JSON string filters into a dictionary
        filter_dict = {}
        if filters:
            try:
                filter_dict = json.loads(filters)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse filters JSON: {filters}")
                filter_dict = {}

        result = content_repository.filter_content(UUID(current_user.profile_id), filter_dict, skip, limit)
        return format_content_list_response(
            items=result["items"],
            total=result["total"],
            page=result["page"],
            size=result["size"]
        )
    except Exception as e:
        logger.error(f"Error in filter_content: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/content/{content_id}", response_model=ContentListItem)
async def get_content(
    content_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        content = content_repository.find_by_field("content_id", content_id)
        if not content or str(content.profile_id) != current_user.profile_id:
            raise HTTPException(status_code=404, detail="Content not found")
        return format_content_list_item(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/content/{content_id}", response_model=Content) 
async def update_content(content_id: UUID, content: ContentUpdate, current_user: dict = Depends(get_current_user_profile)):
    """Update content"""
    result = content_repository.update(
        id_field="content_id",
        id_value=content_id,
        data=content.dict(exclude_unset=True)
    )
    if not result:
        raise HTTPException(status_code=404, detail="Content not found")
    if result["profile_id"] != str(current_user.profile_id):
        raise HTTPException(status_code=403, detail="Not authorized to update this content")
    return result

@router.delete("/content/thread/{thread_id}")
async def delete_thread_content(
    thread_id: UUID,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        # Delete all content associated with thread
        content = content_repository.filter({"thread_id": thread_id})
        if not content or str(content[0].profile_id) != current_user.profile_id:
            raise HTTPException(status_code=404, detail="Content not found")
        return content_repository.batch_delete("thread_id", [thread_id])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/content/thread/{thread_id}", response_model=ContentListItem) 
async def get_content_by_thread(
    thread_id: UUID,
    post_type: Optional[str] = Query(None, description="Filter by post type (blog, twitter, linkedin)"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Get content by thread ID with optional post type filter"""
    try:
        # Get content type ID if post_type is provided
        content_type_id = None
        if post_type:
            type_id = content_type_repository.get_content_type_id_by_name(post_type)
            if not type_id:
                raise HTTPException(status_code=400, detail=f"Invalid post type: {post_type}")
            content_type_id = type_id

        result = content_repository.get_content_by_thread(thread_id, UUID(current_user.profile_id), content_type_id)

        if not result:
            return ContentListItem(
                id="",
                thread_id=str(thread_id),
                title="",
                content="",
                tags=[],
                createdAt=datetime.now().isoformat(),
                updatedAt=datetime.now().isoformat(),
                status="",
                twitter_post="",
                linkedin_post="",
                urls=[],
                media=[],
                source_type=None
            )

        return format_content_list_item(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/content/thread/{thread_id}/save", response_model=ContentListItem)
async def save_content(
    thread_id: UUID,
    content: SaveContentRequest,
    current_user: Dict = Depends(get_current_user_profile)
):
    try:
        result = content_repository.update_by_thread(
            thread_id,
            UUID(current_user.profile_id),
            content.dict(exclude_unset=True)
        )
        if not result:
            raise HTTPException(status_code=404, detail="Content not found")
        return format_content_list_item(result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/content/thread/{thread_id}/schedule")
async def schedule_thread_content(
    thread_id: UUID, 
    payload: ScheduleContentRequest,
    current_user: Dict = Depends(get_current_user_profile)
):
    """Schedule content for publishing"""
    try:
        content_type_id = content_type_repository.get_content_type_id_by_name(f"{payload.platform}_post")
        if not content_type_id:
            raise HTTPException(status_code=400, detail=f"Invalid platform: {payload.platform}")

        content_data = {
            "status": payload.status,
            "scheduled_at": payload.schedule_date
        }

        result = content_repository.update(
            id_field="thread_id",
            id_value=thread_id,
            data=content_data
        )

        if not result:
            raise HTTPException(status_code=404, detail="Content not found")

        return {"message": "Content scheduled successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
