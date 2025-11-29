"""
News translator with context preservation.
Translates English news to Russian maintaining nuance and style.
"""
from typing import List, Dict, Any, Optional
import json
import re


def translate_and_summarize_news(
    news_items: List[Dict[str, Any]],
    provider: str = "openai",
    model: Optional[str] = None,
    preserve_context: bool = True
) -> List[Dict[str, Any]]:
    """
    Translate English news to Russian with context preservation.
    
    Args:
        news_items: List of news items to translate
        provider: LLM provider for translation
        model: Model name
        preserve_context: Maintain meaning and emotional tone
    
    Returns:
        List of translated news items
    """
    from ..gen.llm.providers import call_llm
    
    if not news_items:
        return []
    
    # Separate Russian and English news
    russian_news = []
    english_news = []
    
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        if _is_russian(text):
            russian_news.append(item)
        else:
            english_news.append(item)
    
    # Russian news doesn't need translation
    translated = russian_news.copy()
    
    # Translate English news in batches
    if english_news:
        batch_size = 5
        for i in range(0, len(english_news), batch_size):
            batch = english_news[i:i + batch_size]
            translated_batch = _translate_batch(
                batch,
                provider,
                model,
                preserve_context
            )
            translated.extend(translated_batch)
    
    return translated


def _is_russian(text: str) -> bool:
    """Check if text is primarily in Russian."""
    if not text:
        return False
    
    # Count Cyrillic characters
    cyrillic_count = sum(
        1 for char in text
        if '\u0400' <= char <= '\u04FF'
    )
    
    total_letters = sum(
        1 for char in text
        if char.isalpha()
    )
    
    if total_letters == 0:
        return False
    
    # If more than 30% Cyrillic, consider it Russian
    return (cyrillic_count / total_letters) > 0.3


def _translate_batch(
    batch: List[Dict[str, Any]],
    provider: str,
    model: Optional[str],
    preserve_context: bool
) -> List[Dict[str, Any]]:
    """Translate a batch of news items."""
    from ..gen.llm.providers import call_llm
    
    # Format news for translation
    news_list = []
    for idx, item in enumerate(batch):
        news_list.append(f"""
Новость {idx + 1}:
Заголовок: {item.get('title', '')}
Содержание: {item.get('summary', '')}
Источник: {item.get('source', '')}
""")
    
    news_text = "\n---\n".join(news_list)
    
    prompt = f"""Переведи следующие новости с английского на русский язык.

ТРЕБОВАНИЯ:
- Сохрани смысл и контекст каждой новости
- Используй естественный русский язык (не дословный перевод)
- Сохрани эмоциональную окраску и тон
- Термины переводи с учетом устоявшихся русских эквивалентов
- Имена и географические названия транслитерируй правильно

НОВОСТИ:
{news_text}

Верни результат в формате JSON массива:
[
  {{
    "title": "Переведенный заголовок",
    "summary": "Переведенное содержание",
    "source": "Источник"
  }},
  ...
]

Переведи ВСЕ новости. Массив должен содержать {len(batch)} элементов."""
    
    try:
        response = call_llm(
            provider=provider,
            prompt=prompt,
            model=model,
            temperature=0.3
        )
        
        # Parse JSON response
        translated = _parse_translation_response(response)
        
        # Merge with original items
        result = []
        for i, item in enumerate(batch):
            if i < len(translated):
                result.append({
                    **item,
                    'title': translated[i].get('title', item['title']),
                    'summary': translated[i].get('summary', item['summary']),
                    'translated': True
                })
            else:
                # Fallback to original if translation missing
                result.append({
                    **item,
                    'translated': False
                })
        
        return result
        
    except Exception as e:
        # Return original items if translation fails
        return [{**item, 'translated': False} for item in batch]


def _parse_translation_response(response: str) -> List[Dict[str, str]]:
    """Parse LLM translation response."""
    # Remove markdown code blocks
    response = re.sub(r'^```(?:json)?\s*\n?', '', response, flags=re.IGNORECASE)
    response = re.sub(r'\n?```\s*$', '', response)
    
    # Find JSON array
    start = response.find('[')
    end = response.rfind(']')
    
    if start == -1 or end == -1:
        return []
    
    json_str = response[start:end + 1]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return []


def smart_translate_text(
    text: str,
    provider: str = "openai",
    model: Optional[str] = None,
    style: str = "neutral"
) -> str:
    """
    Translate single text with style preservation.
    
    Args:
        text: Text to translate
        provider: LLM provider
        model: Model name
        style: Translation style (neutral, formal, informal, ironic)
    
    Returns:
        Translated text
    """
    from ..gen.llm.providers import call_llm
    
    if _is_russian(text):
        return text
    
    style_instructions = {
        "neutral": "естественный литературный язык",
        "formal": "формальный официальный стиль",
        "informal": "разговорный неформальный стиль",
        "ironic": "с сохранением иронии и сарказма"
    }
    
    style_instruction = style_instructions.get(style, "естественный язык")
    
    prompt = f"""Переведи текст с английского на русский язык.

Стиль перевода: {style_instruction}

Текст:
{text}

Верни ТОЛЬКО переведенный текст, без пояснений."""
    
    try:
        translated = call_llm(
            provider=provider,
            prompt=prompt,
            model=model,
            temperature=0.3
        )
        return translated.strip()
    except Exception:
        return text


def get_translation_stats(news_items: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get statistics about translated items.
    
    Args:
        news_items: List of news items
    
    Returns:
        Dictionary with stats
    """
    stats = {
        'total': len(news_items),
        'russian': 0,
        'english': 0,
        'translated': 0,
        'failed': 0
    }
    
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        
        if _is_russian(text):
            stats['russian'] += 1
        else:
            stats['english'] += 1
        
        if item.get('translated'):
            stats['translated'] += 1
        elif not _is_russian(text):
            stats['failed'] += 1
    
    return stats

