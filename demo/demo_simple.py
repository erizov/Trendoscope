#!/usr/bin/env python3
"""
Simple demo of Trendoscope without external dependencies.
Shows core functionality without actual scraping.
"""
import sys
import os
import json

# Add src to path (go up one level from demo/ folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def main():
    """Run simple demo."""
    # Set UTF-8 encoding for Windows console
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer,
            encoding='utf-8',
            errors='replace'
        )

    print("\n" + "=" * 70)
    print("ПРОСТАЯ ДЕМОНСТРАЦИЯ ТРЕНДОСКОП")
    print("=" * 70)

    print("\nСоздание тестовых данных...")

    # Sample posts
    posts = [
        {
            "title": "Технологии будущего",
            "text_plain": (
                "Искусственный интеллект меняет наш мир. "
                "Нейросети создают тексты и изображения. "
                "Это революция! Что вы думаете об этом?"
            ),
            "url": "https://test.lj.com/1.html",
            "tags": ["технологии", "AI"]
        },
        {
            "title": "Экономика и финансы",
            "text_plain": (
                "Рынки растут, инвесторы радуются. "
                "Аналитики предсказывают дальнейший рост. "
                "Время покупать акции?"
            ),
            "url": "https://test.lj.com/2.html",
            "tags": ["экономика", "инвестиции"]
        }
    ]

    print(f"OK Создано {len(posts)} тестовых постов")

    # Try NLP analysis
    print("\nПопытка NLP анализа...")
    try:
        from src.trendascope.nlp.analyzer import analyze_text

        for post in posts:
            analysis = analyze_text(post["text_plain"])
            post["analysis"] = analysis

        print(f"OK Постов проанализировано: {len(posts)}")

        # Show sample
        print("\nПример анализа:")
        sample = posts[0]
        print(f"  Заголовок: {sample['title']}")
        if "analysis" in sample:
            print(f"  Ключевые слова: "
                  f"{[kw['text'] for kw in sample['analysis']['keywords'][:3]]}")
            print(f"  Сентимент: {sample['analysis']['sentiment']['label']}")

    except Exception as e:
        print(f"WARN Анализ недоступен: {str(e)}")
        print("  Установите зависимости: pip install keybert yake")

    # Try style analysis
    print("\nПопытка анализа стиля...")
    try:
        from src.trendascope.nlp.style_analyzer import get_style_prompt

        style = get_style_prompt(posts)
        print("OK Стиль проанализирован")
        print(f"\nОписание стиля:\n{style[:150]}...")

    except Exception as e:
        print(f"WARN Анализ стиля недоступен: {str(e)}")

    # Try content generation
    print("\nПопытка генерации контента...")
    try:
        from src.trendascope.gen.generate import generate_summary

        generated = generate_summary(
            posts,
            mode="logospheric",
            provider="demo"
        )

        print("OK Контент сгенерирован")
        print("\nРЕЗЮМЕ:")
        print(generated['summary'][:200] + "...")

        print("\nЗАГОЛОВКИ:")
        for i, title in enumerate(generated['titles'][:3], 1):
            print(f"  {i}. {title}")

    except Exception as e:
        print(f"WARN Генерация недоступна: {str(e)}")

    # Summary
    print("\n" + "=" * 70)
    print("ИТОГИ ДЕМОНСТРАЦИИ")
    print("=" * 70)

    print("\nOK Базовая функциональность продемонстрирована")
    print("\nДля полной функциональности установите зависимости:")
    print("   pip install -r requirements.txt")

    print("\nДля запуска полной демонстрации:")
    print("   python demo.py")

    print("\nДля запуска Web UI:")
    print("   python run.py")
    print()


if __name__ == "__main__":
    main()

