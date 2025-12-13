#!/usr/bin/env python3
"""
Demo script for news database.
Shows how to store, search, and retrieve news.
"""
import sys
import os
from pathlib import Path

# Add src directory to Python path (for both runtime and IDE)
project_root = Path(__file__).parent.absolute()
src_path = project_root / 'src'
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Imports (path is set above, so these work at runtime)
# For IDE: ensure Python interpreter is set to project root or src/trendascope
from trendascope.storage.news_db import NewsDatabase  # noqa: E402
from trendascope.ingest.news_sources import NewsAggregator  # noqa: E402
from trendascope.nlp.controversy_scorer import ControversyScorer  # noqa: E402


def demo_basic_operations():
    """Demo basic database operations."""
    print("=" * 70)
    print("📚 DEMO: Basic Database Operations")
    print("=" * 70)
    
    # Create database
    db = NewsDatabase("data/news_demo.db")
    
    # Add sample news
    print("\n1️⃣ Adding sample news...")
    
    news_id = db.add_news(
        title="GPT-5 заменяет программистов: реальность или паника?",
        summary="OpenAI выпустила GPT-5. Модель пишет код лучше 90% разработчиков.",
        full_text="OpenAI анонсировала GPT-5, новую языковую модель, которая может писать код...",
        url="https://example.com/gpt5",
        source="TechCrunch",
        category="tech",
        controversy_score=89,
        controversy_label="hot",
        keywords=["AI", "GPT", "программирование", "работа"],
        language="ru"
    )
    
    print(f"   ✅ Added news with ID: {news_id}")
    
    # Add more
    db.add_news(
        title="Трамп vs Байден: новая холодная война?",
        summary="Скандал в Вашингтоне разгорается...",
        url="https://example.com/trump-biden",
        source="Politico",
        category="politics",
        controversy_score=94,
        controversy_label="explosive",
        keywords=["США", "Трамп", "Байден", "выборы"],
        language="ru"
    )
    
    db.add_news(
        title="Водитель осужден за перевозку взрывчатки без ведома",
        summary="Федеральный суд вынес приговор водителю грузовика...",
        url="https://example.com/truck-driver-case",
        source="Law.com",
        category="legal",
        controversy_score=67,
        controversy_label="hot",
        keywords=["суд", "водитель", "криминал", "закон"],
        language="ru"
    )
    
    print("   ✅ Added 3 news items total")
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n📊 Database stats:")
    print(f"   Total: {stats['total_items']} items")
    print(f"   Categories: {stats['by_category']}")
    print(f"   Controversy: {stats['controversy_distribution']}")
    
    db.close()


def demo_search():
    """Demo search capabilities."""
    print("\n" + "=" * 70)
    print("🔍 DEMO: Full-Text Search")
    print("=" * 70)
    
    db = NewsDatabase("data/news_demo.db")
    
    # Search queries
    queries = [
        "программист",
        "водитель суд",
        "Трамп Байден",
        "GPT AI",
    ]
    
    for query in queries:
        results = db.search(query, limit=5)
        print(f"\n🔎 Search: '{query}'")
        print(f"   Found: {len(results)} results")
        
        for i, item in enumerate(results, 1):
            print(f"   {i}. [{item['controversy_score']}%] {item['title'][:60]}...")
            print(f"      Category: {item['category']}, Source: {item['source']}")
    
    db.close()


def demo_trending():
    """Demo trending keywords."""
    print("\n" + "=" * 70)
    print("🔥 DEMO: Trending Keywords")
    print("=" * 70)
    
    db = NewsDatabase("data/news_demo.db")
    
    trending = db.get_trending_keywords(limit=10)
    
    print("\n📊 Top keywords:")
    for i, item in enumerate(trending, 1):
        bar = "█" * min(item['count'] * 5, 30)
        print(f"   {i:2d}. {item['keyword']:15s} [{item['count']}] {bar}")
    
    db.close()


def demo_load_real_news():
    """Demo loading real news from API."""
    print("\n" + "=" * 70)
    print("📰 DEMO: Load Real News into Database")
    print("=" * 70)
    
    # Fetch real news
    print("\n📡 Fetching news from RSS feeds...")
    aggregator = NewsAggregator(timeout=5)
    news_items = aggregator.fetch_trending_topics(
        include_russian=True,
        include_ai=True,
        max_per_source=2,
        parallel=True
    )
    
    print(f"   ✅ Fetched {len(news_items)} items")
    
    # Score them
    print("\n🔥 Scoring controversy...")
    scorer = ControversyScorer()
    scored_items = scorer.score_batch(news_items)
    
    # Store in database
    print("\n💾 Storing in database...")
    db = NewsDatabase("data/news_demo.db")
    
    inserted = db.bulk_insert(scored_items)
    
    print(f"   ✅ Inserted {inserted} new items")
    
    # Show stats
    stats = db.get_statistics()
    print(f"\n📊 Database now has {stats['total_items']} total items")
    
    # Show most controversial
    print("\n🔥 Top 5 controversial in database:")
    top = db.get_top_controversial(limit=5)
    for i, item in enumerate(top, 1):
        score = item['controversy_score']
        print(f"   {i}. [{score}%] {item['title'][:60]}...")
    
    db.close()


def demo_api_integration():
    """Show how to use with FastAPI."""
    print("\n" + "=" * 70)
    print("🌐 DEMO: API Integration Example")
    print("=" * 70)
    
    print("\n📝 Add to api/main.py:")
    print("-" * 70)
    print("""
from ..storage.news_db import NewsDatabase

@app.get("/api/news/search")
async def search_news_api(
    query: str = Query(..., description="Search phrase"),
    category: str = Query(default="all"),
    limit: int = Query(default=20, le=100)
):
    '''Search news in database.'''
    with NewsDatabase() as db:
        results = db.search(query, category=category, limit=limit)
    
    return {
        'success': True,
        'query': query,
        'count': len(results),
        'results': results
    }

@app.get("/api/news/trending")
async def trending_keywords():
    '''Get trending keywords.'''
    with NewsDatabase() as db:
        keywords = db.get_trending_keywords(limit=20)
    
    return {
        'success': True,
        'keywords': keywords
    }
""")


def main():
    """Run all demos."""
    print("\n" + "🎓 NEWS DATABASE DEMO" + "\n")
    
    # Run demos
    demo_basic_operations()
    demo_search()
    demo_trending()
    
    # Optional: Load real news
    print("\n" + "=" * 70)
    print("❓ Load Real News?")
    print("=" * 70)
    print("\nThis will fetch real news from RSS feeds and store in database.")
    print("Time: ~10 seconds")
    
    response = input("\nContinue? (y/n): ").lower()
    if response == 'y':
        demo_load_real_news()
    
    # Show API integration
    demo_api_integration()
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print("\n📚 Database created at: data/news_demo.db")
    print("💡 Use SQLite browser to explore: https://sqlitebrowser.org/")
    print("\n🔍 Try queries:")
    print("   - Search Russian: программист, водитель, суд")
    print("   - Search English: AI, truck, court, driver")
    print("   - Phrases: \"GPT-5 released\", \"осужден за перевозку\"")
    print("\n🚀 Ready to integrate into your app!")


if __name__ == '__main__':
    main()





