"""
NLP analysis pipeline.
Extracts topics, sentiment, entities, and keywords.
"""
import re
from typing import List, Dict, Any, Optional

try:
    from keybert import KeyBERT
except ImportError:
    KeyBERT = None

try:
    import yake
except ImportError:
    yake = None


class TextAnalyzer:
    """Analyze text for topics, sentiment, entities, and keywords."""

    def __init__(self):
        """Initialize analyzer with models."""
        self.keyword_extractor = None
        if KeyBERT:
            try:
                self.keyword_extractor = KeyBERT(model='all-MiniLM-L6-v2')
            except Exception:
                pass

        self.yake_extractor = None
        if yake:
            try:
                self.yake_extractor = yake.KeywordExtractor(
                    lan="ru",
                    n=3,
                    dedupLim=0.9,
                    top=20
                )
            except Exception:
                pass

    def extract_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract keywords from text.

        Args:
            text: Input text
            top_n: Number of top keywords to return

        Returns:
            List of keyword dictionaries with text and score
        """
        keywords = []

        # Try KeyBERT first
        if self.keyword_extractor:
            try:
                kw = self.keyword_extractor.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 3),
                    top_n=top_n,
                    stop_words='russian'
                )
                keywords = [
                    {"text": k[0], "score": float(k[1])}
                    for k in kw
                ]
            except Exception:
                pass

        # Fallback to YAKE
        if not keywords and self.yake_extractor:
            try:
                kw = self.yake_extractor.extract_keywords(text)
                keywords = [
                    {"text": k[0], "score": 1.0 - float(k[1])}
                    for k in kw[:top_n]
                ]
            except Exception:
                pass

        # Fallback to simple word frequency
        if not keywords:
            keywords = self._simple_keywords(text, top_n)

        return keywords

    def _simple_keywords(
        self,
        text: str,
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple keyword extraction using word frequency."""
        # Remove punctuation and lowercase
        words = re.findall(r'\b\w+\b', text.lower())

        # Filter short words and stop words
        stop_words = {
            'и', 'в', 'не', 'на', 'с', 'по', 'для', 'как', 'это',
            'что', 'же', 'к', 'у', 'из', 'о', 'от', 'до', 'при',
            'а', 'но', 'или', 'да', 'нет', 'так', 'вот', 'только'
        }
        words = [w for w in words if len(w) > 3 and w not in stop_words]

        # Count frequencies
        freq = {}
        for word in words:
            freq[word] = freq.get(word, 0) + 1

        # Sort by frequency
        sorted_words = sorted(
            freq.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [
            {"text": word, "score": count / len(words)}
            for word, count in sorted_words[:top_n]
        ]

    def detect_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Detect sentiment in text.

        Args:
            text: Input text

        Returns:
            Dictionary with sentiment label and score
        """
        # Simple rule-based sentiment for Russian
        positive_words = {
            'хорошо', 'отлично', 'прекрасно', 'замечательно',
            'великолепно', 'радость', 'счастье', 'успех',
            'победа', 'любовь', 'красиво', 'интересно'
        }
        negative_words = {
            'плохо', 'ужасно', 'кошмар', 'беда', 'провал',
            'неудача', 'грусть', 'печаль', 'страх', 'боль',
            'опасно', 'скучно', 'глупо'
        }

        words = set(re.findall(r'\b\w+\b', text.lower()))

        pos_count = len(words & positive_words)
        neg_count = len(words & negative_words)

        total = pos_count + neg_count
        if total == 0:
            return {"label": "neutral", "score": 0.0}

        pos_score = pos_count / total
        neg_score = neg_count / total

        if pos_score > neg_score:
            return {"label": "positive", "score": pos_score}
        elif neg_score > pos_score:
            return {"label": "negative", "score": neg_score}
        else:
            return {"label": "neutral", "score": 0.5}

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.

        Args:
            text: Input text

        Returns:
            List of entity dictionaries
        """
        # Simple entity extraction using capitalization patterns
        entities = []

        # Find capitalized sequences
        pattern = r'\b[А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*\b'
        matches = re.finditer(pattern, text)

        seen = set()
        for match in matches:
            entity_text = match.group(0)
            if entity_text not in seen and len(entity_text) > 3:
                entities.append({
                    "text": entity_text,
                    "type": "UNKNOWN",
                    "start": match.start(),
                    "end": match.end()
                })
                seen.add(entity_text)

        return entities

    def calculate_readability(self, text: str) -> Dict[str, Any]:
        """
        Calculate readability metrics.

        Args:
            text: Input text

        Returns:
            Dictionary with readability metrics
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = re.findall(r'\b\w+\b', text)

        if not sentences or not words:
            return {
                "words": 0,
                "sentences": 0,
                "avg_words_per_sentence": 0.0,
                "avg_word_length": 0.0
            }

        avg_words_per_sentence = len(words) / len(sentences)
        avg_word_length = sum(len(w) for w in words) / len(words)

        return {
            "words": len(words),
            "sentences": len(sentences),
            "avg_words_per_sentence": round(avg_words_per_sentence, 2),
            "avg_word_length": round(avg_word_length, 2)
        }

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Full text analysis.

        Args:
            text: Input text

        Returns:
            Dictionary with all analysis results
        """
        return {
            "keywords": self.extract_keywords(text),
            "sentiment": self.detect_sentiment(text),
            "entities": self.extract_entities(text),
            "readability": self.calculate_readability(text)
        }


# Global analyzer instance
_analyzer = None


def get_analyzer() -> TextAnalyzer:
    """Get or create global analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = TextAnalyzer()
    return _analyzer


def analyze_text(text: str) -> Dict[str, Any]:
    """Analyze text using global analyzer."""
    return get_analyzer().analyze(text)

