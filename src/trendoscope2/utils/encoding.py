"""
Encoding utilities for text processing.
Handles UTF-8 encoding issues, mojibake detection and correction.
"""
import logging
from typing import Union

logger = logging.getLogger(__name__)


def safe_str(value: Union[str, bytes, None]) -> str:
    """
    Safely convert value to string, handling encoding issues.
    
    Args:
        value: String, bytes, or None to convert
        
    Returns:
        UTF-8 decoded string
    """
    if value is None:
        return ''
    if isinstance(value, bytes):
        try:
            return value.decode('utf-8')
        except UnicodeDecodeError:
            return value.decode('utf-8', errors='replace')
    return str(value)


def fix_double_encoding(text: Union[str, bytes]) -> str:
    """
    Fix double-encoded UTF-8 text (mojibake).
    
    Detects and corrects cases where UTF-8 bytes were interpreted
    as Latin-1, resulting in mojibake patterns like "Р"Рё" instead of "Ди".
    
    Args:
        text: Text that may be double-encoded
        
    Returns:
        Fixed text with proper UTF-8 encoding
    """
    if not text:
        return ''
    
    # Convert bytes to string if needed
    if isinstance(text, bytes):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError:
            text = text.decode('utf-8', errors='replace')
    
    if not isinstance(text, str):
        text = str(text)
    
    # Check if text looks like double-encoded UTF-8 (mojibake)
    # Common pattern: "Р"Рё" instead of "Ди"
    # This happens when UTF-8 bytes are interpreted as Latin-1
    try:
        # Detect mojibake: if text contains sequences like "Р"Рё"
        # These are UTF-8 bytes interpreted as Latin-1
        has_mojibake_pattern = False
        if len(text) > 0:
            # Check for common mojibake patterns (comprehensive list)
            mojibake_indicators = [
                'Р"', 'РІ', 'РЅ', 'Рѕ', 'Р°', 'Рё', 'СЂ', 'СЃ',
                'РЅР°', 'РІРѕ', 'РґРё', 'РїРѕ', 'РєР°', 'РјРё',
                'РЅР°С€', 'РІР°С€', 'РїСЂРё'
            ]
            has_mojibake_pattern = any(
                indicator in text[:300] for indicator in mojibake_indicators
            )
            
            # Also check if text has high-byte chars but no valid Cyrillic
            high_byte_chars = sum(1 for c in text[:200] if ord(c) > 127)
            cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
            if high_byte_chars > 5 and cyrillic_chars < high_byte_chars * 0.2:
                has_mojibake_pattern = True
        
        if has_mojibake_pattern or any(ord(c) > 127 for c in text[:200] if text):
            # Try: encode as latin1 then decode as utf8
            fixed = text.encode('latin1', errors='ignore').decode(
                'utf-8', errors='replace'
            )
            # Only use if it looks better
            if fixed and '\ufffd' not in fixed[:100]:
                # Check if fixed version has more Cyrillic characters
                cyrillic_original = sum(
                    1 for c in text if '\u0400' <= c <= '\u04FF'
                )
                cyrillic_fixed = sum(
                    1 for c in fixed if '\u0400' <= c <= '\u04FF'
                )
                # Also check if fixed has fewer high-byte non-Cyrillic chars
                high_byte_original = sum(
                    1 for c in text[:200]
                    if ord(c) > 127 and not ('\u0400' <= c <= '\u04FF')
                )
                high_byte_fixed = sum(
                    1 for c in fixed[:200]
                    if ord(c) > 127 and not ('\u0400' <= c <= '\u04FF')
                )
                
                # More lenient condition: if fixed has ANY Cyrillic and
                # fewer mojibake chars
                if (cyrillic_fixed > cyrillic_original) or \
                   (cyrillic_fixed > 0 and high_byte_fixed < high_byte_original) or \
                   (cyrillic_fixed > 0 and cyrillic_original == 0):
                    logger.debug(
                        f"Fixed encoding: '{text[:50]}...' -> "
                        f"'{fixed[:50]}...' "
                        f"(Cyrillic: {cyrillic_original}->{cyrillic_fixed})"
                    )
                    text = fixed
    except (UnicodeEncodeError, UnicodeDecodeError) as e:
        logger.debug(f"Encoding fix error: {e}")
        pass
    
    # Clean up common encoding issues
    text = text.replace('\xa0', ' ')  # Non-breaking space
    text = text.replace('\u200b', '')  # Zero-width space
    text = text.replace('\u200c', '')  # Zero-width non-joiner
    text = text.replace('\u200d', '')  # Zero-width joiner
    
    return str(text)
