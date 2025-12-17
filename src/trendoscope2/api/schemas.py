"""
Pydantic schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator, HttpUrl, EmailStr
from typing import Dict, Any, Optional, Literal


class TranslateArticleRequest(BaseModel):
    """Request model for article translation."""
    title: Optional[str] = Field(default="", description="Article title")
    summary: Optional[str] = Field(default="", description="Article summary")
    source_language: Optional[str] = Field(
        default=None, 
        description="Source language (ru, en)"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language (ru, en) - alias for source_language"
    )
    
    @field_validator('title', 'summary')
    @classmethod
    def validate_text_fields(cls, v: Optional[str]) -> str:
        """Strip whitespace from text fields."""
        if v is None:
            return ""
        return v.strip()
    
    def model_post_init(self, __context: Any) -> None:
        """Validate that at least title or summary is provided."""
        if not self.title and not self.summary:
            raise ValueError("At least 'title' or 'summary' must be provided")
        
        # Use language if source_language is not set
        if not self.source_language and self.language:
            self.source_language = self.language


class RutubeGenerateRequest(BaseModel):
    """Request model for Rutube video processing."""
    url: HttpUrl = Field(..., description="Rutube video URL")
    
    @field_validator('url')
    @classmethod
    def validate_rutube_url(cls, v: HttpUrl) -> str:
        """Validate Rutube URL format."""
        url_str = str(v)
        if 'rutube.ru' not in url_str and 'rutube.net' not in url_str:
            raise ValueError("URL must be a valid Rutube video URL")
        return url_str


class TTSGenerateRequest(BaseModel):
    """Request model for TTS generation."""
    text: str = Field(..., min_length=1, description="Text to convert to speech")
    language: Literal["ru", "en", "auto"] = Field(
        default="auto", 
        description="Language (ru, en, auto)"
    )
    voice_gender: Literal["male", "female"] = Field(
        default="female", 
        description="Voice gender (male/female)"
    )
    provider: Optional[Literal["gtts", "pyttsx3", "auto"]] = Field(
        default=None, 
        description="Provider (gtts, pyttsx3, auto)"
    )
    
    @field_validator('text')
    @classmethod
    def validate_text_not_empty(cls, v: str) -> str:
        """Validate that text is not empty after stripping."""
        if isinstance(v, str):
            v = v.strip()
        if not v:
            raise ValueError("Text cannot be empty")
        return v


class EmailSendRequest(BaseModel):
    """Request model for sending email."""
    to_email: EmailStr = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1, description="Email subject")
    html_content: Optional[str] = Field(default=None, description="HTML email content")
    text_content: Optional[str] = Field(default=None, description="Plain text content")
    
    def model_post_init(self, __context: Any) -> None:
        """Validate that at least html_content or text_content is provided."""
        if not self.html_content and not self.text_content:
            raise ValueError("At least 'html_content' or 'text_content' must be provided")


class EmailDigestRequest(BaseModel):
    """Request model for sending daily digest."""
    to_email: EmailStr = Field(..., description="Recipient email address")
    language: Literal["ru", "en"] = Field(default="ru", description="Email language")


class TelegramPostRequest(BaseModel):
    """Request model for posting to Telegram."""
    article: Dict[str, Any] = Field(..., description="News article to post")
    channel_id: Optional[str] = Field(default=None, description="Channel ID or username")
    format_type: Literal["markdown", "html", "plain"] = Field(
        default="markdown",
        description="Post format type"
    )
    
    @field_validator('article')
    @classmethod
    def validate_article(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        """Validate article has required fields."""
        if not v.get('title') and not v.get('summary'):
            raise ValueError("Article must have 'title' or 'summary'")
        return v


class NewsFeedQueryParams(BaseModel):
    """Query parameters model for news feed."""
    category: str = Field(default="all", description="Category filter")
    limit: int = Field(default=20, ge=5, le=100, description="Maximum items")
    language: Literal["all", "ru", "en"] = Field(
        default="all", 
        description="Language filter (all, ru, en)"
    )
    translate_to: Literal["none", "ru", "en"] = Field(
        default="none", 
        description="Translate to (none, ru, en)"
    )
    use_cache: bool = Field(
        default=True, 
        description="Use cached news if available"
    )
