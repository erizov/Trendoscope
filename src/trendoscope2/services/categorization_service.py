"""
News categorization service.
Categorizes news items based on content analysis using keyword matching.
"""
import logging
from typing import Dict, Any
from ..utils.encoding import safe_str

logger = logging.getLogger(__name__)


class CategorizationService:
    """Service for categorizing news items."""
    
    # Legal & Criminal (courts, law, crime, justice) - проверяем первым
    LEGAL_KEYWORDS = [
        'court', 'judge', 'lawyer', 'attorney', 'trial', 'verdict',
        'sentenced', 'conviction', 'criminal', 'crime', 'arrest', 'police',
        'investigation', 'lawsuit', 'legal', 'justice', 'prison', 'jail',
        'prosecutor', 'defendant', 'case', 'ruling',
        'суд', 'судья', 'адвокат', 'прокурор', 'приговор', 'уголовн',
        'преступ', 'полиц', 'следств', 'дело', 'обвинение', 'оправдан',
        'тюрьма', 'арест', 'юрист', 'право', 'закон', 'нарушение',
        'расследование', 'обыск', 'задержан', 'подозреваем', 'обвиняем',
        'штраф', 'наказание', 'судопроизводство'
    ]
    
    # War & Conflict - проверяем вторым (более специфично)
    CONFLICT_KEYWORDS = [
        'war', 'military', 'army', 'weapon', 'conflict', 'attack', 'defense',
        'battle', 'война', 'военн', 'армия', 'оружи', 'конфликт', 'удар',
        'атак', 'оборон', 'бой', 'сражение', 'вооружен', 'войск', 'солдат',
        'фронт', 'наступление', 'обстрел', 'ракет', 'бомбардировк', 'санкц',
        'санкции', 'sanction'
    ]
    
    # Business & Economy - расширенные ключевые слова
    BUSINESS_KEYWORDS = [
        'market', 'stock', 'stock market', 'economy', 'economic', 'business',
        'company', 'corporation', 'trading', 'trade', 'investment', 'investor',
        'ceo', 'cfo', 'revenue', 'profit', 'loss',
        'бизнес', 'компани', 'корпорац', 'рынок', 'фондов', 'экономик',
        'экономика', 'инвестиц', 'инвестор', 'акци', 'акции', 'финанс',
        'финансы', 'банк', 'банки', 'валют', 'доллар', 'евро', 'рубл',
        'рубль', 'курс', 'обмен', 'обменн', 'инфляц', 'инфляция',
        'безработиц', 'безработица', 'gdp', 'ввп', 'recession', 'depression',
        'crisis', 'кризис', 'рецессия', 'торговл', 'торговля', 'экспорт',
        'импорт', 'производств', 'производство', 'завод', 'предприяти',
        'предприятие', 'бюджет', 'налог', 'налоги', 'налогообложен'
    ]
    
    # Tech (AI, ML, technology, platforms, internet)
    TECH_KEYWORDS = [
        'ai', 'artificial', 'intelligence', 'gpt', 'neural', 'machine',
        'learning', 'tech', 'technology', 'algorithm', 'data', 'digital',
        'internet', 'platform', 'cloud', 'software', 'app',
        'ии', 'нейросет', 'технолог', 'алгоритм', 'данные', 'telegram',
        'google', 'microsoft', 'apple', 'meta', 'программ', 'код',
        'chatbot', 'chat', 'robot', 'робот', 'автоматизац', 'кибер', 'cyber'
    ]
    
    # Science & Research - расширенные ключевые слова
    SCIENCE_KEYWORDS = [
        'science', 'research', 'study', 'university', 'scientist', 'discovery',
        'наука', 'исследован', 'ученые', 'университет', 'открыти',
        'experiment', 'climate', 'energy', 'environment', 'климат', 'энергия',
        'экология', 'медицин', 'лекарств', 'лечение', 'болезн', 'вирус',
        'вакцин', 'космос', 'space', 'mars', 'марс', 'ракет', 'спутник',
        'satellite', 'физик', 'хими', 'биолог', 'генетик', 'dna', 'ген'
    ]
    
    # Society (social issues, people, rights)
    SOCIETY_KEYWORDS = [
        'social', 'people', 'society', 'protest', 'demonstration', 'rights',
        'human rights', 'welfare', 'социальн', 'общество', 'социальная',
        'люди', 'права', 'справедлив', 'справедливость', 'пенси', 'пенсия',
        'пенсионер', 'пенсионеры', 'льгот', 'льгота', 'выплат', 'выплата',
        'миграц', 'миграция', 'беженц', 'беженец', 'демографи', 'демография',
        'население', 'образование', 'школ', 'школа', 'университет', 'студент',
        'учитель', 'education', 'здравоохранение', 'больниц', 'больница',
        'врач', 'медицин', 'медицина', 'здоровье', 'культур', 'культура',
        'искусств', 'искусство', 'театр', 'кино', 'музей'
    ]
    
    # Politics (general, any country) - проверяем последним
    POLITICS_KEYWORDS = [
        'politics', 'government', 'election', 'president', 'minister',
        'congress', 'политик', 'правительств', 'выборы', 'президент',
        'министр', 'партия', 'biden', 'trump', 'putin', 'путин', 'parliament',
        'senate', 'кремль', 'белый дом', 'white house', 'госдум', 'дум',
        'сенат', 'конгресс', 'депутат', 'депутаты', 'законодательств',
        'законодатель', 'политическ', 'власть', 'власт', 'администрац',
        'администрация', 'кабинет', 'кабинет министров', 'премьер',
        'премьер-министр', 'глава', 'руководитель', 'лидер', 'лидеры',
        'оппозиц', 'оппозиция', 'фракц', 'фракция', 'коалиц', 'коалиция',
        'реформа', 'реформы', 'законопроект', 'законопроекты', 'голосован',
        'голосование', 'избирательн', 'избирательный', 'кампания', 'кампании',
        'кандидат', 'кандидаты'
    ]
    
    @classmethod
    def categorize(cls, item: Dict[str, Any]) -> str:
        """
        Categorize news item based on content - 8 main categories.
        
        Args:
            item: News item dictionary with title, summary, description
            
        Returns:
            Category name: 'legal', 'conflict', 'business', 'tech',
            'science', 'society', 'politics', or 'general'
        """
        try:
            title = safe_str(item.get('title', ''))
            summary = safe_str(item.get('summary', ''))
            description = safe_str(item.get('description', ''))
            
            # Combine text
            text = f"{title} {summary} {description}"
            
            # Ensure UTF-8 and convert to lowercase safely
            if isinstance(text, bytes):
                try:
                    text = text.decode('utf-8')
                except UnicodeDecodeError:
                    text = text.decode('utf-8', errors='replace')
            
            # Convert to lowercase safely (handles Cyrillic)
            text = text.lower()
            
            # Ensure we have text to categorize
            if not text or len(text.strip()) == 0:
                logger.warning(
                    f"Empty text for categorization, "
                    f"item: {item.get('title', 'no title')[:50]}"
                )
                return 'general'
        except (UnicodeDecodeError, UnicodeEncodeError, AttributeError, TypeError) as e:
            # Fallback: use only title if encoding fails
            logger.warning(
                f"Encoding error in categorization: {e}, "
                f"item keys: {list(item.keys())}"
            )
            try:
                text = safe_str(item.get('title', '')).lower()
                if not text or len(text.strip()) == 0:
                    return 'general'
            except Exception:
                return 'general'
        
        # Check categories using keyword matching with scoring
        def count_matches(keywords, text):
            """Count how many keywords match in text."""
            return sum(1 for kw in keywords if kw in text)
        
        legal_matches = count_matches(cls.LEGAL_KEYWORDS, text)
        conflict_matches = count_matches(cls.CONFLICT_KEYWORDS, text)
        business_matches = count_matches(cls.BUSINESS_KEYWORDS, text)
        science_matches = count_matches(cls.SCIENCE_KEYWORDS, text)
        society_matches = count_matches(cls.SOCIETY_KEYWORDS, text)
        tech_matches = count_matches(cls.TECH_KEYWORDS, text)
        politics_matches = count_matches(cls.POLITICS_KEYWORDS, text)
        
        # Find category with maximum matches
        category_scores = {
            'legal': legal_matches,
            'conflict': conflict_matches,
            'business': business_matches,
            'science': science_matches,
            'society': society_matches,
            'tech': tech_matches,
            'politics': politics_matches
        }
        
        # If there are matches, return category with highest score
        max_score = max(category_scores.values())
        if max_score > 0:
            # If multiple categories have same max, choose by priority
            for category in [
                'legal', 'conflict', 'business', 'science', 'society',
                'tech', 'politics'
            ]:
                if category_scores[category] == max_score:
                    return category
        
        # If no matches, return general
        return 'general'
