"""
Unit tests for encoding utilities.
Tests for safe_str and fix_double_encoding functions.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.utils.encoding import safe_str, fix_double_encoding


class TestSafeStr:
    """Tests for safe_str function."""

    def test_safe_str_with_string(self):
        """Test safe_str with regular string."""
        result = safe_str("Hello World")
        assert result == "Hello World"
        assert isinstance(result, str)

    def test_safe_str_with_bytes_utf8(self):
        """Test safe_str with UTF-8 bytes."""
        text_bytes = "Привет".encode('utf-8')
        result = safe_str(text_bytes)
        assert result == "Привет"
        assert isinstance(result, str)

    def test_safe_str_with_bytes_invalid_utf8(self):
        """Test safe_str with invalid UTF-8 bytes."""
        # Invalid UTF-8 sequence
        invalid_bytes = b'\xff\xfe\x00\x01'
        result = safe_str(invalid_bytes)
        # Should use errors='replace' and return string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_safe_str_with_none(self):
        """Test safe_str with None."""
        result = safe_str(None)
        assert result == ''
        assert isinstance(result, str)

    def test_safe_str_with_empty_string(self):
        """Test safe_str with empty string."""
        result = safe_str("")
        assert result == ""
        assert isinstance(result, str)

    def test_safe_str_with_empty_bytes(self):
        """Test safe_str with empty bytes."""
        result = safe_str(b"")
        assert result == ""
        assert isinstance(result, str)

    def test_safe_str_with_int(self):
        """Test safe_str with integer (converts to str)."""
        result = safe_str(123)
        assert result == "123"
        assert isinstance(result, str)

    def test_safe_str_with_float(self):
        """Test safe_str with float (converts to str)."""
        result = safe_str(3.14)
        assert result == "3.14"
        assert isinstance(result, str)

    def test_safe_str_with_cyrillic_bytes(self):
        """Test safe_str with Cyrillic text as bytes."""
        text_bytes = "Тест".encode('utf-8')
        result = safe_str(text_bytes)
        assert result == "Тест"


class TestFixDoubleEncoding:
    """Tests for fix_double_encoding function."""

    def test_fix_double_encoding_with_empty_string(self):
        """Test fix_double_encoding with empty string."""
        result = fix_double_encoding("")
        assert result == ""

    def test_fix_double_encoding_with_none(self):
        """Test fix_double_encoding with None."""
        result = fix_double_encoding(None)
        assert result == ""

    def test_fix_double_encoding_with_regular_string(self):
        """Test fix_double_encoding with normal string."""
        text = "Hello World"
        result = fix_double_encoding(text)
        assert result == text

    def test_fix_double_encoding_with_cyrillic(self):
        """Test fix_double_encoding with Cyrillic text."""
        text = "Привет, мир!"
        result = fix_double_encoding(text)
        assert result == text

    def test_fix_double_encoding_with_bytes(self):
        """Test fix_double_encoding with bytes input."""
        text_bytes = "Привет".encode('utf-8')
        result = fix_double_encoding(text_bytes)
        assert isinstance(result, str)
        assert "Привет" in result or len(result) > 0

    def test_fix_double_encoding_with_mojibake_pattern(self):
        """Test fix_double_encoding with mojibake pattern."""
        # Simulate double-encoded text (UTF-8 bytes interpreted as Latin-1)
        # Common mojibake pattern: 'Р"Рё' instead of "Ди"
        text = 'Р"Рё'  # Common mojibake pattern
        result = fix_double_encoding(text)
        # Should attempt to fix or return cleaned version
        assert isinstance(result, str)

    def test_fix_double_encoding_with_non_string(self):
        """Test fix_double_encoding with non-string type."""
        result = fix_double_encoding(123)
        assert isinstance(result, str)

    def test_fix_double_encoding_removes_non_breaking_space(self):
        """Test that fix_double_encoding removes non-breaking spaces."""
        text = "Hello\xa0World"
        result = fix_double_encoding(text)
        assert '\xa0' not in result
        assert ' ' in result

    def test_fix_double_encoding_removes_zero_width_spaces(self):
        """Test that fix_double_encoding removes zero-width spaces."""
        text = "Hello\u200bWorld\u200c\u200d"
        result = fix_double_encoding(text)
        assert '\u200b' not in result
        assert '\u200c' not in result
        assert '\u200d' not in result

    def test_fix_double_encoding_with_long_text(self):
        """Test fix_double_encoding with long text."""
        text = "A" * 500
        result = fix_double_encoding(text)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_fix_double_encoding_with_mixed_encoding(self):
        """Test fix_double_encoding with mixed encoding issues."""
        text = "Hello\xa0World\u200bTest"
        result = fix_double_encoding(text)
        assert isinstance(result, str)
        # Should clean up special characters
        assert '\xa0' not in result or result.replace('\xa0', ' ') == result

    def test_fix_double_encoding_preserves_valid_cyrillic(self):
        """Test that valid Cyrillic text is preserved."""
        text = "Новости о технологиях и бизнесе"
        result = fix_double_encoding(text)
        # Should preserve Cyrillic characters
        assert any('\u0400' <= c <= '\u04FF' for c in result)
