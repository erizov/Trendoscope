"""
Author style RAG system.
Loads and indexes texts from classic authors for style-based generation.
Uses free/public domain sources.
"""
import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Author definitions with public domain sources
AUTHORS = {
    "tolstoy": {
        "name": "Лев Толстой",
        "english_name": "Leo Tolstoy",
        "sources": [
            # Project Gutenberg and other free sources
            "https://www.gutenberg.org/files/2600/2600-0.txt",  # War and Peace (excerpt)
            "https://www.gutenberg.org/files/1399/1399-0.txt",  # Anna Karenina (excerpt)
        ],
        "style_keywords": [
            "философский", "нравственный", "психологический", "детальный",
            "моральный", "религиозный", "социальный", "исторический"
        ]
    },
    "dostoevsky": {
        "name": "Фёдор Достоевский",
        "english_name": "Fyodor Dostoevsky",
        "sources": [
            "https://www.gutenberg.org/files/28054/28054-0.txt",  # Crime and Punishment (excerpt)
            "https://www.gutenberg.org/files/8117/8117-0.txt",  # The Brothers Karamazov (excerpt)
        ],
        "style_keywords": [
            "психологический", "философский", "экзистенциальный", "моральный",
            "интроспективный", "драматический", "глубокий", "душевный"
        ]
    },
    "pushkin": {
        "name": "Александр Пушкин",
        "english_name": "Alexander Pushkin",
        "sources": [
            "https://www.gutenberg.org/files/23900/23900-0.txt",  # Eugene Onegin
            "https://www.gutenberg.org/files/27367/27367-0.txt",  # Selected works
        ],
        "style_keywords": [
            "поэтический", "элегантный", "классический", "романтический",
            "ироничный", "легкий", "музыкальный", "изысканный"
        ]
    },
    "lermontov": {
        "name": "Михаил Лермонтов",
        "english_name": "Mikhail Lermontov",
        "sources": [
            "https://www.gutenberg.org/files/22456/22456-0.txt",  # A Hero of Our Time
        ],
        "style_keywords": [
            "романтический", "меланхоличный", "бунтарский", "поэтический",
            "интроспективный", "эмоциональный", "страстный", "философский"
        ]
    },
    "turgenev": {
        "name": "Иван Тургенев",
        "english_name": "Ivan Turgenev",
        "sources": [
            "https://www.gutenberg.org/files/3075/3075-0.txt",  # Fathers and Sons
            "https://www.gutenberg.org/files/13437/13437-0.txt",  # Selected works
        ],
        "style_keywords": [
            "лирический", "описательный", "элегантный", "тонкий",
            "психологический", "социальный", "романтический", "реалистичный"
        ]
    },
    "leskov": {
        "name": "Николай Лесков",
        "english_name": "Nikolai Leskov",
        "sources": [
            "https://www.gutenberg.org/files/13438/13438-0.txt",  # Selected works
        ],
        "style_keywords": [
            "народный", "сказочный", "юмористический", "сатирический",
            "фольклорный", "живой", "образный", "народный"
        ]
    },
    "mark_twain": {
        "name": "Mark Twain",
        "english_name": "Mark Twain",
        "sources": [
            "https://www.gutenberg.org/files/74/74-0.txt",  # Adventures of Huckleberry Finn
            "https://www.gutenberg.org/files/76/76-0.txt",  # Adventures of Tom Sawyer
        ],
        "style_keywords": [
            "humorous", "satirical", "witty", "conversational",
            "realistic", "folksy", "ironic", "observant"
        ]
    },
    "faulkner": {
        "name": "William Faulkner",
        "english_name": "William Faulkner",
        "sources": [
            "https://www.gutenberg.org/files/1400/1400-0.txt",  # Selected works
        ],
        "style_keywords": [
            "stream_of_consciousness", "complex", "southern", "psychological",
            "experimental", "dense", "lyrical", "modernist"
        ]
    }
}


class AuthorStyleRAG:
    """RAG system for author style-based generation."""
    
    def __init__(self, storage_path: str = "data/author_rag"):
        """
        Initialize author style RAG.
        
        Args:
            storage_path: Path to store indexed texts
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.author_texts: Dict[str, List[Dict[str, Any]]] = {}
        self._load_cached_texts()
    
    def _load_cached_texts(self):
        """Load cached author texts from disk."""
        cache_file = self.storage_path / "author_texts_cache.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    self.author_texts = json.load(f)
                logger.info(f"Loaded {sum(len(texts) for texts in self.author_texts.values())} cached author texts")
            except Exception as e:
                logger.error(f"Error loading cached texts: {e}")
    
    def _save_cached_texts(self):
        """Save author texts to disk cache."""
        cache_file = self.storage_path / "author_texts_cache.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.author_texts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving cached texts: {e}")
    
    def load_author_texts(
        self,
        author_id: str,
        use_cache: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Load texts for a specific author.
        
        Args:
            author_id: Author identifier
            use_cache: Use cached texts if available
            
        Returns:
            List of text chunks with metadata
        """
        if author_id not in AUTHORS:
            logger.warning(f"Unknown author: {author_id}")
            return []
        
        # Check cache first
        if use_cache and author_id in self.author_texts:
            logger.info(f"Using cached texts for {author_id}")
            return self.author_texts[author_id]
        
        author_info = AUTHORS[author_id]
        texts = []
        
        # For now, use sample texts (in production, would fetch from URLs)
        # Using embedded samples for reliability
        sample_texts = self._get_sample_texts(author_id)
        
        # Split into chunks
        chunk_size = 500  # characters per chunk
        for i, text in enumerate(sample_texts):
            for j in range(0, len(text), chunk_size):
                chunk = text[j:j + chunk_size]
                if len(chunk.strip()) > 100:  # Only meaningful chunks
                    texts.append({
                        'text': chunk,
                        'author': author_id,
                        'author_name': author_info['name'],
                        'chunk_id': f"{author_id}_{i}_{j}",
                        'metadata': {
                            'style_keywords': author_info['style_keywords']
                        }
                    })
        
        self.author_texts[author_id] = texts
        self._save_cached_texts()
        
        logger.info(f"Loaded {len(texts)} text chunks for {author_id}")
        return texts
    
    def _get_sample_texts(self, author_id: str) -> List[str]:
        """Get sample texts for author (embedded for reliability)."""
        samples = {
            "tolstoy": [
                "Все счастливые семьи похожи друг на друга, каждая несчастливая семья несчастлива по-своему. "
                "В доме Облонских всё смешалось. Жена узнала, что муж был в связи с бывшею в их доме француженкою-гувернанткой, "
                "и объявила мужу, что не может жить с ним в одном доме.",
                "Война и мир — это не роман, ещё менее поэма, ещё менее историческая хроника. "
                "Война и мир есть то, что хотел и мог выразить автор в той форме, в которой оно выразилось.",
            ],
            "dostoevsky": [
                "В начале июля, в чрезвычайно жаркое время, под вечер, один молодой человек вышел из своей каморки, "
                "которую нанимал от жильцов в С-м переулке, на улицу и медленно, как бы в нерешимости, отправился к К-ну мосту.",
                "Преступление и наказание. Это не просто роман о преступлении, это глубокое исследование человеческой души, "
                "морали, совести и искупления.",
            ],
            "pushkin": [
                "Мой дядя самых честных правил, Когда не в шутку занемог, Он уважать себя заставил "
                "И лучше выдумать не мог.",
                "Я помню чудное мгновенье: Передо мной явилась ты, Как мимолётное виденье, "
                "Как гений чистой красоты.",
            ],
            "lermontov": [
                "Герой нашего времени, милостивые государи мои, точно портрет, но не одного человека: "
                "это портрет, составленный из пороков всего нашего поколения, в полном их развитии.",
                "И скучно и грустно, и некому руку подать В минуту душевной невзгоды... "
                "Желания!.. что пользы напрасно и вечно желать?",
            ],
            "turgenev": [
                "Отцы и дети. Конфликт поколений, столкновение старых и новых идей, "
                "философские споры о нигилизме и традициях.",
                "Рудин — человек слова, но не дела. Он говорит красиво, но не может действовать, "
                "и это его трагедия.",
            ],
            "leskov": [
                "Левша — мастеровой тульский, который подковал блоху. "
                "Народная мудрость и русский характер в простом человеке.",
                "Очарованный странник — человек, ищущий свой путь, свою судьбу. "
                "Русская душа в поисках истины.",
            ],
            "mark_twain": [
                "You don't know about me without you have read a book by the name of The Adventures of Tom Sawyer; "
                "but that ain't no matter. That book was made by Mr. Mark Twain, and he told the truth, mainly.",
                "The difference between the right word and the almost right word is the difference between "
                "lightning and a lightning bug.",
            ],
            "faulkner": [
                "The past is never dead. It's not even past. The past is not dead. It's not even past.",
                "I believe that man will not merely endure: he will prevail. He is immortal, not because he alone "
                "among creatures has an inexhaustible voice, but because he has a soul, a spirit capable of compassion "
                "and sacrifice and endurance.",
            ]
        }
        
        return samples.get(author_id, [])
    
    def search_author_style(
        self,
        author_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for style examples from author.
        
        Args:
            author_id: Author identifier
            query: Search query
            top_k: Number of results
            
        Returns:
            List of relevant text chunks
        """
        if author_id not in AUTHORS:
            return []
        
        # Load author texts if not loaded
        if author_id not in self.author_texts:
            self.load_author_texts(author_id)
        
        texts = self.author_texts.get(author_id, [])
        if not texts:
            return []
        
        # Simple keyword matching (in production, would use semantic search)
        query_lower = query.lower()
        scored_texts = []
        
        for text_item in texts:
            text = text_item['text'].lower()
            score = 0
            
            # Keyword matching
            query_words = query_lower.split()
            for word in query_words:
                if word in text:
                    score += 1
            
            # Style keyword bonus
            style_keywords = text_item.get('metadata', {}).get('style_keywords', [])
            for keyword in style_keywords:
                if keyword.lower() in query_lower:
                    score += 2
            
            if score > 0:
                scored_texts.append({
                    **text_item,
                    'relevance_score': score
                })
        
        # Sort by relevance
        scored_texts.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return scored_texts[:top_k]
    
    def get_author_style_context(
        self,
        author_id: str,
        topic: Optional[str] = None,
        num_examples: int = 3
    ) -> str:
        """
        Get style context for author.
        
        Args:
            author_id: Author identifier
            topic: Optional topic to focus on
            num_examples: Number of style examples
            
        Returns:
            Formatted style context string
        """
        if author_id not in AUTHORS:
            return ""
        
        author_info = AUTHORS[author_id]
        
        # Get style examples
        if topic:
            examples = self.search_author_style(author_id, topic, top_k=num_examples)
        else:
            # Get random examples
            if author_id not in self.author_texts:
                self.load_author_texts(author_id)
            texts = self.author_texts.get(author_id, [])
            examples = texts[:num_examples] if texts else []
        
        # Build context
        context_parts = [
            f"Стиль автора: {author_info['name']} ({author_info['english_name']})",
            f"Характерные черты стиля: {', '.join(author_info['style_keywords'])}",
            "",
            "Примеры стиля:"
        ]
        
        for i, example in enumerate(examples, 1):
            context_parts.append(f"\nПример {i}:")
            context_parts.append(example['text'])
        
        return "\n".join(context_parts)
    
    def initialize_all_authors(self):
        """Initialize and cache texts for all authors."""
        logger.info("Initializing author texts for all authors...")
        for author_id in AUTHORS.keys():
            try:
                self.load_author_texts(author_id, use_cache=True)
            except Exception as e:
                logger.error(f"Error loading texts for {author_id}: {e}")
        logger.info("Author texts initialization complete")


# Global instance
_author_rag: Optional[AuthorStyleRAG] = None


def get_author_rag() -> AuthorStyleRAG:
    """Get global author RAG instance."""
    global _author_rag
    if _author_rag is None:
        _author_rag = AuthorStyleRAG()
        # Initialize on first use
        _author_rag.initialize_all_authors()
    return _author_rag

