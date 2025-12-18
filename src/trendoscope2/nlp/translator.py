"""
News translator for Trendoscope2.
"""
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

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
    max_items: int = 5
) -> List[Dict[str, Any]]:
    """Translate news items to target language."""
    if not news_items or not FREE_TRANSLATOR_AVAILABLE:
        return news_items[:max_items] if len(news_items) > max_items else news_items
    
    items_to_translate = news_items[:max_items]
    translated_items = []
    
    lang_map = {'ru': 'ru', 'en': 'en', 'russian': 'ru', 'english': 'en'}
    target_lang = lang_map.get(target_language.lower(), 'ru')
    
    for item in items_to_translate:
        item_lang = item.get('language', '').lower()
        if item_lang in ['ru', 'russian']:
            current_lang = 'ru'
        elif item_lang in ['en', 'english']:
            current_lang = 'en'
        else:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            current_lang = 'ru' if _is_russian(text) else 'en'
        
        if current_lang == target_lang:
            translated_items.append({**item, 'translated': False})
            continue
        
        try:
            title = item.get('title', '')
            summary = item.get('summary', '')
            
            if title:
                translator = GoogleTranslator(source=current_lang, target=target_lang)
                translated_title = translator.translate(title)
            else:
                translated_title = title
            
            if summary:
                translator = GoogleTranslator(source=current_lang, target=target_lang)
                translated_summary = translator.translate(summary[:5000])  # Limit length
            else:
                translated_summary = summary
            
            translated_items.append({
                **item,
                'title': translated_title,
                'summary': translated_summary,
                'language': target_lang,
                'translated': True
            })
        except Exception as e:
            logger.warning(f"Translation failed: {e}")
            translated_items.append({**item, 'translated': False})
    
    return translated_items + news_items[max_items:]


def _is_russian(text: str) -> bool:
    """Check if text is primarily in Russian."""
    if not text:
        return False
    cyrillic_count = sum(1 for char in text if '\u0400' <= char <= '\u04FF')
    total_letters = sum(1 for char in text if char.isalpha())
    if total_letters == 0:
        return False
    return (cyrillic_count / total_letters) > 0.3

