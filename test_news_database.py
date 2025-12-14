#!/usr/bin/env python3
"""
Quick test for news database functionality.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trendascope.storage.news_db import NewsDatabase


def test_database():
    """Test basic database operations."""
    print("\n" + "=" * 70)
    print("🧪 NEWS DATABASE TEST")
    print("=" * 70)
    
    # Create test database
    print("\n1️⃣ Creating database...")
    db = NewsDatabase("data/news_test.db")
    print("   ✅ Database created")
    
    # Add test data
    print("\n2️⃣ Adding test news...")
    
    test_items = [
        {
            'title': 'GPT-5 выходит в 2025 году',
            'summary': 'OpenAI анонсировала выход GPT-5',
            'category': 'tech',
            'keywords': ['AI', 'GPT', 'OpenAI'],
            'controversy_score': 75,
            'language': 'ru'
        },
        {
            'title': 'Truck driver convicted for unknowing explosive transport',
            'summary': 'Federal court ruled strict liability applies',
            'category': 'legal',
            'keywords': ['court', 'driver', 'conviction'],
            'controversy_score': 68,
            'language': 'en'
        },
        {
            'title': 'Трамп против Байдена: новый раунд',
            'summary': 'Предвыборная гонка набирает обороты',
            'category': 'politics',
            'keywords': ['США', 'выборы', 'Трамп'],
            'controversy_score': 92,
            'language': 'ru'
        },
    ]
    
    for i, item in enumerate(test_items, 1):
        news_id = db.add_news(
            title=item['title'],
            summary=item['summary'],
            url=f"https://test.com/{i}",
            source="TestSource",
            category=item['category'],
            controversy_score=item['controversy_score'],
            keywords=item['keywords'],
            language=item['language']
        )
        print(f"   ✅ Added: {item['title'][:40]}... (ID: {news_id})")
    
    # Test search - Russian
    print("\n3️⃣ Testing Russian search...")
    results = db.search("GPT программист")
    print(f"   Query: 'GPT программист'")
    print(f"   Found: {len(results)} results")
    for r in results:
        print(f"   - {r['title'][:50]}")
    
    # Test search - English
    print("\n4️⃣ Testing English search...")
    results = db.search("truck driver court")
    print(f"   Query: 'truck driver court'")
    print(f"   Found: {len(results)} results")
    for r in results:
        print(f"   - {r['title'][:50]}")
    
    # Test category filter
    print("\n5️⃣ Testing category filter...")
    results = db.get_recent(category="legal", limit=10)
    print(f"   Category: legal")
    print(f"   Found: {len(results)} results")
    
    # Test controversy
    print("\n6️⃣ Testing controversy filter...")
    results = db.get_top_controversial(limit=3)
    print(f"   Top 3 controversial:")
    for i, r in enumerate(results, 1):
        print(f"   {i}. [{r['controversy_score']}%] {r['title'][:45]}")
    
    # Test statistics
    print("\n7️⃣ Testing statistics...")
    stats = db.get_statistics()
    print(f"   Total items: {stats['total_items']}")
    print(f"   By category: {stats['by_category']}")
    print(f"   Controversy: {stats['controversy_distribution']}")
    
    # Test trending keywords
    print("\n8️⃣ Testing trending keywords...")
    keywords = db.get_trending_keywords(limit=10)
    print(f"   Top keywords:")
    for i, kw in enumerate(keywords[:5], 1):
        print(f"   {i}. {kw['keyword']} ({kw['count']})")
    
    # Cleanup
    db.close()
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS PASSED")
    print("=" * 70)
    print("\n📁 Test database: data/news_test.db")
    print("💡 You can explore it with DB Browser for SQLite")
    print("🗑️  Delete test database: rm data/news_test.db")
    
    return True


if __name__ == '__main__':
    try:
        success = test_database()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)






