"""
Post generator using author's style from analyzed blog.
Generates posts based on trending news in author's voice.
"""
import os
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


# Post templates for structured generation
POST_TEMPLATES = {
    "news_analysis": """
{hook}

Факты:
{facts}

Контекст:
{context}

Анализ:
{analysis}

{conclusion}
""",
    
    "historical_parallel": """
{current_event}

История повторяется. {historical_event}

Тогда: {then}
Сейчас: {now}

{comparison}

{lesson}
""",
    
    "three_perspectives": """
{topic_intro}

Взгляд первый: {perspective_1}

Взгляд второй: {perspective_2}

Взгляд третий: {perspective_3}

{synthesis}
""",
    
    "problem_solution": """
{problem_statement}

Почему это проблема:
{why_problem}

Возможные решения:
{solutions}

Что произойдет, если ничего не делать:
{consequences}

{call_to_action}
""",
    
    "devils_advocate": """
{popular_opinion}

Но давайте честно:
{counterpoint}

Факты, которые игнорируют:
{ignored_facts}

Неудобные вопросы:
{uncomfortable_questions}

{provocative_conclusion}
"""
}

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
Напиши философский пост (400-600 слов) на актуальную тему из новостей.

ТРЕБОВАНИЯ К СОДЕРЖАНИЮ:
- Используй КОНКРЕТНЫЕ факты и примеры из новостей (не общие рассуждения!)
- Добавь исторический контекст или параллели где уместно
- Философские размышления о природе и последствиях событий
- Никаких банальностей - только глубокие, неочевидные мысли
- Покажи связь локального события с глобальными процессами
- Заканчивай провокационным вопросом, который заставит задуматься

ТРЕБОВАНИЯ К СТИЛЮ:
- Твой фирменный ироничный тон обязателен
- Используй характерные фразы и лексику из примеров
- Короткие емкие предложения чередуй с длинными размышлениями
- Разговорный язык с элементами сарказма
- Без канцелярита и штампов
- Пиши ТОЛЬКО текст поста, без преамбул типа "Вот пост:" или "Написал:"

СТРУКТУРА:
1. Зацепляющий лид - факт или вопрос из новостей
2. Основная часть - анализ и размышления с примерами
3. Заключение - провокационный вывод или вопрос

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
Напиши ироничный пост (350-500 слов) про актуальное событие.

ТРЕБОВАНИЯ К СОДЕРЖАНИЮ:
- Выбери ОДНО конкретное событие из новостей (не все сразу!)
- Покажи абсурд или противоречия в ситуации
- Исторические параллели ОБЯЗАТЕЛЬНЫ (подбери похожий случай из истории)
- Можно использовать цитаты из новостей для усиления иронии
- Без прямых оскорблений, но сарказм - максимальный

ТРЕБОВАНИЯ К СТИЛЮ:
- Твой фирменный саркастический стиль
- Используй характерные фразы из твоих примеров
- Ирония через сравнения и аналогии
- Короткие язвительные реплики
- Риторические вопросы приветствуются
- Пиши ТОЛЬКО текст поста

СТРУКТУРА:
1. Открытие - абсурдная констатация факта
2. Развитие - историческая параллель или сравнение
3. Кульминация - максимальный сарказм
4. Финал - ироничный вывод

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
Напиши аналитический пост (500-700 слов) с глубоким разбором ситуации.

ТРЕБОВАНИЯ К СОДЕРЖАНИЮ:
- Выбери основное событие и разбери его детально
- ОБЯЗАТЕЛЬНО: причины → текущая ситуация → последствия
- Исторический контекст (похожие события в прошлом и их исход)
- Прогноз развития на ближайшие 3-6 месяцев
- Назови конкретных игроков/участников и их мотивацию
- Покажи неочевидные связи и факторы

ТРЕБОВАНИЯ К СТИЛЮ:
- Твой обычный стиль письма (см. примеры)
- Логичная структура аргументации
- Без излишних эмоций, но с характерной иронией
- Факты подкрепляй ссылками на источники из новостей
- Избегай категоричных суждений - используй "вероятно", "возможно"
- Пиши ТОЛЬКО текст поста

СТРУКТУРА:
1. Лид - суть события в 2-3 предложениях
2. Контекст - что привело к этой ситуации
3. Анализ - разбор причин и движущих сил
4. Прогноз - возможные сценарии развития
5. Вывод - твоя оценка ситуации

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
Напиши провокационный пост (400-550 слов) который взорвет комментарии.

ТРЕБОВАНИЯ К СОДЕРЖАНИЮ:
- Возьми событие из новостей и подай с НЕОЖИДАННОГО ракурса
- Выскажи непопулярное мнение (но обоснуй его!)
- Поставь под сомнение общепринятые истины
- Покажи противоречия в логике большинства
- Используй провокационные сравнения и аналогии
- ОБЯЗАТЕЛЬНО закончи прямым вопросом к читателям

ТРЕБОВАНИЯ К СТИЛЮ:
- Твой фирменный стиль (см. примеры)
- Прямые обращения к аудитории
- Риторические вопросы по ходу текста
- Намеренные упрощения для усиления эффекта
- Можно сломать политкорректность (в разумных пределах)
- Эмоциональность приветствуется
- Пиши ТОЛЬКО текст поста

СТРУКТУРА:
1. Шокирующее утверждение или вопрос
2. Аргументация - почему все не так очевидно
3. Примеры и доказательства твоей точки зрения
4. Усиление - доведение мысли до логического завершения
5. Прямой вопрос к читателям для дискуссии

ВАЖНО:
- Пост должен вызывать желание возразить
- Но аргументация должна быть крепкой
- Без оскорблений, но с максимальной провокацией

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
    max_examples: int = 3  # Reduced from default to save tokens
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

    # Fetch trending news (reduced for cost savings)
    news_data = fetch_trending_news(max_items=5)  # Reduced from 10
    
    # Translate English news to Russian (can be skipped to save costs)
    # Check if translation should be skipped
    skip_translation = os.getenv("SKIP_TRANSLATION", "false").lower() == "true"
    
    if skip_translation and provider != "demo":
        # Use news as-is (user understands English or prefers original)
        translated_news = news_data['news_items']
    else:
        from ..nlp.translator import translate_and_summarize_news
        # Use cheaper model for translation
        from .model_selector import select_model_for_task
        translation_config = select_model_for_task("translation", "standard", provider)
        translation_model = translation_config.get("model", "gpt-3.5-turbo")
        
        translated_news = translate_and_summarize_news(
            news_data['news_items'],
            provider=provider,
            model=translation_model  # Use cheaper model for translation
        )
    
    # Filter news by topic (semantic + keyword hybrid)
    try:
        from ..nlp.semantic_filter import hybrid_filter
        filtered_news = hybrid_filter(
            translated_news,
            topic,
            use_semantic=True,
            use_keywords=True,
            semantic_threshold=0.3
        )
        # Fallback to old keyword method if no results
        if not filtered_news:
            filtered_news = _filter_news_by_topic(translated_news, topic)
    except Exception:
        # Fallback if semantic filter fails
        filtered_news = _filter_news_by_topic(translated_news, topic)
    
    # Aggregate news context (reduced for cost savings)
    from ..nlp.context_aggregator import aggregate_news_context
    try:
        news_context = aggregate_news_context(
            filtered_news[:3],  # Reduced from 10 to 3
            topic=topic,
            format_for_prompt=True
        )
    except Exception:
        # Fallback to simple formatting (summarized)
        news_context = "\n\n".join([
            f"- {item['title']} ({item['source']})\n  {item['summary'][:150]}..."  # Reduced from 200
            for item in filtered_news[:3]  # Reduced from 5
        ])
    
    # Add topic instruction
    topic_instruction = _get_topic_instruction(topic)

    # Build prompt with topic focus
    prompt_base = style_config["prompt_template"]
    
    # Add topic instruction if specified
    if topic != "any":
        prompt_base = prompt_base.replace(
            "ЗАДАЧА:",
            f"ФОКУС ТЕМЫ:\n{topic_instruction}\n\nЗАДАЧА:"
        )
    
    # Limit style examples to save tokens (reduced from all to top 3)
    style_examples_list = author_context["examples"][:3]  # Limit to 3 examples
    
    prompt = prompt_base.format(
        author_style=author_context["description"][:500],  # Limit style description
        style_examples="\n\n---\n\n".join([
            f"Пример {i+1}:\n{ex[:300]}"  # Limit each example to 300 chars
            for i, ex in enumerate(style_examples_list)
        ]),
        news_context=news_context
    )

    # Select appropriate max_tokens based on quality
    from .model_selector import select_model_for_task
    model_config = select_model_for_task("post_generation", "standard", provider)
    max_tokens = model_config.get("max_tokens", 2000)
    
    # Generate with LLM
    response = call_llm(
        provider=provider,
        prompt=prompt,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens
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

