"""
Unit tests for categorization service.
Tests for CategorizationService.categorize method.
"""
import pytest
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from trendoscope2.services.categorization_service import CategorizationService


class TestCategorizationService:
    """Tests for CategorizationService."""

    def test_categorize_legal_news(self):
        """Test categorization of legal news."""
        item = {
            'title': 'Court ruling on criminal case',
            'summary': 'Judge sentenced the defendant',
            'description': 'The court made a decision'
        }
        result = CategorizationService.categorize(item)
        assert result == 'legal'

    def test_categorize_legal_news_russian(self):
        """Test categorization of legal news in Russian."""
        item = {
            'title': 'Суд вынес приговор',
            'summary': 'Прокурор обвинил подозреваемого',
            'description': 'Дело передано в суд'
        }
        result = CategorizationService.categorize(item)
        assert result == 'legal'

    def test_categorize_conflict_news(self):
        """Test categorization of conflict/war news."""
        item = {
            'title': 'Military conflict escalates',
            'summary': 'Army attacks enemy positions',
            'description': 'War continues'
        }
        result = CategorizationService.categorize(item)
        assert result == 'conflict'

    def test_categorize_conflict_news_russian(self):
        """Test categorization of conflict news in Russian."""
        item = {
            'title': 'Военные действия продолжаются',
            'summary': 'Армия нанесла удар',
            'description': 'Конфликт обострился'
        }
        result = CategorizationService.categorize(item)
        assert result == 'conflict'

    def test_categorize_business_news(self):
        """Test categorization of business news."""
        item = {
            'title': 'Stock market rises',
            'summary': 'Company revenue increases',
            'description': 'Business growth'
        }
        result = CategorizationService.categorize(item)
        assert result == 'business'

    def test_categorize_business_news_russian(self):
        """Test categorization of business news in Russian."""
        item = {
            'title': 'Рынок акций растет',
            'summary': 'Компания увеличила прибыль',
            'description': 'Экономика развивается'
        }
        result = CategorizationService.categorize(item)
        assert result == 'business'

    def test_categorize_tech_news(self):
        """Test categorization of technology news."""
        item = {
            'title': 'AI breakthrough in machine learning',
            'summary': 'Neural network achieves new results',
            'description': 'Technology advances'
        }
        result = CategorizationService.categorize(item)
        assert result == 'tech'

    def test_categorize_tech_news_russian(self):
        """Test categorization of tech news in Russian."""
        item = {
            'title': 'Нейросеть создала новый алгоритм',
            'summary': 'Искусственный интеллект развивается',
            'description': 'Технологии будущего'
        }
        result = CategorizationService.categorize(item)
        assert result == 'tech'

    def test_categorize_science_news(self):
        """Test categorization of science news."""
        item = {
            'title': 'New scientific discovery',
            'summary': 'Research shows promising results',
            'description': 'University study published'
        }
        result = CategorizationService.categorize(item)
        assert result == 'science'

    def test_categorize_science_news_russian(self):
        """Test categorization of science news in Russian."""
        item = {
            'title': 'Ученые сделали открытие',
            'summary': 'Исследование в университете',
            'description': 'Научная работа опубликована'
        }
        result = CategorizationService.categorize(item)
        assert result == 'science'

    def test_categorize_society_news(self):
        """Test categorization of society news."""
        item = {
            'title': 'Social welfare program',
            'summary': 'People protest for rights',
            'description': 'Society demands change'
        }
        result = CategorizationService.categorize(item)
        assert result == 'society'

    def test_categorize_society_news_russian(self):
        """Test categorization of society news in Russian."""
        item = {
            'title': 'Социальные выплаты увеличились',
            'summary': 'Пенсионеры получили льготы',
            'description': 'Общество требует справедливости'
        }
        result = CategorizationService.categorize(item)
        assert result == 'society'

    def test_categorize_politics_news(self):
        """Test categorization of politics news."""
        item = {
            'title': 'President announces new policy',
            'summary': 'Government makes decision',
            'description': 'Election campaign begins'
        }
        result = CategorizationService.categorize(item)
        assert result == 'politics'

    def test_categorize_politics_news_russian(self):
        """Test categorization of politics news in Russian."""
        item = {
            'title': 'Президент выступил с заявлением',
            'summary': 'Правительство приняло решение',
            'description': 'Выборы начались'
        }
        result = CategorizationService.categorize(item)
        assert result == 'politics'

    def test_categorize_general_news(self):
        """Test categorization of general news (no specific category)."""
        item = {
            'title': 'Sunny day tomorrow',
            'summary': 'Nice weather coming',
            'description': 'Temperature will be pleasant'
        }
        result = CategorizationService.categorize(item)
        assert result == 'general'

    def test_categorize_empty_item(self):
        """Test categorization with empty item."""
        item = {}
        result = CategorizationService.categorize(item)
        assert result == 'general'

    def test_categorize_item_with_only_title(self):
        """Test categorization with only title."""
        item = {
            'title': 'Court case begins'
        }
        result = CategorizationService.categorize(item)
        assert result == 'legal'

    def test_categorize_item_with_empty_strings(self):
        """Test categorization with empty strings."""
        item = {
            'title': '',
            'summary': '',
            'description': ''
        }
        result = CategorizationService.categorize(item)
        assert result == 'general'

    def test_categorize_item_with_none_values(self):
        """Test categorization with None values."""
        item = {
            'title': None,
            'summary': None,
            'description': None
        }
        result = CategorizationService.categorize(item)
        assert result == 'general'

    def test_categorize_item_with_bytes(self):
        """Test categorization with bytes in item."""
        item = {
            'title': b'Court case',
            'summary': 'Legal proceedings',
            'description': 'Trial begins'
        }
        result = CategorizationService.categorize(item)
        # Should handle bytes and still categorize
        assert result in ['legal', 'general']

    def test_categorize_multiple_keywords_same_category(self):
        """Test categorization with multiple keywords in same category."""
        item = {
            'title': 'Court judge lawyer trial',
            'summary': 'Criminal case investigation',
            'description': 'Police arrest defendant'
        }
        result = CategorizationService.categorize(item)
        assert result == 'legal'

    def test_categorize_priority_legal_over_politics(self):
        """Test that legal category has priority over politics."""
        item = {
            'title': 'Court case about government policy',
            'summary': 'Judge rules on political matter',
            'description': 'Legal proceedings in parliament'
        }
        result = CategorizationService.categorize(item)
        # Legal should have priority (checked first)
        assert result == 'legal'

    def test_categorize_priority_conflict_over_politics(self):
        """Test that conflict category has priority over politics."""
        item = {
            'title': 'War and government response',
            'summary': 'Military action during election',
            'description': 'Conflict affects politics'
        }
        result = CategorizationService.categorize(item)
        # Conflict should have priority (checked second)
        assert result == 'conflict'

    def test_categorize_case_insensitive(self):
        """Test that categorization is case-insensitive."""
        item = {
            'title': 'COURT CASE',
            'summary': 'Judge Ruling',
            'description': 'LEGAL PROCEEDINGS'
        }
        result = CategorizationService.categorize(item)
        assert result == 'legal'

    def test_categorize_with_encoding_issues(self):
        """Test categorization handles encoding issues gracefully."""
        # Simulate encoding issues
        item = {
            'title': 'Р"РёРЅРѕРІР°С†РёРё',  # Potential mojibake
            'summary': 'Технологии',
            'description': 'Инновации'
        }
        result = CategorizationService.categorize(item)
        # Should not crash and return a category
        assert result in ['tech', 'general', 'legal', 'conflict',
                          'business', 'science', 'society', 'politics']
