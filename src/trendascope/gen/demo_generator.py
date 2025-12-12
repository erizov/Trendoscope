"""
Demo mode generator with template-based content creation.
Generates style-aware and topic-aware posts without AI.
"""
import json
import random
import re
from typing import Dict, Any, List, Optional


# Topic keywords for content variation
TOPIC_KEYWORDS = {
    "ai": {
        "topic": "искусственном интеллекте",
        "concept": "разум",
        "theme": "будущем человечества",
        "context": "когнитивной революции",
        "technology": "нейросети",
        "example": "GPT-5",
        "question": "сможет ли ИИ заменить человека",
        "concern": "вытеснение человека",
    },
    "politics": {
        "topic": "политике",
        "concept": "власть",
        "theme": "демократии",
        "context": "цифровой эпохи",
        "technology": "пропаганда",
        "example": "выборы",
        "question": "кто контролирует информацию",
        "concern": "манипуляция общественным мнением",
    },
    "us_affairs": {
        "topic": "событиях в США",
        "concept": "американская мечта",
        "theme": "американской политике",
        "context": "современной Америки",
        "technology": "социальные сети",
        "example": "Вашингтон",
        "question": "куда движется Америка",
        "concern": "поляризация общества",
    },
    "russian_history": {
        "topic": "российской истории",
        "concept": "историческая память",
        "theme": "связи прошлого с настоящим",
        "context": "исторических параллелей",
        "technology": "историческая пропаганда",
        "example": "СССР",
        "question": "что повторяется в истории",
        "concern": "забывание уроков истории",
    },
    "science": {
        "topic": "научных открытиях",
        "concept": "знание",
        "theme": "прогресса науки",
        "context": "научной революции",
        "technology": "исследования",
        "example": "новое открытие",
        "question": "куда ведёт наука человечество",
        "concern": "этические границы науки",
    },
    "any": {
        "topic": "событиях",
        "concept": "изменения",
        "theme": "современности",
        "context": "нашего времени",
        "technology": "технологии",
        "example": "новости",
        "question": "куда мы движемся",
        "concern": "неопределённость будущего",
    }
}


# Style-specific templates
STYLE_TEMPLATES = {
    "philosophical": [
        """Очередная новость о {topic} заставила меня задуматься о том, куда мы движемся.

Все эти разговоры о {common_opinion} упускают главное — мы сами создаём инструменты для своего же вытеснения. И делаем это с энтузиазмом.

История знает множество примеров технологического прогресса, который казался благом, а обернулся проблемой. {historical_example}? Да, это дало нам процветание. Но одновременно — и экологический кризис, и отчуждение человека от труда.

Сейчас мы на пороге революции когнитивной. И вопрос не в том, {superficial_question} — это уже реальность. Вопрос в том, что останется человеку, когда машины освоят всё, что мы считали исключительно человеческим?

Философы спорили о сущности {concept} столетиями. Теперь мы создаём его искусственную копию, даже не разобравшись, что такое оригинал. Не слишком ли это самонадеянно?

А может, это и есть наше предназначение — создать нечто большее, чем мы сами? Передать эстафету эволюции следующему виду разума?

Вопрос только — захотим ли мы с этим смириться, когда поймём, что это уже случилось?""",
        
        """Что значит {concept} в эпоху {context}? Вопрос не новый, но актуальность его только растёт.

{news_hook}

Мы стоим на пороге изменений, масштаб которых трудно переоценить. {technology} меняют не только то, как мы работаем, но и то, кто мы есть.

История показывает: каждое технологическое прорыва несёт в себе зерно как освобождения, так и порабощения. {historical_parallel}

Сейчас мы видим, как {current_trend}. Но что это значит для {theme}? Ответ не очевиден.

Философская мысль всегда пыталась понять природу {concept}. Теперь мы создаём её искусственную версию. Это триумф или поражение человеческого духа?

Возможно, правильный вопрос не в том, сможем ли мы это сделать, а в том, должны ли мы это делать. И если да, то как сохранить человеческое в мире машин?""",
    ],
    
    "ironic": [
        """Смотрю на новости о {topic} и не могу отделаться от чувства дежавю.

Те же лица, те же обещания, те же скандалы. Только декорации меняются. В 90-е было одно шоу, в нулевые — другое, сейчас — третье. А суть? Суть прежняя.

Вспоминается анекдот советских времён: «Партия обещала, что при коммунизме будет всё. Обещание выполнено — при коммунизме не было ничего». Заменяем «коммунизм» на любой современный изм — и актуальность не теряется.

{news_hook}

Политики научились главному — говорить много, не обещая ничего конкретного. А если и обещают, то с таким количеством оговорок, что потом можно легко выкрутиться. «Мы обещали рост экономики, но не уточнили, какой именно показатель». Гениально!

История повторяется. Сначала трагедией, потом фарсом, а потом — бесконечным сериалом с одним и тем же сюжетом. Зрители уже догадываются, чем закончится серия, но всё равно смотрят. Надежда умирает последней, как говорится.

И знаете, что самое смешное? Мы продолжаем участвовать в этом спектакле. Голосуем, спорим, возмущаемся. А режиссёры уже пишут сценарий следующего акта.

Когда же антракт?""",
        
        """Очередной {event_type} — уже который по счёту? Давайте разберёмся трезво, без эмоций.

{news_hook}

Во-первых, {fact_1}. Ничего нового, история знает десятки примеров. {historical_examples}. Где-то сработало, где-то — нет.

Во-вторых, эффективность зависит от трёх факторов: масштаба, времени и альтернатив. Чем шире охват, чем дольше действие, чем меньше обходных путей — тем больше эффект. Но и цена для инициатора растёт пропорционально.

Текущая ситуация показывает интересную картину. Да, {current_situation_1}. Но {current_situation_2}. Да, с потерями, но система не рухнула.

С другой стороны, {opposite_side} получил {their_problems}. Классическая ситуация, когда все в минусе.

Прогноз? {prediction}. История показывает: {historical_lesson}. Вопрос в том, сколько времени и ресурсов потратим на дороге к нему.

Ирония в том, что мы всё это уже проходили. Но почему-то каждый раз думаем, что в этот раз будет по-другому.""",
    ],
    
    "analytical": [
        """Очередной пакет {topic} — давайте разберёмся трезво, без эмоций.

{news_hook}

Во-первых, {fact_1}. Ничего нового, история знает десятки примеров. {historical_examples}. Где-то сработало, где-то — нет.

Во-вторых, эффективность зависит от трёх факторов: масштаба, времени и альтернатив. Чем шире охват, чем дольше действие, чем меньше обходных путей — тем больше эффект. Но и цена для инициатора растёт пропорционально.

Текущая ситуация показывает интересную картину. Да, {current_situation_1}. Но {current_situation_2}. Да, с потерями, но система не рухнула.

С другой стороны, {opposite_side} получил {their_problems}. Классическая ситуация, когда все в минусе.

Прогноз? {prediction}. История показывает: {historical_lesson}. Вопрос в том, сколько времени и ресурсов потратим на дороге к нему.

Анализ данных показывает: {data_insight}. Это означает, что {implication}. Следовательно, {conclusion}.""",
        
        """Анализ ситуации с {topic} показывает интересную картину.

{news_hook}

Давайте разберём по пунктам:

1. {point_1}
2. {point_2}
3. {point_3}

Каждый из этих факторов влияет на общий исход. Но ключевой вопрос: {key_question}

Исторические параллели показывают, что {historical_pattern}. Это означает, что {meaning}.

Текущие данные свидетельствуют о том, что {current_data}. Это создаёт условия для {conditions}.

Прогноз на ближайшее будущее: {forecast}. Однако, {uncertainty_factor} может изменить траекторию.

Вывод: {conclusion}. Рекомендация: {recommendation}.""",
    ],
    
    "provocative": [
        """Давайте поговорим о неудобном: {controversial_statement}.

{news_hook}

«Но у нас же есть {common_objection}!» — скажете вы. Да, есть. И именно поэтому {ironic_reality}. Раньше нужно было {old_way}. Теперь достаточно {new_way}.

Самое лицемерное — это называется «{euphemism}». Звучит благородно, правда? Кто же против {positive_goal}? Вот только решает, что является {negative_term}, узкая группа людей в {power_center}.

История с {current_issue} — не баг, это фича. Система работает именно так, как задумано. Создаётся иллюзия {illusion}, но реальная {reality} контролируется {controller}.

{historical_warning} предупреждал о {warning}. Но он не предвидел, что люди сами добровольно {voluntary_action} и будут платить за это деньги. И благодарить за удобство.

Альтернатива? {alternative} существуют, но маргинальны. Большинство предпочитает {preference}. Парадокс современности.

Вопрос в зале: как долго мы будем притворяться, что {pretense} всё ещё существует?""",
        
        """{topic} умер. Или умирает. Медленно, но верно.

{news_hook}

Мы притворяемся, что {pretense}, но реальность говорит другое. {reality_check}

История показывает: {historical_pattern}. Сначала {stage_1}, потом {stage_2}, а потом — {stage_3}.

Сейчас мы на этапе {current_stage}. Но большинство не замечает, потому что {distraction}.

{provocative_question_1}? {provocative_answer}

{provocative_question_2}? {provocative_answer_2}

Правда неудобна. Но только признав её, мы можем что-то изменить. Или хотя бы понять, что происходит на самом деле.

Вопрос не в том, {superficial_question}. Вопрос в том, {real_question}. И ответ, скорее всего, {likely_answer}.""",
    ]
}


# Fallback content when no news available
FALLBACK_CONTENT = {
    "philosophical": {
        "common_opinion": "том, что технологии решат все проблемы",
        "superficial_question": "сможет ли ИИ написать статью лучше человека",
        "historical_example": "Промышленная революция",
    },
    "ironic": {
        "event_type": "скандал",
        "fact_1": "это инструмент манипуляции",
        "current_situation_1": "ситуация болезненна",
        "current_situation_2": "найдены альтернативы",
        "opposite_side": "другая сторона",
        "their_problems": "свои проблемы",
        "prediction": "ситуация останется",
        "historical_lesson": "экономика находит пути",
    },
    "analytical": {
        "fact_1": "это системный процесс",
        "current_situation_1": "наблюдаются изменения",
        "current_situation_2": "адаптация идёт",
        "opposite_side": "контрагенты",
        "their_problems": "сопутствующие издержки",
        "prediction": "тренд продолжится",
        "historical_lesson": "системы адаптируются",
        "data_insight": "статистика показывает устойчивость",
        "implication": "изменения носят структурный характер",
        "conclusion": "процесс необратим",
    },
    "provocative": {
        "controversial_statement": "система не работает",
        "common_objection": "альтернативы",
        "ironic_reality": "контроль стал тотальным",
        "old_way": "контролировать десятки источников",
        "new_way": "контролировать несколько платформ",
        "euphemism": "борьбой с дезинформацией",
        "positive_goal": "защиты",
        "negative_term": "дезинформацией",
        "power_center": "Силиконовой долине",
        "current_issue": "блокировками",
        "illusion": "свободы",
        "reality": "видимость",
        "controller": "алгоритмами",
        "historical_warning": "Оруэлл",
        "warning": "Большом брате",
        "voluntary_action": "установят камеры слежения",
        "alternative": "Децентрализованные платформы",
        "preference": "удобство контроля неудобству свободы",
        "pretense": "свобода",
    }
}


def extract_style_from_prompt(prompt: str) -> str:
    """
    Extract style from prompt with improved context awareness.
    
    Args:
        prompt: Input prompt
        
    Returns:
        Style name (philosophical, ironic, analytical, provocative)
    """
    prompt_lower = prompt.lower()
    
    # Check for explicit style mentions
    if any(kw in prompt_lower for kw in ["философ", "philosophical", "логосфер"]):
        return "philosophical"
    elif any(kw in prompt_lower for kw in ["ирон", "ironic", "сатир", "sarcastic"]):
        return "ironic"
    elif any(kw in prompt_lower for kw in ["аналит", "analytical", "логическ"]):
        return "analytical"
    elif any(kw in prompt_lower for kw in ["провока", "provocative", "острый", "резкий"]):
        return "provocative"
    
    # Check for style in JSON-like structures
    style_match = re.search(r'["\']?style["\']?\s*[:=]\s*["\']?(\w+)', prompt_lower)
    if style_match:
        style_val = style_match.group(1)
        if style_val in ["philosophical", "ironic", "analytical", "provocative"]:
            return style_val
    
    # Check for mode parameter
    mode_match = re.search(r'["\']?mode["\']?\s*[:=]\s*["\']?(\w+)', prompt_lower)
    if mode_match:
        mode_val = mode_match.group(1)
        mode_map = {
            "logospheric": "philosophical",
            "ironic": "ironic",
            "analytical": "analytical",
            "provocative": "provocative",
        }
        if mode_val in mode_map:
            return mode_map[mode_val]
    
    return "philosophical"  # default


def extract_topic_from_prompt(prompt: str) -> str:
    """
    Extract topic from prompt with improved context awareness.
    
    Args:
        prompt: Input prompt
        
    Returns:
        Topic name (ai, politics, us_affairs, russian_history, science, any)
    """
    prompt_lower = prompt.lower()
    
    # Check for explicit topic parameter
    topic_match = re.search(r'["\']?topic["\']?\s*[:=]\s*["\']?(\w+)', prompt_lower)
    if topic_match:
        topic = topic_match.group(1)
        # Map common variations
        topic_map = {
            "ai": "ai",
            "any": "any",
            "politics": "politics",
            "us": "us_affairs",
            "usa": "us_affairs",
            "russia": "russian_history",
            "russian": "russian_history",
            "science": "science",
        }
        if topic in topic_map:
            return topic_map[topic]
        elif topic in TOPIC_KEYWORDS:
            return topic
    
    # Keyword-based detection with priority
    if any(kw in prompt_lower for kw in ["ai", "ии", "искусственный интеллект", 
                                          "нейросет", "gpt", "chatgpt", "llm"]):
        return "ai"
    elif any(kw in prompt_lower for kw in ["politics", "политик", "выборы", 
                                           "правительств", "парламент"]):
        return "politics"
    elif any(kw in prompt_lower for kw in ["us", "сша", "америк", "вашингтон", 
                                           "белый дом", "конгресс"]):
        return "us_affairs"
    elif any(kw in prompt_lower for kw in ["russia", "россия", "российск", 
                                           "ссср", "советск", "кремл"]):
        return "russian_history"
    elif any(kw in prompt_lower for kw in ["science", "наука", "научн", 
                                          "исследован", "открытие"]):
        return "science"
    
    return "any"


def get_recent_news(topic: str, limit: int = 1) -> List[Dict[str, Any]]:
    """
    Get recent news for topic (if news aggregator available).
    
    Args:
        topic: Topic to filter by
        limit: Maximum items to return
        
    Returns:
        List of news items
    """
    try:
        from ..ingest.news_sources import NewsAggregator
        
        aggregator = NewsAggregator(timeout=5)
        
        # Map topic to source flags
        source_flags = {
            "ai": {"include_ai": True},
            "politics": {"include_politics": True},
            "us_affairs": {"include_us": True},
            "russian_history": {"include_russian": True},
            "science": {"include_ai": True, "include_international": True},
            "any": {"include_russian": True, "include_international": True}
        }
        
        flags = source_flags.get(topic, source_flags["any"])
        news = aggregator.fetch_trending_topics(
            max_per_source=1,
            parallel=True,
            max_workers=5,
            **flags
        )
        
        aggregator.close()
        return news[:limit] if news else []
    except Exception:
        return []


def fill_template(template: str, keywords: Dict[str, str], 
                  news_item: Optional[Dict[str, Any]] = None) -> str:
    """
    Fill template with keywords and optional news data.
    
    Args:
        template: Template string with {placeholders}
        keywords: Dictionary of keyword replacements
        news_item: Optional news item for context
        
    Returns:
        Filled template
    """
    # Start with keywords
    values = keywords.copy()
    
    # Add news data if available
    if news_item:
        values["news_hook"] = (
            f"Очередная новость: «{news_item.get('title', 'Новость')}». "
            f"{news_item.get('summary', '')[:200]}..."
        )
    else:
        values["news_hook"] = "Последние события заставляют задуматься."
    
    # Fill template
    try:
        return template.format(**values)
    except KeyError as e:
        # If placeholder missing, use fallback
        missing = str(e).strip("'")
        values[missing] = f"[{missing}]"
        return template.format(**values)


def generate_demo_post(style: str, topic: str, 
                       news_items: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Generate a demo post using templates.
    
    Args:
        style: Post style (philosophical, ironic, analytical, provocative)
        topic: Topic (ai, politics, us_affairs, russian_history, science, any)
        news_items: Optional list of news items for context
        
    Returns:
        Generated post dictionary
    """
    # Get topic keywords
    topic_kw = TOPIC_KEYWORDS.get(topic, TOPIC_KEYWORDS["any"])
    
    # Get style templates
    templates = STYLE_TEMPLATES.get(style, STYLE_TEMPLATES["philosophical"])
    template = random.choice(templates)
    
    # Get fallback content for style
    fallback = FALLBACK_CONTENT.get(style, FALLBACK_CONTENT["philosophical"])
    
    # Merge all values
    all_values = {**topic_kw, **fallback}
    
    # Add style-specific values
    if style == "philosophical":
        all_values.update({
            "common_opinion": "том, что технологии решат все проблемы",
            "superficial_question": f"{topic_kw['question']}",
            "historical_example": "Промышленная революция",
        })
    elif style == "ironic":
        all_values.update({
            "event_type": "скандал" if topic == "politics" else "новость",
            "fact_1": "это инструмент манипуляции" if topic == "politics" else "это системный процесс",
            "historical_examples": "Континентальная блокада Наполеона, эмбарго против СССР",
        })
    elif style == "analytical":
        all_values.update({
            "point_1": f"Фактор первый: {topic_kw['concept']}",
            "point_2": f"Фактор второй: {topic_kw['context']}",
            "point_3": f"Фактор третий: {topic_kw['theme']}",
            "key_question": topic_kw['question'],
            "historical_pattern": "цикличность процессов",
            "meaning": "повторяемость",
            "current_data": "наблюдаются изменения",
            "conditions": "новые возможности",
            "forecast": "продолжение тренда",
            "uncertainty_factor": "внешние обстоятельства",
            "conclusion": "процесс развивается",
            "recommendation": "наблюдать за развитием",
        })
    elif style == "provocative":
        all_values.update({
            "controversial_statement": f"{topic_kw['concern']}",
            "pretense": "всё хорошо",
            "reality_check": "Но реальность говорит другое.",
            "historical_pattern": "всё повторяется",
            "stage_1": "отрицание",
            "stage_2": "принятие",
            "stage_3": "адаптация",
            "current_stage": "переходный период",
            "distraction": "нас отвлекают",
            "provocative_question_1": "Что происходит на самом деле",
            "provocative_answer": "Мы не хотим это видеть.",
            "provocative_question_2": "Почему мы молчим",
            "provocative_answer_2": "Потому что удобнее не знать.",
            "superficial_question": "что делать",
            "real_question": "готовы ли мы к правде",
            "likely_answer": "скорее всего, нет",
        })
    
    # Use news if available
    news_item = news_items[0] if news_items else None
    
    # Generate text
    text = fill_template(template, all_values, news_item)
    
    # Generate title
    if news_item:
        title = f"Размышления о {news_item.get('title', topic_kw['topic'])}"
    else:
        title_options = [
            f"{topic_kw['concept'].title()} в эпоху {topic_kw['context']}",
            f"О {topic_kw['topic']} и {topic_kw['theme']}",
            f"{topic_kw['concept'].title()}, {topic_kw['technology']} и будущее",
        ]
        title = random.choice(title_options)
    
    # Generate tags
    tag_map = {
        "ai": ["искусственныйинтеллект", "технологии", "будущее"],
        "politics": ["политика", "общество", "власть"],
        "us_affairs": ["сша", "политика", "международныеотношения"],
        "russian_history": ["история", "россия", "прошлое"],
        "science": ["наука", "исследования", "открытия"],
        "any": ["размышления", "современность", "тренды"],
    }
    tags = tag_map.get(topic, tag_map["any"])
    
    return {
        "title": title,
        "text": text,
        "tags": tags,
        "demo_mode": True,
        "demo_note": (
            "Это демонстрационный пост, созданный на основе шаблонов. "
            "В реальном режиме с OpenAI контент будет более персонализированным "
            "и точным, учитывая ваш уникальный стиль письма."
        )
    }


def generate_demo_summary(style: str, topic: str) -> Dict[str, Any]:
    """
    Generate demo summary format.
    
    Args:
        style: Summary style
        topic: Topic
        
    Returns:
        Summary dictionary
    """
    topic_kw = TOPIC_KEYWORDS.get(topic, TOPIC_KEYWORDS["any"])
    
    summary_templates = {
        "philosophical": (
            f"Размышления о {topic_kw['topic']} и {topic_kw['theme']}. "
            f"Ключевой вопрос: {topic_kw['question']}? "
            f"Исторические параллели показывают, что {topic_kw['context']} "
            f"неизбежно ведёт к переосмыслению {topic_kw['concept']}. "
            f"Выводы требуют глубокого анализа."
        ),
        "analytical": (
            f"Анализ {topic_kw['topic']} показывает системные изменения. "
            f"Фактор первый: {topic_kw['technology']}. "
            f"Фактор второй: {topic_kw['context']}. "
            f"Фактор третий: {topic_kw['theme']}. "
            f"Прогноз: продолжение тренда с адаптацией."
        ),
    }
    
    summary = summary_templates.get(style, summary_templates["analytical"])
    
    title_options = [
        f"О {topic_kw['topic']} и {topic_kw['theme']}",
        f"{topic_kw['concept'].title()} в эпоху {topic_kw['context']}",
        f"Размышления о {topic_kw['topic']}",
    ]
    
    return {
        "summary": summary,
        "titles": title_options,
        "ideas": [
            {
                "title": f"Идея: {topic_kw['concept']}",
                "explanation": f"Исследование {topic_kw['theme']}",
                "format": "лонгрид",
                "cta": "Обсудить в комментариях",
                "timing": "вечер"
            },
            {
                "title": f"Идея: {topic_kw['technology']}",
                "explanation": f"Анализ {topic_kw['context']}",
                "format": "короткий пост",
                "cta": "Поделиться",
                "timing": "утро"
            }
        ],
        "leads": {
            "short": f"Краткий обзор {topic_kw['topic']}.",
            "long": (
                f"Подробный анализ {topic_kw['topic']} и его влияния на "
                f"{topic_kw['theme']}. Рассмотрение {topic_kw['context']} "
                f"и перспектив развития."
            )
        },
        "viral_potential": {
            "label": "medium",
            "score": 0.55,
            "why": "Демонстрационный режим с шаблонным контентом"
        },
        "demo_mode": True
    }

