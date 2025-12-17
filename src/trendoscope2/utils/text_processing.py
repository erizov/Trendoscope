"""
Text processing utilities.
HTML cleaning, text normalization, and other text transformations.
"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Try to import BeautifulSoup, fallback to regex if not available
try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False
    BeautifulSoup = None


def clean_html(text: Optional[str]) -> str:
    """
    Remove HTML tags from text.
    
    Uses BeautifulSoup if available for thorough cleaning,
    falls back to regex-based removal if not.
    
    Args:
        text: Text that may contain HTML tags
        
    Returns:
        Cleaned text with HTML tags removed
    """
    if not text:
        return ''
    
    # Try BeautifulSoup first (more thorough)
    if HAS_BEAUTIFULSOUP and BeautifulSoup:
        try:
            soup = BeautifulSoup(text, 'html.parser')
            cleaned = soup.get_text(separator=' ', strip=True)
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            return cleaned
        except Exception as e:
            logger.debug(f"HTML cleaning error with BeautifulSoup: {e}")
            # Fallback to regex
    
    # Fallback: regex-based HTML tag removal
    cleaned = re.sub(r'<[^>]+>', '', text)
    # Remove extra whitespace
    cleaned = ' '.join(cleaned.split())
    return cleaned
