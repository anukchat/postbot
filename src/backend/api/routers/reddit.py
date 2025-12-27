

from typing import List, Dict, Optional
from fastapi import APIRouter, Query, Body, Depends
from src.backend.api.datamodel import RedditResponse, RedditSuggestionsResponse
from src.backend.extraction.extractors.reddit import RedditExtractor
from src.backend.api.dependencies import get_current_user_profile

router = APIRouter(tags=["Reddit"])

@router.get("/reddit/trending", response_model=RedditResponse)
async def get_trending_reddit_topics(
    limit: int = Query(10, description="Number of posts to fetch per subreddit"),
    subreddits: Optional[str] = Query(None, description="Comma-separated list of subreddits"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Fetch trending topics from specified subreddits or r/all"""
    try:
        reddit_extractor = RedditExtractor()
        subreddit_list = subreddits.split(',') if subreddits else None
        trending_data = reddit_extractor.get_trending_topics(
            limit=limit,
            subreddits=subreddit_list
        )
        return trending_data
    except Exception as e:
        return trending_data

@router.get("/reddit/discussions", response_model=RedditResponse)
async def get_trending_discussions(
    category: str = Query('all', description="Category/subreddit to fetch from"),
    timeframe: str = Query('day', description="Time period (hour, day, week, month, year, all)"),
    limit: int = Query(10, description="Number of posts to fetch"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Fetch trending discussion posts based on category and timeframe"""
    try:
        reddit_extractor = RedditExtractor()
        discussions = reddit_extractor.get_trending_discussions(
            category=category,
            timeframe=timeframe,
            limit=limit
        )
        
        return RedditResponse(
            data=discussions,
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

@router.get("/reddit/topic-suggestions", response_model=RedditSuggestionsResponse)
async def get_topic_suggetsions(
    limit: int = Query(15, description="Number of posts to fetch per subreddit"),
    subreddits: Optional[str] = Query(None, description="Comma-separated list of subreddits"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Get information about a specific subreddit"""
    try:
        reddit_extractor = RedditExtractor()
        subreddit_list = subreddits.split(',') if subreddits else None
        trending_data = reddit_extractor.get_trending_topics(
            limit=limit,
            subreddits=subreddit_list
        )
        
        topic_list=reddit_extractor.suggest_trending_titles(trending_data)

        return topic_list
    except Exception as e:
        # Return proper response structure on error
        return RedditSuggestionsResponse(
            category="error",
            content_ideas=[],
            trending_blogs=[],
            error=str(e)
        )

@router.get("/reddit/active-subreddits", response_model=RedditResponse)
async def get_active_subreddits(
    category: Optional[str] = Query(None, description="Category filter"),
    limit: int = Query(10, description="Number of subreddits to return"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Get most active subreddits for a given category"""
    try:
        reddit_extractor = RedditExtractor()
        active_subs = reddit_extractor.get_active_subreddits(
            category=category,
            limit=limit
        )
        
        return RedditResponse(
            data={"subreddits": active_subs},
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

@router.post("/reddit/extract", response_model=RedditResponse)
async def extract_reddit_content(
    url: str = Body(..., description="Reddit post URL to extract"),
    skip_llm: bool = Body(False, description="Skip LLM processing"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Extract content from a Reddit post URL"""
    try:
        reddit_extractor = RedditExtractor()
        content = reddit_extractor.extract(
            source=url,
            skip_llm=skip_llm
        )
        
        return RedditResponse(
            data=content,
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)

@router.post("/reddit/batch-summary", response_model=RedditResponse)
async def create_reddit_summary(
    posts: List[Dict] = Body(..., description="List of Reddit posts to summarize"),
    current_user: dict = Depends(get_current_user_profile)
):
    """Create a summary from multiple Reddit posts"""
    try:
        reddit_extractor = RedditExtractor()
        summary = reddit_extractor.create_summary(posts)
        
        return RedditResponse(
            data={"summary": summary},
            status="success"
        )
    except Exception as e:
        return RedditResponse(
            data={},
            status="error",
            error=str(e)
)
