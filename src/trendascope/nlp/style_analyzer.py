"""
Style analyzer for learning writing patterns from historical posts.
"""
import re
from typing import List, Dict, Any, Optional
from collections import Counter


class StyleAnalyzer:
    """Analyze and extract writing style from posts."""

    def __init__(self):
        """Initialize style analyzer."""
        self.style_features = {}

    def analyze_post(self, text: str) -> Dict[str, Any]:
        """
        Analyze a single post for style features.

        Args:
            text: Post text

        Returns:
            Dictionary with style features
        """
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        words = re.findall(r'\b\w+\b', text.lower())

        # Sentence structure
        avg_sentence_length = (
            len(words) / len(sentences) if sentences else 0
        )

        # Question frequency
        questions = len(re.findall(r'\?', text))
        question_ratio = questions / len(sentences) if sentences else 0

        # Exclamation frequency
        exclamations = len(re.findall(r'!', text))
        exclamation_ratio = (
            exclamations / len(sentences) if sentences else 0
        )

        # Quote frequency
        quotes = len(re.findall(r'«[^»]+»', text))
        quote_ratio = quotes / len(sentences) if sentences else 0

        # List/enumeration frequency
        lists = len(re.findall(r'\n\s*[-•]\s+', text))
        list_ratio = lists / len(sentences) if sentences else 0

        # Paragraph structure
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        avg_paragraph_length = len(sentences) / len(paragraphs) if paragraphs else 0

        # Common opening patterns
        openings = []
        for sent in sentences[:3]:
            words_in_sent = sent.split()[:3]
            if words_in_sent:
                openings.append(' '.join(words_in_sent))

        # Common phrases (2-3 word combinations)
        phrases = []
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            phrases.append(phrase)

        return {
            "avg_sentence_length": avg_sentence_length,
            "question_ratio": question_ratio,
            "exclamation_ratio": exclamation_ratio,
            "quote_ratio": quote_ratio,
            "list_ratio": list_ratio,
            "avg_paragraph_length": avg_paragraph_length,
            "openings": openings,
            "phrases": phrases,
            "total_words": len(words),
            "total_sentences": len(sentences)
        }

    def learn_style(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Learn writing style from multiple posts.

        Args:
            posts: List of posts with 'text_plain' field

        Returns:
            Aggregated style features
        """
        all_features = []
        all_openings = []
        all_phrases = []

        for post in posts:
            text = post.get('text_plain', '')
            if not text:
                continue

            features = self.analyze_post(text)
            all_features.append(features)
            all_openings.extend(features['openings'])
            all_phrases.extend(features['phrases'])

        if not all_features:
            return {}

        # Aggregate numeric features
        style = {
            "avg_sentence_length": sum(
                f['avg_sentence_length'] for f in all_features
            ) / len(all_features),
            "question_ratio": sum(
                f['question_ratio'] for f in all_features
            ) / len(all_features),
            "exclamation_ratio": sum(
                f['exclamation_ratio'] for f in all_features
            ) / len(all_features),
            "quote_ratio": sum(
                f['quote_ratio'] for f in all_features
            ) / len(all_features),
            "list_ratio": sum(
                f['list_ratio'] for f in all_features
            ) / len(all_features),
            "avg_paragraph_length": sum(
                f['avg_paragraph_length'] for f in all_features
            ) / len(all_features),
        }

        # Find common openings
        opening_counts = Counter(all_openings)
        style["common_openings"] = [
            op for op, _ in opening_counts.most_common(10)
        ]

        # Find common phrases
        phrase_counts = Counter(all_phrases)
        style["common_phrases"] = [
            phrase for phrase, _ in phrase_counts.most_common(20)
        ]

        self.style_features = style
        return style

    def get_style_examples(
        self,
        posts: List[Dict[str, Any]],
        max_examples: int = 5
    ) -> List[str]:
        """
        Extract representative style examples.

        Args:
            posts: List of posts
            max_examples: Maximum number of examples

        Returns:
            List of text excerpts
        """
        examples = []

        for post in posts[:max_examples]:
            text = post.get('text_plain', '')
            if not text:
                continue

            # Extract first 2-3 sentences
            sentences = re.split(r'[.!?]+', text)
            excerpt = '. '.join(
                s.strip() for s in sentences[:3] if s.strip()
            )

            if excerpt and len(excerpt) > 50:
                examples.append(excerpt + '.')

        return examples

    def generate_style_prompt(
        self,
        posts: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a prompt describing the writing style.

        Args:
            posts: List of posts to analyze

        Returns:
            Style description prompt
        """
        style = self.learn_style(posts)
        examples = self.get_style_examples(posts, max_examples=3)

        if not style:
            return "Пиши в нейтральном стиле."

        prompt_parts = ["Пиши в следующем стиле:"]

        # Describe sentence structure
        avg_len = style.get('avg_sentence_length', 0)
        if avg_len < 10:
            prompt_parts.append("- Короткие, рубленые предложения.")
        elif avg_len > 20:
            prompt_parts.append(
                "- Развёрнутые, сложные предложения."
            )
        else:
            prompt_parts.append("- Средние по длине предложения.")

        # Describe tone
        if style.get('question_ratio', 0) > 0.2:
            prompt_parts.append("- Часто используй вопросы.")

        if style.get('exclamation_ratio', 0) > 0.15:
            prompt_parts.append("- Эмоциональный, экспрессивный тон.")

        if style.get('quote_ratio', 0) > 0.1:
            prompt_parts.append("- Используй цитаты и кавычки.")

        if style.get('list_ratio', 0) > 0.1:
            prompt_parts.append("- Структурируй текст списками.")

        # Add examples
        if examples:
            prompt_parts.append("\nПримеры стиля:")
            for ex in examples:
                prompt_parts.append(f"«{ex}»")

        return '\n'.join(prompt_parts)


# Global analyzer instance
_style_analyzer = None


def get_style_analyzer() -> StyleAnalyzer:
    """Get or create global style analyzer."""
    global _style_analyzer
    if _style_analyzer is None:
        _style_analyzer = StyleAnalyzer()
    return _style_analyzer


def analyze_style(posts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze writing style from posts."""
    return get_style_analyzer().learn_style(posts)


def get_style_prompt(posts: List[Dict[str, Any]]) -> str:
    """Generate style prompt from posts."""
    return get_style_analyzer().generate_style_prompt(posts)

