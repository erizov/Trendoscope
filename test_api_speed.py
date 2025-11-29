#!/usr/bin/env python3
"""
Quick test to check API response time.
"""
import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trendascope.ingest.news_sources import NewsAggregator
from trendascope.nlp.controversy_scorer import ControversyScorer


def test_parallel_fetching():
    """Test parallel news fetching speed."""
    print("=" * 60)
    print("🚀 Testing Parallel News Fetching")
    print("=" * 60)
    
    aggregator = NewsAggregator(timeout=5)
    
    # Test with few sources
    print("\n📰 Fetching from Russian sources only...")
    start = time.time()
    
    news_items = aggregator.fetch_trending_topics(
        include_russian=True,
        include_international=False,
        include_ai=False,
        include_politics=False,
        include_us=False,
        include_eu=False,
        max_per_source=2,
        parallel=True,
        max_workers=10
    )
    
    elapsed = time.time() - start
    
    print(f"\n✅ Fetched {len(news_items)} items in {elapsed:.2f} seconds")
    
    if elapsed < 15:
        print("   ✅ FAST: Response time is good!")
    elif elapsed < 30:
        print("   ⚠️  MODERATE: Could be faster")
    else:
        print("   ❌ SLOW: Still too slow")
    
    # Show sample
    if news_items:
        print(f"\n📄 Sample news:")
        for i, item in enumerate(news_items[:3], 1):
            print(f"   {i}. {item['title'][:50]}... ({item['source']})")
    
    return elapsed < 30


def test_with_scoring():
    """Test full pipeline with scoring."""
    print("\n" + "=" * 60)
    print("🔥 Testing with Controversy Scoring")
    print("=" * 60)
    
    aggregator = NewsAggregator(timeout=5)
    scorer = ControversyScorer()
    
    print("\n📰 Fetching AI news...")
    start = time.time()
    
    news_items = aggregator.fetch_trending_topics(
        include_russian=False,
        include_international=False,
        include_ai=True,
        include_politics=False,
        include_us=False,
        include_eu=False,
        max_per_source=2,
        parallel=True,
        max_workers=10
    )
    
    # Score items
    scored_items = scorer.score_batch(news_items)
    
    elapsed = time.time() - start
    
    print(f"\n✅ Fetched and scored {len(scored_items)} items in {elapsed:.2f} seconds")
    
    # Show top controversial
    hot_items = [item for item in scored_items if item['controversy']['score'] >= 60]
    print(f"\n🔥 Found {len(hot_items)} hot/controversial items")
    
    if hot_items:
        print("\n   Top provocative:")
        for i, item in enumerate(hot_items[:3], 1):
            score = item['controversy']['score']
            emoji = item['controversy']['emoji']
            print(f"   {i}. [{score}% {emoji}] {item['title'][:45]}...")
    
    return elapsed < 30


def main():
    """Run all tests."""
    print("\n" + "🧪 API SPEED TEST" + "\n")
    
    results = []
    
    try:
        results.append(("Basic Fetching", test_parallel_fetching()))
    except Exception as e:
        print(f"\n❌ Basic test failed: {e}")
        results.append(("Basic Fetching", False))
    
    try:
        results.append(("With Scoring", test_with_scoring()))
    except Exception as e:
        print(f"\n❌ Scoring test failed: {e}")
        results.append(("With Scoring", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}  {test_name}")
    
    passed_count = sum(1 for _, p in results if p)
    total = len(results)
    
    if passed_count == total:
        print(f"\n   🎉 All {total} tests passed! API is fast!")
        print("\n   Ready to use:")
        print("   1. Start server: python run.py")
        print("   2. Open: http://localhost:8003/static/news_feed_full.html")
        return 0
    else:
        print(f"\n   ⚠️  {passed_count}/{total} tests passed")
        print("\n   Troubleshooting:")
        print("   - Check internet connection")
        print("   - Some RSS feeds might be slow/down")
        print("   - Try reducing max_per_source")
        return 1


if __name__ == '__main__':
    sys.exit(main())

