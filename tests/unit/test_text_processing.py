"""
Unit tests for text processing utilities.
Tests for clean_html function.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.utils.text_processing import clean_html


class TestCleanHtml:
    """Tests for clean_html function."""

    def test_clean_html_with_none(self):
        """Test clean_html with None."""
        result = clean_html(None)
        assert result == ""

    def test_clean_html_with_empty_string(self):
        """Test clean_html with empty string."""
        result = clean_html("")
        assert result == ""

    def test_clean_html_with_plain_text(self):
        """Test clean_html with plain text (no HTML)."""
        text = "This is plain text"
        result = clean_html(text)
        assert result == text

    def test_clean_html_with_simple_tags(self):
        """Test clean_html with simple HTML tags."""
        text = "<p>Hello World</p>"
        result = clean_html(text)
        assert "<p>" not in result
        assert "</p>" not in result
        assert "Hello World" in result

    def test_clean_html_with_multiple_tags(self):
        """Test clean_html with multiple HTML tags."""
        text = "<div><h1>Title</h1><p>Content</p></div>"
        result = clean_html(text)
        assert "<div>" not in result
        assert "<h1>" not in result
        assert "<p>" not in result
        assert "Title" in result
        assert "Content" in result

    def test_clean_html_with_attributes(self):
        """Test clean_html with HTML tags containing attributes."""
        text = '<a href="http://example.com">Link</a>'
        result = clean_html(text)
        assert "<a" not in result
        assert "href" not in result
        assert "Link" in result

    def test_clean_html_with_nested_tags(self):
        """Test clean_html with nested HTML tags."""
        text = "<div><span>Nested <strong>bold</strong> text</span></div>"
        result = clean_html(text)
        assert "<div>" not in result
        assert "<span>" not in result
        assert "<strong>" not in result
        assert "Nested" in result
        assert "bold" in result
        assert "text" in result

    def test_clean_html_with_self_closing_tags(self):
        """Test clean_html with self-closing HTML tags."""
        text = "Line 1<br/>Line 2<hr/>Line 3"
        result = clean_html(text)
        assert "<br" not in result
        assert "<hr" not in result
        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result

    def test_clean_html_with_whitespace(self):
        """Test clean_html normalizes whitespace."""
        text = "<p>Text   with    multiple   spaces</p>"
        result = clean_html(text)
        # Should normalize multiple spaces
        assert "   " not in result or result.count(" ") < text.count(" ")

    def test_clean_html_with_newlines(self):
        """Test clean_html with newlines in HTML."""
        text = "<p>Line 1\nLine 2</p>"
        result = clean_html(text)
        assert "Line 1" in result
        assert "Line 2" in result

    def test_clean_html_with_special_characters(self):
        """Test clean_html preserves special characters."""
        text = "<p>Price: $100 &amp; €50</p>"
        result = clean_html(text)
        assert "Price" in result
        # HTML entities might be decoded or preserved
        assert isinstance(result, str)

    def test_clean_html_with_cyrillic(self):
        """Test clean_html with Cyrillic text."""
        text = "<p>Привет, мир!</p>"
        result = clean_html(text)
        assert "Привет" in result
        assert "мир" in result
        assert "<p>" not in result

    def test_clean_html_with_complex_html(self):
        """Test clean_html with complex HTML structure."""
        text = """
        <html>
            <head><title>Title</title></head>
            <body>
                <div class="content">
                    <h1>Heading</h1>
                    <p>Paragraph with <em>emphasis</em>.</p>
                </div>
            </body>
        </html>
        """
        result = clean_html(text)
        assert "<html>" not in result
        assert "<head>" not in result
        assert "<body>" not in result
        assert "Title" in result or "Heading" in result
        assert "Paragraph" in result or "emphasis" in result

    def test_clean_html_with_malformed_html(self):
        """Test clean_html with malformed HTML."""
        text = "<p>Unclosed tag<div>Another</p>"
        result = clean_html(text)
        # Should still remove tags and return text
        assert isinstance(result, str)
        assert "Unclosed" in result or "tag" in result or "Another" in result

    def test_clean_html_with_script_tags(self):
        """Test clean_html removes script tags."""
        text = "<script>alert('test');</script><p>Content</p>"
        result = clean_html(text)
        assert "<script>" not in result
        assert "alert" not in result or "Content" in result

    def test_clean_html_with_style_tags(self):
        """Test clean_html removes style tags."""
        text = "<style>body { color: red; }</style><p>Content</p>"
        result = clean_html(text)
        assert "<style>" not in result
        assert "Content" in result

    def test_clean_html_preserves_text_content(self):
        """Test that clean_html preserves actual text content."""
        text = "<div>Important information here</div>"
        result = clean_html(text)
        assert "Important information here" in result
