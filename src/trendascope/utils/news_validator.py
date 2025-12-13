"""
News item validation utilities.
Filters out empty, invalid, or low-quality articles.
"""
from typing import Dict, Any, List
import re
import logging

logger = logging.getLogger(__name__)


def is_valid_article(item: Dict[str, Any]) -> bool:
    """
    Alias for is_valid_news_item for consistency.
    """
    return is_valid_news_item(item)


def is_valid_news_item(item: Dict[str, Any]) -> bool:
    """
    Check if news item is valid and should be displayed.
    
    Args:
        item: News item dictionary
        
    Returns:
        True if item is valid, False otherwise
    """
    title = item.get('title', '').strip()
    summary = item.get('summary', '').strip()
    
    # Must have at least a title
    if not title:
        return False
    
    # Check for empty or placeholder titles
    if len(title) < 3:
        return False
    
    # Check for patterns that indicate invalid content
    invalid_patterns = [
        r'^[A-Z]+:\s*[-,\s]*$',  # "HGC: - , , ,"
        r'^[A-Z]+\s*[:\-]\s*$',  # "ABC: -"
        r'^[^\w\s]+$',  # Only punctuation/symbols
        r'^\.+\s*$',  # Only dots
        r'^,\s*$',  # Only commas
        r'^\s*[-,\s\.]+\s*$',  # Only dashes, commas, dots, spaces
    ]
    
    for pattern in invalid_patterns:
        if re.match(pattern, title, re.IGNORECASE):
            logger.debug(f"Invalid title pattern: {title[:50]}")
            return False
    
    # Check for too many special characters (likely corrupted)
    special_char_ratio = sum(1 for c in title if not c.isalnum() and not c.isspace()) / max(len(title), 1)
    if special_char_ratio > 0.5:  # More than 50% special chars
        logger.debug(f"Too many special characters in title: {title[:50]}")
        return False
    
    # Check for repetitive patterns (like "Facebook*, Instagram, YouTube, Google . , . , ,")
    if _has_repetitive_pattern(title):
        logger.debug(f"Repetitive pattern detected: {title[:50]}")
        return False
    
    # Check summary if available
    if summary:
        # Similar checks for summary
        if len(summary) < 10:
            return False
        
        if _has_repetitive_pattern(summary):
            logger.debug(f"Repetitive pattern in summary: {summary[:50]}")
            return False
        
        # Check for too many special characters in summary
        special_char_ratio_summary = sum(1 for c in summary if not c.isalnum() and not c.isspace()) / max(len(summary), 1)
        if special_char_ratio_summary > 0.4:
            logger.debug(f"Too many special characters in summary")
            return False
    
    # Check for meaningful content (at least some words)
    words = re.findall(r'\b\w+\b', title.lower())
    if len(words) < 2:  # At least 2 words
        logger.debug(f"Not enough words in title: {title[:50]}")
        return False
    
    return True


def _has_repetitive_pattern(text: str) -> bool:
    """
    Check if text has repetitive patterns like "., ., .," or "Facebook, Instagram, YouTube, Google . , . ,"
    
    Args:
        text: Text to check
        
    Returns:
        True if repetitive pattern detected
    """
    # Check for patterns like "., ., .," or ", , ,"
    if re.search(r'[.,]\s*[.,]\s*[.,]\s*[.,]', text):
        return True
    
    # Check for patterns like "word, word, word . , . ,"
    # Count punctuation sequences
    punctuation_sequences = re.findall(r'[.,;:]\s*[.,;:]', text)
    if len(punctuation_sequences) >= 3:
        return True
    
    # Check for too many commas/dots in a row
    if re.search(r'[,.]\s*[,.]\s*[,.]\s*[,.]', text):
        return True
    
    return False


def filter_valid_news(news_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Filter out invalid news items.
    
    Args:
        news_items: List of news items
        
    Returns:
        List of valid news items
    """
    original_count = len(news_items)
    valid_items = [item for item in news_items if is_valid_news_item(item)]
    filtered_count = original_count - len(valid_items)
    
    if filtered_count > 0:
        logger.info(f"Filtered out {filtered_count} invalid news items (from {original_count})")
    
    return valid_items

