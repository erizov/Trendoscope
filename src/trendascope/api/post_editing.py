"""
Post editing and refinement endpoints.
Allows users to edit, refine, and improve generated posts.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ..gen.post_generator import generate_post_from_storage
from ..gen.llm.providers import call_llm
from ..storage.post_storage import PostStorage
from ..utils.response import APIResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/{post_id}/refine")
async def refine_post(
    post_id: str,
    refinement: Dict[str, Any] = Body(...)
):
    """
    Refine a generated post.
    
    Request body:
    {
        "section": "title" | "text" | "all",
        "tone": "formal" | "informal" | "neutral" | "provocative",
        "length": "short" | "medium" | "long",
        "focus": "specific aspect to emphasize"
    }
    
    Returns:
        Refined post
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        section = refinement.get('section', 'all')
        tone = refinement.get('tone', 'neutral')
        length = refinement.get('length', 'medium')
        focus = refinement.get('focus', '')
        
        # Build refinement prompt
        original_text = post.get('text', '')
        original_title = post.get('title', '')
        
        if section == 'title':
            prompt = f"""Улучши заголовок следующего поста:
            
Оригинальный заголовок: {original_title}

Требования:
- Тон: {tone}
- Фокус: {focus if focus else 'общий'}
- Сохрани смысл, но сделай более привлекательным

Верни только улучшенный заголовок, без дополнительных комментариев."""
        elif section == 'text':
            prompt = f"""Улучши текст следующего поста:
            
Оригинальный текст: {original_text}

Требования:
- Тон: {tone}
- Длина: {length}
- Фокус: {focus if focus else 'общий'}
- Сохрани основную идею, но улучши формулировки

Верни только улучшенный текст."""
        else:  # all
            prompt = f"""Улучши следующий пост:
            
Заголовок: {original_title}
Текст: {original_text}

Требования:
- Тон: {tone}
- Длина: {length}
- Фокус: {focus if focus else 'общий'}
- Сохрани основную идею, но улучши формулировки

Верни JSON:
{{
    "title": "улучшенный заголовок",
    "text": "улучшенный текст"
}}"""
        
        # Call LLM for refinement
        refined_content = call_llm(
            provider=post.get('provider', 'demo'),
            prompt=prompt,
            model=post.get('model'),
            temperature=0.7,
            max_tokens=2000
        )
        
        # Parse response
        if section == 'all' and '{' in refined_content:
            import json
            try:
                refined_data = json.loads(refined_content)
                post['title'] = refined_data.get('title', original_title)
                post['text'] = refined_data.get('text', original_text)
            except:
                # Fallback: treat as text
                post['text'] = refined_content
        elif section == 'title':
            post['title'] = refined_content.strip()
        else:
            post['text'] = refined_content.strip()
        
        # Update post
        post['refined_at'] = datetime.now().isoformat()
        post['refinement_history'] = post.get('refinement_history', []) + [refinement]
        
        storage.update_post(post_id, post)
        
        return APIResponse.success_response(
            data=post,
            message="Post refined successfully"
        )
        
    except Exception as e:
        logger.error(f"Post refinement error: {e}", exc_info=True)
        return APIResponse.error_response(f"Refinement failed: {str(e)}")


@router.post("/{post_id}/regenerate-section")
async def regenerate_section(
    post_id: str,
    section: str = Body(..., embed=True),
    prompt: Optional[str] = Body(None, embed=True)
):
    """
    Regenerate a specific section of a post.
    
    Args:
        post_id: Post ID
        section: Section to regenerate (title, introduction, body, conclusion)
        prompt: Optional custom prompt for regeneration
        
    Returns:
        Updated post
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        original_text = post.get('text', '')
        
        # Build regeneration prompt
        if not prompt:
            if section == 'title':
                prompt = f"Создай новый заголовок для поста: {original_text[:200]}"
            elif section == 'introduction':
                prompt = f"Создай новое введение для поста: {original_text}"
            elif section == 'conclusion':
                prompt = f"Создай новое заключение для поста: {original_text}"
            else:
                prompt = f"Перепиши секцию '{section}' поста: {original_text}"
        
        # Regenerate
        regenerated = call_llm(
            provider=post.get('provider', 'demo'),
            prompt=prompt,
            model=post.get('model'),
            temperature=0.8,
            max_tokens=1000
        )
        
        # Update post
        if section == 'title':
            post['title'] = regenerated.strip()
        else:
            # For text sections, replace the relevant part
            # This is simplified - in real app, would parse and replace specific section
            post['text'] = regenerated.strip()
        
        post['regenerated_at'] = datetime.now().isoformat()
        storage.update_post(post_id, post)
        
        return APIResponse.success_response(
            data=post,
            message=f"Section '{section}' regenerated successfully"
        )
        
    except Exception as e:
        logger.error(f"Section regeneration error: {e}", exc_info=True)
        return APIResponse.error_response(f"Regeneration failed: {str(e)}")


@router.post("/{post_id}/adjust-tone")
async def adjust_tone(
    post_id: str,
    tone: str = Body(..., embed=True)
):
    """
    Adjust the tone of a post.
    
    Args:
        post_id: Post ID
        tone: New tone (formal, informal, neutral, provocative, philosophical)
        
    Returns:
        Updated post
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        original_text = post.get('text', '')
        original_title = post.get('title', '')
        
        prompt = f"""Измени тон следующего поста на {tone}:

Заголовок: {original_title}
Текст: {original_text}

Верни JSON:
{{
    "title": "новый заголовок в тоне {tone}",
    "text": "новый текст в тоне {tone}"
}}"""
        
        adjusted = call_llm(
            provider=post.get('provider', 'demo'),
            prompt=prompt,
            model=post.get('model'),
            temperature=0.8,
            max_tokens=2000
        )
        
        # Parse response
        import json
        try:
            adjusted_data = json.loads(adjusted)
            post['title'] = adjusted_data.get('title', original_title)
            post['text'] = adjusted_data.get('text', original_text)
        except:
            post['text'] = adjusted.strip()
        
        post['tone'] = tone
        post['adjusted_at'] = datetime.now().isoformat()
        storage.update_post(post_id, post)
        
        return APIResponse.success_response(
            data=post,
            message=f"Tone adjusted to {tone}"
        )
        
    except Exception as e:
        logger.error(f"Tone adjustment error: {e}", exc_info=True)
        return APIResponse.error_response(f"Tone adjustment failed: {str(e)}")


@router.get("/{post_id}/suggestions")
async def get_improvement_suggestions(post_id: str):
    """
    Get AI-powered suggestions for improving a post.
    
    Returns:
        List of improvement suggestions
    """
    try:
        storage = PostStorage()
        post = storage.get_post(post_id)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        prompt = f"""Проанализируй следующий пост и предложи 3-5 конкретных улучшений:

Заголовок: {post.get('title', '')}
Текст: {post.get('text', '')}

Верни JSON массив с предложениями:
[
    {{
        "type": "grammar" | "style" | "structure" | "content",
        "suggestion": "конкретное предложение",
        "priority": "high" | "medium" | "low"
    }}
]"""
        
        suggestions_text = call_llm(
            provider=post.get('provider', 'demo'),
            prompt=prompt,
            model=post.get('model'),
            temperature=0.5,
            max_tokens=1000
        )
        
        # Parse suggestions
        import json
        try:
            suggestions = json.loads(suggestions_text)
        except:
            # Fallback: create simple suggestions
            suggestions = [
                {
                    "type": "style",
                    "suggestion": "Проверь стиль и тон поста",
                    "priority": "medium"
                }
            ]
        
        return APIResponse.success_response(
            data={'suggestions': suggestions},
            message="Suggestions generated"
        )
        
    except Exception as e:
        logger.error(f"Suggestions error: {e}", exc_info=True)
        return APIResponse.error_response(f"Failed to generate suggestions: {str(e)}")

