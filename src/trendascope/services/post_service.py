"""
Post generation service - business logic for post operations.
"""
from typing import Dict, Optional, Any
import os

from ..gen.post_generator import generate_post_from_storage
from ..gen.model_selector import select_model_for_task
from ..gen.cost_tracker import track_call
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PostService:
    """Service for post generation operations."""
    
    def generate_post(
        self,
        style: str = "philosophical",
        topic: str = "any",
        provider: str = "openai",
        model: Optional[str] = None,
        quality: str = "standard",
        temperature: float = 0.8,
        translate: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a post.
        
        Args:
            style: Post style
            topic: Topic focus
            provider: LLM provider
            model: Model name
            quality: Quality tier
            temperature: Generation temperature
            translate: Translate news
            
        Returns:
            Generated post with metadata
        """
        logger.info(
            "generating_post",
            extra={
                "style": style,
                "topic": topic,
                "provider": provider,
                "quality": quality
            }
        )
        
        # Select model based on quality tier
        if not model:
            model_config = select_model_for_task("post_generation", quality, provider)
            model = model_config["model"]
            if quality in ["draft", "standard", "premium"]:
                temperature = model_config.get("temperature", temperature)
        
        # Set translation preference
        if not translate:
            os.environ["SKIP_TRANSLATION"] = "true"
        else:
            os.environ.pop("SKIP_TRANSLATION", None)
        
        # Generate post
        result = generate_post_from_storage(
            style=style,
            topic=topic,
            provider=provider,
            model=model,
            temperature=temperature
        )
        
        # Track cost if using AI provider
        if provider in ["openai", "anthropic"]:
            try:
                prompt_len = len(str(result.get("title", "")) + str(result.get("text", "")))
                estimated_tokens_in = prompt_len // 4
                estimated_tokens_out = len(result.get("text", "")) // 4
                cost = track_call(provider, model, estimated_tokens_in, estimated_tokens_out)
                result["cost_estimate"] = f"${cost:.4f}"
            except Exception:
                pass
        
        logger.info(
            "post_generated",
            extra={
                "title": result.get('title', 'No title')[:50],
                "provider": provider
            }
        )
        
        return result

