"""
Trend engine for tracking topic popularity and growth.
"""
from typing import List, Dict, Any, Optional
from collections import Counter, defaultdict
from datetime import datetime, timedelta


class TrendEngine:
    """Track and analyze trending topics."""

    def __init__(self):
        """Initialize trend engine."""
        self.topic_history = defaultdict(list)

    def extract_topics_from_posts(
        self,
        posts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract topics from posts.

        Args:
            posts: List of posts with analysis

        Returns:
            List of topic dictionaries
        """
        topic_counts = Counter()
        topic_posts = defaultdict(list)

        for post in posts:
            # Get keywords from NLP analysis
            analysis = post.get('analysis', {})
            keywords = analysis.get('keywords', [])

            for kw in keywords:
                topic = kw['text']
                score = kw.get('score', 0)

                topic_counts[topic] += score
                topic_posts[topic].append(post)

            # Also extract from tags
            tags = post.get('tags', [])
            for tag in tags:
                topic_counts[tag] += 1.0
                topic_posts[tag].append(post)

        # Build topic list
        topics = []
        for topic, score in topic_counts.most_common(50):
            topics.append({
                "topic": topic,
                "score": score,
                "post_count": len(topic_posts[topic]),
                "posts": topic_posts[topic]
            })

        return topics

    def calculate_trend_slope(
        self,
        topic: str,
        window_days: int = 7
    ) -> float:
        """
        Calculate trend slope (growth rate).

        Args:
            topic: Topic name
            window_days: Time window in days

        Returns:
            Trend slope (positive = growing, negative = declining)
        """
        history = self.topic_history.get(topic, [])
        if len(history) < 2:
            return 0.0

        # Get recent history
        cutoff = datetime.now() - timedelta(days=window_days)
        recent = [
            h for h in history
            if datetime.fromisoformat(h['timestamp']) > cutoff
        ]

        if len(recent) < 2:
            return 0.0

        # Simple linear regression
        scores = [h['score'] for h in recent]
        n = len(scores)

        if n == 0:
            return 0.0

        # Calculate slope
        x_mean = n / 2
        y_mean = sum(scores) / n

        numerator = sum(
            (i - x_mean) * (scores[i] - y_mean)
            for i in range(n)
        )
        denominator = sum(
            (i - x_mean) ** 2
            for i in range(n)
        )

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def calculate_viral_potential(
        self,
        post: Dict[str, Any],
        topics: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Calculate viral potential score.

        Args:
            post: Post dictionary
            topics: List of trending topics

        Returns:
            Viral potential dictionary
        """
        score = 0.0
        factors = []

        # Factor 1: Content length (optimal range)
        text = post.get('text_plain', '')
        word_count = len(text.split())

        if 300 <= word_count <= 1500:
            length_score = 0.2
            factors.append("Оптимальная длина текста")
        elif word_count < 300:
            length_score = 0.1
            factors.append("Короткий текст")
        else:
            length_score = 0.15
            factors.append("Длинный текст")

        score += length_score

        # Factor 2: Trending topics
        analysis = post.get('analysis', {})
        keywords = analysis.get('keywords', [])
        keyword_texts = [kw['text'] for kw in keywords]

        trending_topics = [t['topic'] for t in topics[:10]]
        overlap = len(set(keyword_texts) & set(trending_topics))

        if overlap > 0:
            topic_score = min(0.3, overlap * 0.1)
            score += topic_score
            factors.append(f"Содержит {overlap} трендовых тем")

        # Factor 3: Sentiment
        sentiment = analysis.get('sentiment', {})
        if sentiment.get('label') in ['positive', 'negative']:
            score += 0.15
            factors.append("Эмоциональный окрас")

        # Factor 4: Engagement signals
        comments = post.get('comments_count', 0)
        if comments > 10:
            engagement_score = min(0.2, comments / 100)
            score += engagement_score
            factors.append(f"{comments} комментариев")

        # Factor 5: Questions and lists
        readability = analysis.get('readability', {})
        sentences = readability.get('sentences', 0)

        if '?' in text:
            questions = text.count('?')
            if questions > 0:
                score += 0.1
                factors.append("Содержит вопросы")

        # Normalize score
        score = min(1.0, score)

        # Determine label
        if score >= 0.7:
            label = "high"
        elif score >= 0.4:
            label = "medium"
        else:
            label = "low"

        return {
            "label": label,
            "score": round(score, 2),
            "factors": factors,
            "why": "; ".join(factors)
        }

    def update_topic_history(
        self,
        topics: List[Dict[str, Any]]
    ) -> None:
        """
        Update topic history for trend tracking.

        Args:
            topics: List of topics with scores
        """
        timestamp = datetime.now().isoformat()

        for topic in topics:
            self.topic_history[topic['topic']].append({
                "timestamp": timestamp,
                "score": topic['score'],
                "post_count": topic['post_count']
            })

    def get_trending_topics(
        self,
        posts: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get currently trending topics.

        Args:
            posts: List of analyzed posts
            top_n: Number of top topics to return

        Returns:
            List of trending topics with metadata
        """
        topics = self.extract_topics_from_posts(posts)

        # Calculate trend slopes
        for topic in topics:
            slope = self.calculate_trend_slope(topic['topic'])
            topic['trend_slope'] = slope
            topic['trending'] = slope > 0

        # Sort by score and trend
        topics.sort(
            key=lambda t: (t['score'], t['trend_slope']),
            reverse=True
        )

        # Update history
        self.update_topic_history(topics)

        return topics[:top_n]


# Global engine instance
_engine = None


def get_trend_engine() -> TrendEngine:
    """Get or create global trend engine."""
    global _engine
    if _engine is None:
        _engine = TrendEngine()
    return _engine


def get_trending_topics(
    posts: List[Dict[str, Any]],
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """Get trending topics from posts."""
    return get_trend_engine().get_trending_topics(posts, top_n)


def calculate_viral_potential(
    post: Dict[str, Any],
    topics: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate viral potential for a post."""
    return get_trend_engine().calculate_viral_potential(post, topics)

