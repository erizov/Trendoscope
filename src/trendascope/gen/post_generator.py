"""
Post generator using author's style from analyzed blog.
Generates posts based on trending news in author's voice.
"""
from typing import List, Dict, Any, Optional

from ..nlp.style_analyzer import get_style_prompt, get_style_analyzer
from ..ingest.news_sources import fetch_trending_news
from ..index.vector_db import search_similar
from .llm.providers import call_llm


# Topic definitions for filtering and instruction
TOPIC_DEFINITIONS = {
    "ai": {
        "keywords": ["AI", "artificial intelligence", "machine learning", "neural", "GPT", "ChatGPT", 
                     "LLM", "нейросет", "искусственный интеллект", "ИИ", "алгоритм"],
        "instruction": "Сфокусируйся на теме искусственного интеллекта, нейросетей, машинного обучения и их влиянии на общество."
    },
    "politics": {
        "keywords": ["politics", "government", "election", "policy", "diplomacy", "политик", "правительств", 
                     "выборы", "дипломат", "парламент", "геополитик"],
        "instruction": "Сфокусируйся на политических событиях, международных отношениях и геополитике."
    },
    "us_affairs": {
        "keywords": ["USA", "US", "America", "American", "Washington", "White House", "Congress", "Trump", "Biden",
                     "США", "Америк", "Вашингтон", "Белый дом", "Конгресс"],
        "instruction": "Сфокусируйся на событиях в США, американской политике и влиянии США на мировую арену."
    },
    "russian_history": {
        "keywords": ["Russia", "Russian", "USSR", "Soviet", "Россия", "российск", "советск", "СССР", 
                     "истори", "петербург", "москв", "кремл"],
        "instruction": "Сфокусируйся на российской истории, исторических параллелях и связи прошлого с настоящим."
    },
    "science": {
        "keywords": ["science", "research", "study", "technology", "space", "physics", "biology", 
                     "наука", "научн", "исследован", "технолог", "космос", "физик"],
        "instruction": "Сфокусируйся на научных открытиях, технологических прорывах и их значении для человечества."
    }
}


def _filter_news_by_topic(news_items: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
    """Filter news items by topic keywords."""
    if topic == "any" or topic not in TOPIC_DEFINITIONS:
        return news_items
    
    keywords = TOPIC_DEFINITIONS[topic]["keywords"]
    filtered = []
    
    for item in news_items:
        text = f"{item.get('title', '')} {item.get('summary', '')}".lower()
        if any(keyword.lower() in text for keyword in keywords):
            filtered.append(item)
    
    # If no matches, return all (better than empty)
    return filtered if filtered else news_items


def _get_topic_instruction(topic: str) -> str:
    """Get instruction text for the specified topic."""
    if topic == "any" or topic not in TOPIC_DEFINITIONS:
        return ""
    return TOPIC_DEFINITIONS[topic]["instruction"]


# Post generation styles
POST_STYLES = {
    "philosophical": {
        "name": "Философский",
        "description": "Глубокие размышления о смысле событий",
        "prompt_template": """Ты пишешь в блоге civil-engineer.livejournal.com.

ТВОЙ СТИЛЬ:
{author_style}

ПРИМЕРЫ ТВОИХ ПОСТОВ:
{style_examples}

АКТУАЛЬНЫЕ НОВОСТИ:
{news_context}

ЗАДАЧА:
Напиши философский пост (300-500 слов) на актуальную тему из новостей.

ТРЕБОВАНИЯ:
- Используй твой обычный стиль и лексику
- Философские размышления о природе событий
- Никаких банальностей, только глубокие мысли
- Можно использовать сарказм и иронию (как обычно)
- Заканчивай провокационным вопросом или выводом
- Пиши ТОЛЬКО текст поста, без преамбул

ФОРМАТ:
Верни JSON:
{{
  "title": "Заголовок поста",
  "text": "Текст поста...",
  "tags": ["тег1", "тег2", "тег3"]
}}"""
    },
    
    "ironic": {
        "name": "Ироничный",
        "description": "Саркастический взгляд на события",
        "prompt_template": """Ты пишешь в блоге civil-engineer.livejournal.com.

ТВОЙ СТИЛЬ:
{author_style}

ПРИМЕРЫ ТВОИХ ПОСТОВ:
{style_examples}

АКТУАЛЬНЫЕ НОВОСТИ:
{news_context}

ЗАДАЧА:
Напиши ироничный пост (200-400 слов) про актуальное событие.

ТРЕБОВАНИЯ:
- Твой фирменный саркастический стиль
- Используй свою обычную лексику
- Покажи абсурд ситуации
- Исторические параллели приветствуются
- Можно цитаты и аналогии
- Пиши ТОЛЬКО текст поста

ФОРМАТ:
Верни JSON:
{{
  "title": "Заголовок поста",
  "text": "Текст поста...",
  "tags": ["тег1", "тег2", "тег3"]
}}"""
    },
    
    "analytical": {
        "name": "Аналитический",
        "description": "Трезвый анализ событий",
        "prompt_template": """Ты пишешь в блоге civil-engineer.livejournal.com.

ТВОЙ СТИЛЬ:
{author_style}

ПРИМЕРЫ ТВОИХ ПОСТОВ:
{style_examples}

АКТУАЛЬНЫЕ НОВОСТИ:
{news_context}

ЗАДАЧА:
Напиши аналитический пост (400-600 слов) с разбором ситуации.

ТРЕБОВАНИЯ:
- Твой обычный стиль письма
- Логичный анализ причин и следствий
- Исторический контекст если уместно
- Прогноз развития ситуации
- Без лишних эмоций, но с твоей иронией
- Пиши ТОЛЬКО текст поста

ФОРМАТ:
Верни JSON:
{{
  "title": "Заголовок поста",
  "text": "Текст поста...",
  "tags": ["тег1", "тег2", "тег3"]
}}"""
    },
    
    "provocative": {
        "name": "Провокационный",
        "description": "Вызов на дискуссию",
        "prompt_template": """Ты пишешь в блоге civil-engineer.livejournal.com.

ТВОЙ СТИЛЬ:
{author_style}

ПРИМЕРЫ ТВОИХ ПОСТОВ:
{style_examples}

АКТУАЛЬНЫЕ НОВОСТИ:
{news_context}

ЗАДАЧА:
Напиши провокационный пост (250-450 слов) который вызовет дискуссию.

ТРЕБОВАНИЯ:
- Используй свой фирменный стиль
- Непопулярное мнение или неочевидный ракурс
- Вызови читателя на размышление
- Можно сломать стереотипы
- Закончи вопросом к аудитории
- Пиши ТОЛЬКО текст поста

ФОРМАТ:
Верни JSON:
{{
  "title": "Заголовок поста",
  "text": "Текст поста...",
  "tags": ["тег1", "тег2", "тег3"]
}}"""
    }
}


def get_author_style_context(
    analyzed_posts: List[Dict[str, Any]],
    max_examples: int = 3
) -> Dict[str, str]:
    """
    Extract author style context from analyzed posts.

    Args:
        analyzed_posts: List of analyzed blog posts
        max_examples: Maximum example posts

    Returns:
        Dictionary with style description and examples
    """
    # Get style description
    style_description = get_style_prompt(analyzed_posts)

    # Get example excerpts
    analyzer = get_style_analyzer()
    examples = analyzer.get_style_examples(analyzed_posts, max_examples)

    return {
        "description": style_description,
        "examples": examples
    }


def generate_post(
    analyzed_posts: List[Dict[str, Any]],
    style: str = "philosophical",
    topic: str = "any",
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.8
) -> Dict[str, Any]:
    """
    Generate a new post in author's style.

    Args:
        analyzed_posts: Previously analyzed blog posts for style
        style: Generation style (philosophical, ironic, analytical, provocative)
        topic: Topic focus (any, ai, politics, us_affairs, russian_history, science)
        provider: LLM provider
        model: Model name
        temperature: Generation temperature

    Returns:
        Generated post dictionary
    """
    # Get style configuration
    if style not in POST_STYLES:
        style = "philosophical"

    style_config = POST_STYLES[style]

    # Get author style
    author_context = get_author_style_context(analyzed_posts)

    # Fetch trending news
    news_data = fetch_trending_news(max_items=10)
    
    # Filter news by topic if specified
    filtered_news = _filter_news_by_topic(news_data['news_items'], topic)
    
    # Format news context with topic focus
    topic_instruction = _get_topic_instruction(topic)
    news_context = "\n\n".join([
        f"- {item['title']} ({item['source']})\n  {item['summary'][:200]}..."
        for item in filtered_news[:5]
    ])

    # Build prompt with topic focus
    prompt_base = style_config["prompt_template"]
    
    # Add topic instruction if specified
    if topic != "any":
        prompt_base = prompt_base.replace(
            "ЗАДАЧА:",
            f"ФОКУС ТЕМЫ:\n{topic_instruction}\n\nЗАДАЧА:"
        )
    
    prompt = prompt_base.format(
        author_style=author_context["description"],
        style_examples="\n\n---\n\n".join([
            f"Пример {i+1}:\n{ex}"
            for i, ex in enumerate(author_context["examples"])
        ]),
        news_context=news_context
    )

    # Generate with LLM
    response = call_llm(
        provider=provider,
        prompt=prompt,
        model=model,
        temperature=temperature
    )

    # Parse JSON response (custom parser for posts)
    import json
    import re

    def extract_field_regex(text: str, field: str) -> str:
        """Extract field value using regex as fallback."""
        # Try to find "field": "value" or "field": value
        pattern = rf'"{field}"\s*:\s*"([^"]*(?:"[^"]*)*)"'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1)
        
        # Try without quotes
        pattern = rf'"{field}"\s*:\s*([^,\}}]+)'
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
        
        return ""

    def extract_tags_regex(text: str) -> list:
        """Extract tags array using regex."""
        pattern = r'"tags"\s*:\s*\[(.*?)\]'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            tags_str = match.group(1)
            # Extract quoted strings
            tags = re.findall(r'"([^"]+)"', tags_str)
            return tags
        return []

    try:
        # Extract JSON from response
        response_text = response.strip()
        
        # Remove markdown code blocks if present
        response_text = re.sub(r'^```(?:json)?\s*\n?', '', response_text, flags=re.IGNORECASE)
        response_text = re.sub(r'\n?```\s*$', '', response_text)
        
        # Find JSON object
        start = response_text.find('{')
        end = response_text.rfind('}')
        
        if start == -1 or end == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response_text[start:end+1]
        
        # Try parsing as valid JSON first
        try:
            generated = json.loads(json_str)
        except json.JSONDecodeError as e:
            # JSON parsing failed - use regex fallback
            # This handles cases where LLM generates invalid JSON
            # with unescaped newlines or other control chars
            
            generated = {
                "title": extract_field_regex(json_str, "title"),
                "text": extract_field_regex(json_str, "text"),
                "tags": extract_tags_regex(json_str)
            }
            
            # Clean up extracted text
            if generated["text"]:
                # Unescape common sequences
                generated["text"] = generated["text"].replace('\\n', '\n')
                generated["text"] = generated["text"].replace('\\r', '\r')
                generated["text"] = generated["text"].replace('\\t', '\t')
                generated["text"] = generated["text"].replace('\\"', '"')
        
        # Validate and set defaults
        if not generated.get("title"):
            generated["title"] = "Без заголовка"
        
        if not generated.get("text"):
            raise ValueError("Missing 'text' field")
        
        if "tags" not in generated or not generated["tags"]:
            generated["tags"] = []

        # Add metadata
        generated["style"] = style
        generated["style_name"] = style_config["name"]
        generated["news_topics"] = news_data['top_topics']
        generated["timestamp"] = __import__('datetime').datetime.now().isoformat()

        return generated

    except Exception as e:
        # Fallback response
        return {
            "title": "Ошибка генерации",
            "text": f"Не удалось сгенерировать пост: {str(e)}\n\nОтвет LLM:\n{response[:800]}",
            "tags": [],
            "error": str(e)
        }


def generate_post_from_storage(
    style: str = "philosophical",
    topic: str = "any",
    provider: str = "openai",
    model: Optional[str] = None,
    temperature: float = 0.8
) -> Dict[str, Any]:
    """
    Generate post using saved style guide from storage.

    Args:
        style: Generation style
        topic: Topic focus (any, ai, politics, us_affairs, russian_history, science)
        provider: LLM provider
        model: Model name
        temperature: Generation temperature

    Returns:
        Generated post dictionary
    """
    from ..storage.style_storage import load_style_guide, has_saved_style
    from ..index.vector_db import get_store

    # Check if style guide exists
    if not has_saved_style():
        return {
            "title": "Ошибка: нет сохраненного стиля",
            "text": "Сначала запустите анализ блога чтобы система изучила ваш стиль письма.",
            "tags": ["ошибка"],
            "error": "No saved style guide"
        }

    # Load saved style
    style_data = load_style_guide()
    if not style_data:
        return {
            "title": "Ошибка загрузки стиля",
            "text": "Не удалось загрузить сохраненный стиль.",
            "tags": ["ошибка"],
            "error": "Failed to load style"
        }

    # Get stored posts from vector DB
    store = get_store()
    if not hasattr(store, 'documents') or not store.documents:
        return {
            "title": "Ошибка: нет сохраненных постов",
            "text": "Векторная база данных пуста. Запустите анализ блога.",
            "tags": ["ошибка"],
            "error": "No stored posts"
        }

    # Use stored documents as analyzed posts
    analyzed_posts = store.documents

    # Generate post
    return generate_post(
        analyzed_posts=analyzed_posts,
        style=style,
        topic=topic,
        provider=provider,
        model=model,
        temperature=temperature
    )


def get_available_styles() -> List[Dict[str, str]]:
    """
    Get list of available post styles.

    Returns:
        List of style dictionaries
    """
    return [
        {
            "value": key,
            "name": config["name"],
            "description": config["description"]
        }
        for key, config in POST_STYLES.items()
    ]

