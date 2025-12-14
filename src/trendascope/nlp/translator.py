"""
News translator with context preservation.
Translates English news to Russian maintaining nuance and style.
Supports free translation via deep-translator.
"""
from typing import List, Dict, Any, Optional
import json
import re
import logging

logger = logging.getLogger(__name__)

# Try to import free translator
try:
    from deep_translator import GoogleTranslator
    FREE_TRANSLATOR_AVAILABLE = True
except ImportError:
    FREE_TRANSLATOR_AVAILABLE = False
    GoogleTranslator = None


def translate_and_summarize_news(
    news_items: List[Dict[str, Any]],
    target_language: str = "ru",
    provider: str = "free",
    model: Optional[str] = None,
    preserve_context: bool = True,
    max_items: int = 5
) -> List[Dict[str, Any]]:
    """
    Translate news items to target language.
    Limits translation to max_items for reliability.
    
    Args:
        news_items: List of news items to translate
        target_language: Target language ('ru' or 'en')
        provider: Translation provider ('free' for free translator, 'openai' for paid)
        model: Model name (for paid providers)
        preserve_context: Maintain meaning and emotional tone
        max_items: Maximum number of items to translate (default: 5)
    
    Returns:
        List of translated news items
    """
    if not news_items:
        return []
    
    # Limit number of items to translate (for reliability)
    items_to_translate = news_items[:max_items] if len(news_items) > max_items else news_items
    items_not_translated = news_items[max_items:] if len(news_items) > max_items else []
    
    if len(news_items) > max_items:
        logger.info(f"Limiting translation to {max_items} items (from {len(news_items)})")
    
    # Use free translator by default
    translated = []
    if provider == "free" and FREE_TRANSLATOR_AVAILABLE:
        translated = _translate_with_free_service(
            items_to_translate,
            target_language,
            batch_size=3,
            max_items=max_items
        )
    elif provider == "openai":
        # Fallback to OpenAI for paid translation
        translated = _translate_with_llm(items_to_translate, target_language, model)
    else:
        # If free translator not available, return original
        logger.warning("Free translator not available, returning original items")
        translated = items_to_translate
    
    # Combine translated items with non-translated items
    result = translated + items_not_translated
    return result


def _translate_with_free_service(
    news_items: List[Dict[str, Any]],
    target_language: str,
    batch_size: int = 3,
    max_items: int = 5
) -> List[Dict[str, Any]]:
    """
    Translate news using free Google Translate service.
    Processes in small batches for reliability.
    
    Args:
        news_items: List of news items
        target_language: Target language ('ru' or 'en')
        batch_size: Number of items to translate at once (default: 3)
    
    Returns:
        List of translated news items
    """
    if not FREE_TRANSLATOR_AVAILABLE:
        logger.warning("Free translator (deep-translator) not available - returning original items")
        return news_items
    
    if GoogleTranslator is None:
        logger.error("GoogleTranslator is None - translation unavailable")
        return news_items
    
    # Map language codes
    lang_map = {
        'ru': 'ru',
        'en': 'en',
        'russian': 'ru',
        'english': 'en'
    }
    target_lang = lang_map.get(target_language.lower(), 'ru')
    source_lang = 'en' if target_lang == 'ru' else 'ru'
    
    # Limit total items to translate (for speed)
    items_to_process = news_items[:max_items] if len(news_items) > max_items else news_items
    items_not_translated = news_items[max_items:] if len(news_items) > max_items else []
    
    if len(news_items) > max_items:
        logger.info(f"Limiting translation to {max_items} items (from {len(news_items)})")
    
    translated_items = []
    
    # Process in small batches (3 items at a time)
    for batch_start in range(0, len(items_to_process), batch_size):
        batch = items_to_process[batch_start:batch_start + batch_size]
        logger.debug(f"Translating batch {batch_start // batch_size + 1} ({len(batch)} items)")
        
        for item in batch:
            # Detect current language from item or text
            item_lang = item.get('language', '').lower()
            if item_lang in ['ru', 'russian']:
                current_lang = 'ru'
            elif item_lang in ['en', 'english']:
                current_lang = 'en'
            else:
                # Fallback to text detection
                text = f"{item.get('title', '')} {item.get('summary', '')}"
                current_lang = 'ru' if _is_russian(text) else 'en'
            
            # Only translate if needed
            if current_lang == target_lang:
                # Already in target language
                translated_items.append({**item, 'translated': False})
                continue
            
            # Use detected source language, not hardcoded assumption
            actual_source_lang = current_lang
            
            logger.info(
                f"Translating item: source={actual_source_lang}, target={target_lang}, "
                f"title={item.get('title', '')[:50]}..."
            )
            
            try:
                # Translate title
                title = item.get('title', '')
                if title:
                    logger.debug(f"Translating title: {title[:50]}...")
                    translator = GoogleTranslator(source=actual_source_lang, target=target_lang)
                    translated_title = translator.translate(title)
                    logger.debug(f"Translated title: {translated_title[:50]}...")
                    if translated_title == title:
                        logger.warning(f"Title translation returned same text - translation may have failed")
                else:
                    translated_title = title
                
                # Translate summary
                summary = item.get('summary', '')
                if summary:
                    logger.debug(f"Translating summary: {len(summary)} chars")
                    # Split long text into chunks (Google Translate has limits)
                    if len(summary) > 5000:
                        # Split by sentences
                        sentences = summary.split('. ')
                        translated_sentences = []
                        for sentence in sentences:
                            if sentence.strip():
                                try:
                                    translator = GoogleTranslator(source=actual_source_lang, target=target_lang)
                                    translated_sent = translator.translate(sentence)
                                    translated_sentences.append(translated_sent)
                                except Exception as e:
                                    logger.warning(f"Translation error for sentence: {e}")
                                    translated_sentences.append(sentence)
                        translated_summary = '. '.join(translated_sentences)
                    else:
                        translator = GoogleTranslator(source=actual_source_lang, target=target_lang)
                        translated_summary = translator.translate(summary)
                        logger.debug(f"Translated summary: {translated_summary[:100]}...")
                        if translated_summary == summary:
                            logger.warning(f"Summary translation returned same text - translation may have failed")
                else:
                    translated_summary = summary
                
                # Create translated item
                translated_item = {
                    **item,
                    'title': translated_title,
                    'summary': translated_summary,
                    'language': target_lang,
                    'translated': True
                }
                translated_items.append(translated_item)
                logger.info(f"Translation successful: {translated_title[:50]}...")
                
            except Exception as e:
                logger.error(f"Translation failed for item: {e}", exc_info=True)
                # Return original item if translation fails
                translated_items.append({**item, 'translated': False})
    
    # Add non-translated items back (they keep original language)
    translated_items.extend([
        {**item, 'translated': False} for item in items_not_translated
    ])
    
    return translated_items


def _translate_with_llm(
    news_items: List[Dict[str, Any]],
    target_language: str,
    model: Optional[str]
) -> List[Dict[str, Any]]:
    """
    Translate using LLM (OpenAI) - paid option.
    
    Args:
        news_items: List of news items
        target_language: Target language ('ru' or 'en')
        model: Model name
    
    Returns:
        List of translated news items
    """
    from ..gen.llm.providers import call_llm
    
    # Separate by current language
    items_to_translate = []
    items_already_correct = []
    
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}"
        current_lang = 'ru' if _is_russian(text) else 'en'
        
        if current_lang == target_language:
            items_already_correct.append({**item, 'translated': False})
        else:
            items_to_translate.append(item)
    
    if not items_to_translate:
        return items_already_correct
    
    # Translate in batches
    translated = items_already_correct.copy()
    batch_size = 5
    
    for i in range(0, len(items_to_translate), batch_size):
        batch = items_to_translate[i:i + batch_size]
        translated_batch = _translate_batch_llm(batch, target_language, model)
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


def _translate_batch_llm(
    batch: List[Dict[str, Any]],
    target_language: str,
    model: Optional[str]
) -> List[Dict[str, Any]]:
    """Translate a batch of news items using LLM."""
    from ..gen.llm.providers import call_llm
    
    # Determine source and target
    target_lang_name = "русский" if target_language == "ru" else "English"
    source_lang_name = "английского" if target_language == "ru" else "русского"
    
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
        # Use OpenAI provider for LLM translation
        response = call_llm(
            provider="openai",
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

