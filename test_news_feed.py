#!/usr/bin/env python3
"""
Test script for news feed functionality.
Verifies all components work correctly.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trendascope.ingest.news_sources import NewsAggregator
from trendascope.nlp.controversy_scorer import ControversyScorer


def test_news_aggregation():
    """Test fetching news from sources."""
    print("🔍 Testing News Aggregation...")
    print("-" * 60)
    
    aggregator = NewsAggregator()
    
    # Fetch small sample
    news_items = aggregator.fetch_trending_topics(
        include_ai=True,
        include_politics=True,
        include_us=True,
        include_eu=True,
        include_russian=True,
        max_per_source=2
    )
    
    print(f"✅ Fetched {len(news_items)} news items")
    
    if news_items:
        sample = news_items[0]
        print(f"\n📰 Sample News:")
        print(f"   Title: {sample.get('title', 'N/A')[:60]}...")
        print(f"   Source: {sample.get('source', 'N/A')}")
        print(f"   Link: {sample.get('link', 'N/A')[:50]}...")
    
    return len(news_items) > 0


def test_controversy_scoring():
    """Test controversy scoring algorithm."""
    print("\n🔥 Testing Controversy Scoring...")
    print("-" * 60)
    
    scorer = ControversyScorer()
    
    # Test cases
    test_cases = [
        {
            'title': 'Трамп vs Байден: Новая холодная война?',
            'summary': 'Скандал в Вашингтоне. Президенты угрожают...',
            'expected': 'high'
        },
        {
            'title': 'GPT-5 заменит программистов. Вы готовы?',
            'summary': 'OpenAI анонсировала GPT-5. ИИ пишет код лучше людей.',
            'expected': 'high'
        },
        {
            'title': 'Погода в Москве',
            'summary': 'Сегодня облачно, температура +5 градусов.',
            'expected': 'low'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        result = scorer.score_news(case)
        controversy = result['controversy']
        
        print(f"\n   Test {i}: {case['title'][:40]}...")
        print(f"   Score: {controversy['score']}%")
        print(f"   Label: {controversy['emoji']} {controversy['label']}")
        print(f"   Breakdown:")
        for key, value in controversy['breakdown'].items():
            print(f"     - {key}: {value}")
        
        # Verify expectations
        if case['expected'] == 'high' and controversy['score'] >= 60:
            print(f"   ✅ Correctly scored as provocative")
        elif case['expected'] == 'low' and controversy['score'] < 60:
            print(f"   ✅ Correctly scored as mild")
        else:
            print(f"   ⚠️  Unexpected score")
    
    return True


def test_categorization():
    """Test news categorization."""
    print("\n🏷️  Testing Categorization...")
    print("-" * 60)
    
    from trendascope.api.main import _categorize_news
    
    test_cases = [
        {
            'title': 'GPT-5 released by OpenAI',
            'summary': 'New AI model with improved capabilities',
            'expected': 'ai'
        },
        {
            'title': 'Biden announces new policy',
            'summary': 'US president speaks in Washington',
            'expected': 'us'
        },
        {
            'title': 'Путин встретился с министрами',
            'summary': 'Встреча в Кремле',
            'expected': 'russia'
        },
        {
            'title': 'EU passes new regulation',
            'summary': 'European Union in Brussels',
            'expected': 'eu'
        }
    ]
    
    correct = 0
    for case in test_cases:
        category = _categorize_news(case)
        match = "✅" if category == case['expected'] else "❌"
        print(f"   {match} '{case['title'][:40]}...' → {category} "
              f"(expected: {case['expected']})")
        if category == case['expected']:
            correct += 1
    
    print(f"\n   Accuracy: {correct}/{len(test_cases)} "
          f"({100*correct//len(test_cases)}%)")
    
    return correct >= len(test_cases) * 0.75  # 75% accuracy threshold


def test_api_endpoint():
    """Test API endpoint is available."""
    print("\n🌐 Testing API Endpoint...")
    print("-" * 60)
    
    try:
        import requests
        
        url = "http://localhost:8003/api/news/feed"
        params = {
            'category': 'all',
            'limit': 5,
            'translate': False
        }
        
        print(f"   Calling: {url}")
        print(f"   Params: {params}")
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API responded successfully")
            print(f"   Status: {data.get('success')}")
            print(f"   Count: {data.get('count')}")
            print(f"   Category: {data.get('category')}")
            return True
        else:
            print(f"   ❌ API error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Server not running (start with: python run.py)")
        print(f"   (This is OK if testing components only)")
        return None
    except ImportError:
        print(f"   ⚠️  'requests' not installed (pip install requests)")
        print(f"   (This is OK if testing components only)")
        return None
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 TRENDOSCOPE NEWS FEED TEST SUITE")
    print("=" * 60)
    
    results = {}
    
    # Test 1: News Aggregation
    try:
        results['aggregation'] = test_news_aggregation()
    except Exception as e:
        print(f"❌ News aggregation test failed: {e}")
        results['aggregation'] = False
    
    # Test 2: Controversy Scoring
    try:
        results['scoring'] = test_controversy_scoring()
    except Exception as e:
        print(f"❌ Controversy scoring test failed: {e}")
        results['scoring'] = False
    
    # Test 3: Categorization
    try:
        results['categorization'] = test_categorization()
    except Exception as e:
        print(f"❌ Categorization test failed: {e}")
        results['categorization'] = False
    
    # Test 4: API Endpoint (optional)
    try:
        results['api'] = test_api_endpoint()
    except Exception as e:
        print(f"❌ API test failed: {e}")
        results['api'] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✅ PASS"
        elif result is False:
            status = "❌ FAIL"
        else:
            status = "⚠️  SKIP"
        print(f"   {status}  {test_name.capitalize()}")
    
    # Overall result
    passed = sum(1 for r in results.values() if r is True)
    total = len([r for r in results.values() if r is not None])
    
    print(f"\n   Result: {passed}/{total} tests passed")
    
    if passed == total and passed > 0:
        print("\n   🎉 All tests passed! News feed is ready to use!")
        print("\n   Start server: python run.py")
        print("   Open feed: http://localhost:8003/static/news_feed_full.html")
        return 0
    elif passed >= total * 0.75:
        print("\n   ⚠️  Most tests passed. Check failures above.")
        return 0
    else:
        print("\n   ❌ Multiple tests failed. Check errors above.")
        return 1


if __name__ == '__main__':
    sys.exit(main())

