"""
Post generator using author style from RAG.
Generates posts in the style of classic authors.
"""
import os
from typing import Dict, Any, Optional
import logging

from .author_style_rag import get_author_rag, AUTHORS
from ..ingest.news_sources import fetch_trending_news
from .llm.providers import call_llm

logger = logging.getLogger(__name__)


def generate_post_with_author_style(
    author_id: str,
    topic: str = "any",
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.8,
    translate: bool = True
) -> Dict[str, Any]:
    """
    Generate post in author's style.
    
    Args:
        author_id: Author identifier
        topic: Topic focus
        provider: LLM provider
        model: Model name
        temperature: Generation temperature
        translate: Translate news
        
    Returns:
        Generated post dictionary
    """
    if author_id not in AUTHORS:
        return {
            "title": "Ошибка: неизвестный автор",
            "text": f"Автор '{author_id}' не найден в системе.",
            "tags": ["ошибка"],
            "error": f"Unknown author: {author_id}"
        }
    
    try:
        author_info = AUTHORS[author_id]
        author_rag = get_author_rag()
        
        # Get author style context
        style_context = author_rag.get_author_style_context(
            author_id=author_id,
            topic=topic if topic != "any" else None,
            num_examples=3
        )
        
        # Fetch trending news
        news_data = fetch_trending_news(max_items=5)
        news_items = news_data.get("news_items", [])
        
        # Filter by topic if needed
        if topic != "any":
            from .post_generator import _filter_news_by_topic
            news_items = _filter_news_by_topic(news_items, topic)
        
        # Translate if needed
        if translate and news_items:
            skip_translation = os.getenv("SKIP_TRANSLATION", "false").lower() == "true"
            if not skip_translation and provider != "demo":
                from ..nlp.translator import translate_and_summarize_news
                news_items = translate_and_summarize_news(
                    news_items,
                    target_language="ru",
                    provider="free",
                    max_items=3
                )
        
        # Build news context
        news_context = "\n\n".join([
            f"Новость {i+1}: {item.get('title', '')}\n{item.get('summary', '')[:300]}"
            for i, item in enumerate(news_items[:3])
        ])
        
        # Build prompt
        prompt = f"""Ты - писатель, который пишет в стиле {author_info['name']} ({author_info['english_name']}).

{style_context}

Задача: Напиши пост в стиле этого автора на основе следующих новостей:

{news_context}

Требования:
1. Стиль должен точно соответствовать стилю {author_info['name']}
2. Используй характерные для этого автора:
   - Лексику и фразеологию
   - Синтаксические конструкции
   - Тематические акценты: {', '.join(author_info['style_keywords'])}
3. Пост должен быть актуальным и связанным с новостями
4. Сохрани философскую/литературную глубину автора

Верни JSON:
{{
    "title": "заголовок в стиле автора",
    "text": "текст поста в стиле автора (минимум 500 слов)",
    "tags": ["тег1", "тег2", "тег3"]
}}

Важно: Текст должен быть написан именно в стиле {author_info['name']}, а не просто упоминать его имя."""
        
        # Generate post
        logger.info(f"Generating post in style of {author_info['name']}")
        
        response = call_llm(
            provider=provider,
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=2500
        )
        
        # Parse response
        import json
        import re
        
        try:
            # Extract JSON
            response_text = response.strip()
            response_text = re.sub(r'^```(?:json)?\s*\n?', '', response_text, flags=re.IGNORECASE)
            response_text = re.sub(r'\n?```\s*$', '', response_text)
            
            start = response_text.find('{')
            end = response_text.rfind('}')
            
            if start == -1 or end == -1:
                raise ValueError("No JSON found")
            
            json_str = response_text[start:end+1]
            generated = json.loads(json_str)
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"JSON parsing failed, using fallback: {e}")
            # Fallback: extract title and text
            lines = response.split('\n')
            title = lines[0] if lines else "Пост в стиле автора"
            text = '\n'.join(lines[1:]) if len(lines) > 1 else response
            
            generated = {
                "title": title.replace('Заголовок:', '').replace('Title:', '').strip(),
                "text": text.strip(),
                "tags": []
            }
        
        # Validate
        if not generated.get("title"):
            generated["title"] = f"Пост в стиле {author_info['name']}"
        
        if not generated.get("text"):
            generated["text"] = "Текст не был сгенерирован."
        
        if "tags" not in generated or not generated["tags"]:
            generated["tags"] = [author_id, topic if topic != "any" else "general"]
        
        # Add metadata
        generated["author_style"] = author_id
        generated["author_name"] = author_info['name']
        generated["style"] = f"author:{author_id}"
        generated["topic"] = topic
        generated["provider"] = provider
        
        return generated
        
    except Exception as e:
        logger.error(f"Error generating post with author style: {e}", exc_info=True)
        return {
            "title": "Ошибка генерации",
            "text": f"Не удалось сгенерировать пост: {str(e)}",
            "tags": ["ошибка"],
            "error": str(e)
        }

