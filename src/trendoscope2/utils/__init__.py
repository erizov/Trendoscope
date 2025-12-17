"""
Utility functions for Trendoscope2.
Common helpers for text processing, encoding, and validation.
"""
from .encoding import fix_double_encoding, safe_str
from .text_processing import clean_html

__all__ = [
    'fix_double_encoding',
    'safe_str',
    'clean_html',
]
