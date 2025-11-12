#!/usr/bin/env python3
"""
Quick demo of Trendoscope pipeline.
Demonstrates the full workflow without actual scraping.
"""
import sys
import os
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.trendascope.pipeline.orchestrator import Pipeline
from src.trendascope.nlp.analyzer import analyze_text
from src.trendascope.nlp.style_analyzer import get_style_prompt
from src.trendascope.trends.engine import get_trending_topics


def create_sample_posts():
    """Create sample posts for demonstration."""
    return [
        {
            "title": "Технологии меняют мир",
            "text_plain": (
                "Искусственный интеллект стремительно развивается. "
                "Машинное обучение проникает во все сферы жизни. "
                "Нейросети создают тексты, изображения и музыку. "
                "Что это значит для будущего человечества? "
                "Будут ли роботы умнее людей? "
                "Эти вопросы волнуют учёных и философов."
            ),
            "url": "https://civil-engineer.livejournal.com/1.html",
            "published": "2024-11-10",
            "tags": ["технологии", "AI", "будущее"],
            "comments_count": 42,
            "likes_count": 156
        },
        {
            "title": "Экономика и кризис",
            "text_plain": (
                "Мировая экономика переживает непростые времена. "
                "Инфляция растёт, центробанки повышают ставки. "
                "Инвесторы нервничают, рынки волатильны. "
                "Эксперты предсказывают рецессию. "
                "Но есть и позитивные сигналы. "
                "Некоторые отрасли показывают рост."
            ),
            "url": "https://civil-engineer.livejournal.com/2.html",
            "published": "2024-11-11",
            "tags": ["экономика", "финансы", "кризис"],
            "comments_count": 28,
            "likes_count": 89
        },
        {
            "title": "Философия повседневности",
            "text_plain": (
                "Что значит быть человеком в современном мире? "
                "Мы гонимся за успехом, забывая о смысле. "
                "Технологии отдаляют нас друг от друга. "
                "Или приближают? Парадокс нашего времени. "
                "Древние мудрецы знали ответы. "
                "Но актуальны ли они сегодня?"
            ),
            "url": "https://civil-engineer.livejournal.com/3.html",
            "published": "2024-11-12",
            "tags": ["философия", "жизнь", "смысл"],
            "comments_count": 15,
            "likes_count": 67
        },
        {
            "title": "Образование 2.0",
            "text_plain": (
                "Традиционная система образования устарела. "
                "Университеты не готовят к реальной работе. "
                "Онлайн-курсы и самообразование — новый тренд. "
                "ChatGPT помогает учиться эффективнее. "
                "Нужны ли нам преподаватели? "
                "Споры об этом не утихают."
            ),
            "url": "https://civil-engineer.livejournal.com/4.html",
            "published": "2024-11-12",
            "tags": ["образование", "онлайн", "технологии"],
            "comments_count": 35,
            "likes_count": 124
        },
        {
            "title": "Урбанистика и будущее городов",
            "text_plain": (
                "Города растут и меняются. "
                "Умные технологии улучшают жизнь горожан. "
                "Датчики, камеры, аналитика — везде. "
                "Но что с приватностью? "
                "Зелёные зоны исчезают под застройкой. "
                "Нужен баланс между развитием и экологией."
            ),
            "url": "https://civil-engineer.livejournal.com/5.html",
            "published": "2024-11-12",
            "tags": ["урбанистика", "города", "экология"],
            "comments_count": 19,
            "likes_count": 78
        }
    ]


def main():
    """Run demo pipeline."""
    print("\n" + "=" * 70)
    print("🔍 ДЕМОНСТРАЦИЯ ТРЕНДОСКОП (TRENDOSCOPE)")
    print("=" * 70)

    # Create pipeline
    pipeline = Pipeline()

    # Get sample posts
    print("\n[1/5] Создание тестовых постов...")
    posts = create_sample_posts()
    print(f"✓ Создано {len(posts)} постов")

    # Analyze posts
    print("\n[2/5] Анализ постов с помощью NLP...")
    analyzed_posts = pipeline.analyze_posts(posts)
    print(f"✓ Проанализировано {len(analyzed_posts)} постов")

    # Show sample analysis
    if analyzed_posts:
        sample = analyzed_posts[0]
        print(f"\nПример анализа поста '{sample['title']}':")
        analysis = sample['analysis']
        print(f"  Ключевые слова: {[kw['text'] for kw in analysis['keywords'][:5]]}")
        print(f"  Сентимент: {analysis['sentiment']['label']}")
        print(f"  Слов: {analysis['readability']['words']}")
        print(f"  Предложений: {analysis['readability']['sentences']}")

    # Extract trends
    print("\n[3/5] Извлечение трендовых тем...")
    trends = pipeline.extract_trends(analyzed_posts)
    print(f"✓ Найдено {len(trends)} трендов")

    print("\nТоп-5 трендов:")
    for i, trend in enumerate(trends[:5], 1):
        print(f"  {i}. {trend['topic']} (score: {trend['score']:.2f}, "
              f"posts: {trend['post_count']})")

    # Analyze style
    print("\n[4/5] Анализ стиля автора...")
    style_prompt = get_style_prompt(analyzed_posts)
    print("✓ Стиль проанализирован")
    print(f"\nОписание стиля:\n{style_prompt[:200]}...")

    # Generate content
    print("\n[5/5] Генерация контента...")
    generated = pipeline.generate_content(
        analyzed_posts[:3],
        mode="analytical",
        provider="demo"
    )
    print("✓ Контент сгенерирован")

    # Display results
    print("\n" + "=" * 70)
    print("РЕЗУЛЬТАТЫ ГЕНЕРАЦИИ")
    print("=" * 70)

    print("\n📝 РЕЗЮМЕ:")
    print(generated['summary'])

    print("\n🎯 ВАРИАНТЫ ЗАГОЛОВКОВ:")
    for i, title in enumerate(generated['titles'], 1):
        print(f"  {i}. {title}")

    print("\n💡 ИДЕИ ДЛЯ ПОСТОВ:")
    for i, idea in enumerate(generated['ideas'], 1):
        print(f"\n  {i}. {idea['title']}")
        print(f"     {idea['explanation']}")
        print(f"     Формат: {idea['format']} | CTA: {idea['cta']} | "
              f"Timing: {idea['timing']}")

    print("\n🔥 ВИРУСНЫЙ ПОТЕНЦИАЛ:")
    vp = generated['viral_potential']
    print(f"  Уровень: {vp['label'].upper()}")
    print(f"  Оценка: {vp['score']}")
    print(f"  Причина: {vp['why']}")

    # Save results
    output_file = "demo_results.json"
    result = {
        "posts": analyzed_posts,
        "trends": trends,
        "generated": generated,
        "stats": {
            "total_posts": len(posts),
            "analyzed_posts": len(analyzed_posts),
            "top_trends": len(trends)
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 70)
    print(f"✓ Результаты сохранены в {output_file}")
    print("=" * 70)

    print("\n💻 Для запуска Web UI выполните:")
    print("   python run.py")
    print("\n📚 Для запуска тестов выполните:")
    print("   pytest tests/test_pipeline.py -v")
    print()


if __name__ == "__main__":
    main()

