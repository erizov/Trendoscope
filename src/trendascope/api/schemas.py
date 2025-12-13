"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PostGenerateRequest(BaseModel):
    """Request schema for post generation."""
    style: str = Field(default="philosophical", description="Post style")
    topic: str = Field(default="any", description="Topic focus")
    provider: str = Field(default="openai", description="LLM provider")
    model: Optional[str] = Field(default=None, description="Model name")
    quality: str = Field(default="standard", description="Quality tier")
    temperature: float = Field(default=0.8, ge=0.0, le=2.0, description="Temperature")
    translate: bool = Field(default=True, description="Translate news")


class PostSaveRequest(BaseModel):
    """Request schema for saving posts."""
    title: str = Field(..., min_length=1, max_length=500, description="Post title")
    text: str = Field(..., min_length=10, description="Post text")
    tags: List[str] = Field(default_factory=list, description="Post tags")
    style: Optional[str] = Field(default=None, description="Post style")
    topic: Optional[str] = Field(default=None, description="Post topic")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class PostUpdateRequest(BaseModel):
    """Request schema for updating posts."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    text: Optional[str] = Field(None, min_length=10)
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class NewsFeedRequest(BaseModel):
    """Request schema for news feed."""
    category: str = Field(default="all", description="Category filter")
    limit: int = Field(default=20, ge=5, le=100, description="Maximum items")
    translate: bool = Field(default=True, description="Translate to Russian")


class PostResponse(BaseModel):
    """Response schema for posts."""
    id: str
    title: str
    text: str
    tags: List[str]
    created_at: str
    updated_at: Optional[str] = None
    style: Optional[str] = None
    topic: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

