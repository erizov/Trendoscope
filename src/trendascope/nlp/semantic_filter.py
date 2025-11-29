"""
Semantic topic filtering using sentence embeddings.
Filters news by semantic similarity instead of keywords.
"""
from typing import List, Dict, Any, Optional
import numpy as np


class SemanticTopicFilter:
    """Filter news by semantic similarity to topics."""
    
    # Rich topic descriptions for semantic matching
    TOPIC_DESCRIPTIONS = {
        "ai": """
            Искусственный интеллект, нейронные сети, машинное обучение,
            глубокое обучение, большие языковые модели, ChatGPT, GPT,
            автоматизация, роботы, автономные системы, компьютерное зрение,
            обработка естественного языка, этика ИИ, AGI,
            влияние технологий на общество, цифровизация,
            artificial intelligence, neural networks, machine learning,
            deep learning, LLM, automation, robots
        """,
        
        "politics": """
            Политика, геополитика, международные отношения,
            дипломатия, выборы, правительство, парламент, власть,
            государство, законодательство, референдум, санкции,
            внешняя политика, внутренняя политика, оппозиция,
            politics, geopolitics, international relations,
            diplomacy, elections, government, parliament, power
        """,
        
        "us_affairs": """
            США, Америка, американская политика, Вашингтон,
            Белый дом, Конгресс, Сенат, президент США,
            Демократы, Республиканцы, Трамп, Байден,
            американские выборы, внешняя политика США,
            Пентагон, ЦРУ, ФБР, американская экономика,
            USA, America, American politics, Washington,
            White House, Congress, Senate, US president
        """,
        
        "russian_history": """
            Россия, российская история, СССР, Советский Союз,
            российская политика, история России, исторические параллели,
            Петербург, Москва, Кремль, российская власть,
            советская эпоха, постсоветское пространство,
            российская культура, русская история,
            Russia, Russian history, USSR, Soviet Union,
            Russian politics, historical parallels
        """,
        
        "science": """
            Наука, научные исследования, научные открытия,
            технологии, космос, физика, биология, химия,
            медицина, эксперимент, исследование, ученые,
            научный прогресс, инновации, технологический прорыв,
            science, research, scientific discoveries,
            technology, space, physics, biology, innovation
        """,
        
        "any": """
            Любые темы, все новости, общие события,
            актуальные новости, текущие события
        """
    }
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
        """
        Initialize semantic filter.
        
        Args:
            model_name: Sentence transformer model name
        """
        self.model = None
        self.model_name = model_name
        self.topic_embeddings = {}
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize sentence transformer model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(self.model_name)
            
            # Pre-compute topic embeddings
            for topic, description in self.TOPIC_DESCRIPTIONS.items():
                self.topic_embeddings[topic] = self.model.encode(
                    description,
                    convert_to_numpy=True
                )
        except ImportError:
            # Fallback if sentence-transformers not available
            self.model = None
    
    def filter_by_topic(
        self,
        news_items: List[Dict[str, Any]],
        topic: str,
        threshold: float = 0.3,
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Filter news by semantic similarity to topic.
        
        Args:
            news_items: List of news items
            topic: Topic name
            threshold: Minimum similarity score (0-1)
            top_k: Return only top K items (optional)
        
        Returns:
            Filtered and scored news items
        """
        if topic == "any" or not self.model:
            return news_items
        
        if topic not in self.topic_embeddings:
            # Unknown topic, return all
            return news_items
        
        topic_emb = self.topic_embeddings[topic]
        filtered = []
        
        for item in news_items:
            # Combine title and summary
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            
            if not text.strip():
                continue
            
            # Encode text
            text_emb = self.model.encode(text, convert_to_numpy=True)
            
            # Calculate cosine similarity
            similarity = self._cosine_similarity(topic_emb, text_emb)
            
            if similarity >= threshold:
                item_copy = item.copy()
                item_copy['topic_relevance'] = float(similarity)
                filtered.append(item_copy)
        
        # Sort by relevance
        filtered.sort(key=lambda x: x['topic_relevance'], reverse=True)
        
        # Return top K if specified
        if top_k:
            return filtered[:top_k]
        
        return filtered
    
    def _cosine_similarity(
        self,
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm_product = np.linalg.norm(vec1) * np.linalg.norm(vec2)
        
        if norm_product == 0:
            return 0.0
        
        return dot_product / norm_product
    
    def get_topic_scores(
        self,
        news_item: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Get similarity scores for all topics.
        
        Args:
            news_item: Single news item
        
        Returns:
            Dictionary of topic -> score
        """
        if not self.model:
            return {}
        
        text = f"{news_item.get('title', '')} {news_item.get('summary', '')}"
        
        if not text.strip():
            return {}
        
        text_emb = self.model.encode(text, convert_to_numpy=True)
        
        scores = {}
        for topic, topic_emb in self.topic_embeddings.items():
            if topic != "any":
                scores[topic] = float(
                    self._cosine_similarity(topic_emb, text_emb)
                )
        
        return scores
    
    def rank_news_by_topics(
        self,
        news_items: List[Dict[str, Any]],
        topics: List[str]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Rank news items for multiple topics.
        
        Args:
            news_items: List of news items
            topics: List of topic names
        
        Returns:
            Dictionary of topic -> ranked news list
        """
        results = {}
        
        for topic in topics:
            if topic in self.topic_embeddings:
                filtered = self.filter_by_topic(news_items, topic)
                results[topic] = filtered
        
        return results


def filter_news_by_topic_semantic(
    news_items: List[Dict[str, Any]],
    topic: str,
    threshold: float = 0.3,
    top_k: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function for semantic filtering.
    
    Args:
        news_items: List of news items
        topic: Topic name
        threshold: Minimum similarity score
        top_k: Maximum items to return
    
    Returns:
        Filtered news items
    """
    filter_obj = SemanticTopicFilter()
    return filter_obj.filter_by_topic(news_items, topic, threshold, top_k)


def hybrid_filter(
    news_items: List[Dict[str, Any]],
    topic: str,
    use_semantic: bool = True,
    use_keywords: bool = True,
    semantic_threshold: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Hybrid filtering using both semantic and keyword approaches.
    
    Args:
        news_items: List of news items
        topic: Topic name
        use_semantic: Use semantic filtering
        use_keywords: Use keyword filtering
        semantic_threshold: Threshold for semantic matching
    
    Returns:
        Combined filtered results
    """
    results = set()
    
    # Semantic filtering
    if use_semantic:
        semantic_filter = SemanticTopicFilter()
        semantic_results = semantic_filter.filter_by_topic(
            news_items,
            topic,
            threshold=semantic_threshold
        )
        results.update(item['link'] for item in semantic_results if 'link' in item)
    
    # Keyword filtering (fallback)
    if use_keywords:
        from ..gen.post_generator import _filter_news_by_topic
        keyword_results = _filter_news_by_topic(news_items, topic)
        results.update(item['link'] for item in keyword_results if 'link' in item)
    
    # Return all items that matched either method
    return [
        item for item in news_items
        if item.get('link') in results
    ]

