"""
Controversy scorer for news items.
Calculates provocation and engagement potential.
"""
from typing import Dict, Any, List
import re


class ControversyScorer:
    """Score news items for controversy and provocation."""
    
    # Controversial keywords and their weights
    CONTROVERSIAL_KEYWORDS = {
        # Politics
        'война': 3, 'санкции': 2, 'путин': 2, 'байден': 2, 'трамп': 3,
        'выборы': 2, 'скандал': 3, 'коррупция': 3, 'протест': 2,
        'революция': 3, 'переворот': 3, 'кризис': 2,
        
        # AI/Tech
        'заменит': 3, 'угроза': 2, 'конец': 3, 'смерть': 3,
        'опасность': 2, 'запрет': 2, 'цензура': 2,
        
        # Economy
        'крах': 3, 'обвал': 3, 'дефолт': 3, 'инфляция': 2,
        
        # Strong language
        'шок': 2, 'сенсация': 2, 'скандал': 3, 'провал': 2,
        
        # English equivalents
        'war': 3, 'scandal': 3, 'crisis': 2, 'threat': 2,
        'ban': 2, 'collapse': 3, 'death': 3, 'end': 2,
    }
    
    # Provocative patterns
    PROVOCATIVE_PATTERNS = [
        r'\?$',  # Ends with question
        r'!{2,}',  # Multiple exclamation marks
        r'[А-ЯA-Z]{3,}',  # CAPS words
        r'vs\.?|против',  # Versus/against
        r'но |однако ',  # Contrasts
        r'пора|время',  # Time pressure
        r'почему|зачем|как так',  # Why questions
    ]
    
    def __init__(self):
        """Initialize scorer."""
        pass
    
    def score_news(self, news_item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score a single news item for controversy.
        
        Args:
            news_item: News dictionary with title, summary, etc.
        
        Returns:
            Scored item with controversy metrics
        """
        title = news_item.get('title', '').lower()
        summary = news_item.get('summary', '').lower()
        text = f"{title} {summary}"
        
        # Calculate individual scores
        keyword_score = self._keyword_score(text)
        pattern_score = self._pattern_score(text)
        length_score = self._length_score(summary)
        question_score = self._question_score(text)
        emotion_score = self._emotion_score(text)
        
        # Weighted total (0-100)
        total_score = int(
            keyword_score * 0.3 +
            pattern_score * 0.25 +
            question_score * 0.2 +
            emotion_score * 0.15 +
            length_score * 0.1
        )
        
        # Determine label
        if total_score >= 75:
            label = 'explosive'
            emoji = '💥'
        elif total_score >= 60:
            label = 'hot'
            emoji = '🔥'
        elif total_score >= 40:
            label = 'spicy'
            emoji = '🌶️'
        else:
            label = 'mild'
            emoji = '📰'
        
        return {
            **news_item,
            'controversy': {
                'score': total_score,
                'label': label,
                'emoji': emoji,
                'breakdown': {
                    'keywords': keyword_score,
                    'patterns': pattern_score,
                    'questions': question_score,
                    'emotion': emotion_score,
                    'length': length_score
                }
            },
            'is_hot': total_score >= 60
        }
    
    def score_batch(
        self,
        news_items: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Score multiple news items."""
        return [self.score_news(item) for item in news_items]
    
    def _keyword_score(self, text: str) -> float:
        """Score based on controversial keywords."""
        score = 0
        for keyword, weight in self.CONTROVERSIAL_KEYWORDS.items():
            if keyword in text:
                score += weight
        
        # Normalize to 0-100
        return min(100, score * 10)
    
    def _pattern_score(self, text: str) -> float:
        """Score based on provocative patterns."""
        score = 0
        for pattern in self.PROVOCATIVE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                score += 15
        
        return min(100, score)
    
    def _length_score(self, text: str) -> float:
        """Score based on optimal length (shorter = more provocative)."""
        length = len(text)
        
        if length < 100:
            return 100
        elif length < 200:
            return 80
        elif length < 300:
            return 60
        else:
            return 40
    
    def _question_score(self, text: str) -> float:
        """Score based on question usage."""
        questions = text.count('?')
        
        if questions >= 2:
            return 100
        elif questions == 1:
            return 70
        else:
            return 30
    
    def _emotion_score(self, text: str) -> float:
        """Score based on emotional language."""
        emotional_words = [
            'шок', 'ужас', 'скандал', 'сенсация', 'невероятн',
            'катастроф', 'триумф', 'провал', 'позор',
            'shock', 'scandal', 'amazing', 'terrible', 'disaster'
        ]
        
        score = sum(15 for word in emotional_words if word in text.lower())
        return min(100, score)


def score_controversy(
    news_item: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function to score a single news item.
    
    Args:
        news_item: News dictionary
    
    Returns:
        Scored news item
    """
    scorer = ControversyScorer()
    return scorer.score_news(news_item)

