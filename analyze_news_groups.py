#!/usr/bin/env python3
"""
Analyze available news and suggest meaningful groups/categories.
"""
import sys
import os
from collections import Counter, defaultdict
import re

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trendascope.ingest.news_sources import NewsAggregator
from trendascope.nlp.controversy_scorer import ControversyScorer


def extract_keywords(text):
    """Extract important keywords from text."""
    # Convert to lowercase
    text = text.lower()
    
    # Common stop words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'can', 'в', 'и', 'на', 'с', 'по',
        'за', 'из', 'к', 'о', 'от', 'что', 'как', 'это', 'для', 'не', 'то',
        'же', 'был', 'была', 'были', 'будет', 'может', 'быть', 'весь',
    }
    
    # Extract words (2+ characters)
    words = re.findall(r'\b[a-zа-яё]{2,}\b', text)
    
    # Filter stop words and get meaningful keywords
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    return keywords


def analyze_topics(news_items):
    """Analyze news and group by topics."""
    print("\n" + "=" * 70)
    print("📊 ANALYZING NEWS TOPICS")
    print("=" * 70)
    
    # Collect all keywords
    all_keywords = []
    keyword_to_news = defaultdict(list)
    
    for i, item in enumerate(news_items):
        text = f"{item['title']} {item['summary']}"
        keywords = extract_keywords(text)
        all_keywords.extend(keywords)
        
        for keyword in keywords:
            keyword_to_news[keyword].append(i)
    
    # Count keyword frequencies
    keyword_counts = Counter(all_keywords)
    
    print(f"\n📰 Analyzed {len(news_items)} news items")
    print(f"🔤 Found {len(keyword_counts)} unique keywords")
    
    # Top keywords overall
    print("\n🔥 TOP 20 KEYWORDS (most frequent):")
    print("-" * 70)
    for keyword, count in keyword_counts.most_common(20):
        percentage = (count / len(news_items)) * 100
        bar = "█" * min(int(percentage), 50)
        print(f"   {keyword:20s} [{count:3d}] {bar} {percentage:.1f}%")
    
    return keyword_counts, keyword_to_news


def suggest_groups(news_items, keyword_counts, keyword_to_news):
    """Suggest meaningful news groups based on content."""
    print("\n" + "=" * 70)
    print("💡 SUGGESTED NEWS GROUPS")
    print("=" * 70)
    
    # Define topic clusters based on keywords
    topic_clusters = {
        'AI & Technology': {
            'keywords': ['ai', 'artificial', 'intelligence', 'gpt', 'chatgpt', 'llm', 
                        'machine', 'learning', 'neural', 'model', 'openai', 'google',
                        'tech', 'technology', 'algorithm', 'data', 'ии', 'нейросет',
                        'технолог', 'алгоритм', 'модел'],
            'news': set(),
            'icon': '🤖'
        },
        'US Politics': {
            'keywords': ['biden', 'trump', 'usa', 'america', 'washington', 'congress',
                        'republican', 'democrat', 'белый', 'дом', 'сша', 'америк'],
            'news': set(),
            'icon': '🇺🇸'
        },
        'Russia & CIS': {
            'keywords': ['putin', 'russia', 'moscow', 'kremlin', 'путин', 'россия',
                        'москв', 'кремл', 'российск', 'рф', 'украин', 'беларус'],
            'news': set(),
            'icon': '🇷🇺'
        },
        'Europe & EU': {
            'keywords': ['europe', 'european', 'eu', 'brussels', 'germany', 'france',
                        'европ', 'евросоюз', 'брюссель', 'германи', 'франци'],
            'news': set(),
            'icon': '🇪🇺'
        },
        'Business & Economy': {
            'keywords': ['market', 'stock', 'economy', 'business', 'company', 'ceo',
                        'startup', 'investment', 'бизнес', 'компани', 'рынок', 'стартап',
                        'экономик', 'инвестиц', 'акци'],
            'news': set(),
            'icon': '💼'
        },
        'War & Conflict': {
            'keywords': ['war', 'military', 'army', 'weapon', 'conflict', 'attack',
                        'война', 'военн', 'армия', 'оружи', 'конфликт', 'атак', 'удар'],
            'news': set(),
            'icon': '⚔️'
        },
        'Science & Research': {
            'keywords': ['science', 'research', 'study', 'university', 'scientist',
                        'наука', 'исследован', 'ученые', 'университет'],
            'news': set(),
            'icon': '🔬'
        },
        'Social & Society': {
            'keywords': ['social', 'people', 'protest', 'rights', 'law', 'court',
                        'социальн', 'люди', 'протест', 'права', 'закон', 'суд'],
            'news': set(),
            'icon': '👥'
        },
        'Media & Internet': {
            'keywords': ['media', 'internet', 'online', 'platform', 'website', 'social',
                        'медиа', 'интернет', 'сайт', 'платформ', 'онлайн'],
            'news': set(),
            'icon': '📱'
        },
        'Energy & Climate': {
            'keywords': ['energy', 'climate', 'oil', 'gas', 'renewable', 'environmental',
                        'энергия', 'климат', 'нефть', 'газ', 'экология'],
            'news': set(),
            'icon': '⚡'
        }
    }
    
    # Classify each news item
    for i, item in enumerate(news_items):
        text = f"{item['title']} {item['summary']}".lower()
        keywords = extract_keywords(text)
        
        # Check which topics match
        for topic, data in topic_clusters.items():
            for keyword in keywords:
                if any(kw in keyword for kw in data['keywords']):
                    data['news'].add(i)
                    break
    
    # Sort by number of news items
    sorted_topics = sorted(
        topic_clusters.items(),
        key=lambda x: len(x[1]['news']),
        reverse=True
    )
    
    # Display suggested groups
    print("\n📋 RECOMMENDED CATEGORIES:")
    print("-" * 70)
    
    for topic, data in sorted_topics:
        count = len(data['news'])
        if count > 0:
            percentage = (count / len(news_items)) * 100
            bar = "█" * min(int(percentage / 2), 30)
            print(f"\n   {data['icon']} {topic:25s} [{count:3d} items] {percentage:.1f}%")
            print(f"      {bar}")
            
            # Show sample headlines
            sample_indices = list(data['news'])[:3]
            for idx in sample_indices:
                title = news_items[idx]['title'][:60]
                print(f"      • {title}...")
    
    return topic_clusters


def analyze_sources(news_items):
    """Analyze news by source."""
    print("\n" + "=" * 70)
    print("📰 NEWS BY SOURCE")
    print("=" * 70)
    
    source_counts = Counter(item['source'] for item in news_items)
    
    print(f"\n📊 {len(source_counts)} active sources:")
    print("-" * 70)
    
    for source, count in source_counts.most_common(15):
        bar = "█" * min(count * 2, 40)
        print(f"   {source:25s} [{count:2d}] {bar}")
    
    return source_counts


def analyze_controversy(news_items):
    """Analyze controversy distribution."""
    print("\n" + "=" * 70)
    print("🔥 CONTROVERSY ANALYSIS")
    print("=" * 70)
    
    scorer = ControversyScorer()
    scored_items = scorer.score_batch(news_items)
    
    # Group by controversy level
    explosive = [item for item in scored_items if item['controversy']['score'] >= 75]
    hot = [item for item in scored_items if 60 <= item['controversy']['score'] < 75]
    spicy = [item for item in scored_items if 40 <= item['controversy']['score'] < 60]
    mild = [item for item in scored_items if item['controversy']['score'] < 40]
    
    print(f"\n📊 Controversy Distribution:")
    print("-" * 70)
    print(f"   💥 Explosive (75-100%): {len(explosive):3d} items {len(explosive)/len(scored_items)*100:5.1f}%")
    print(f"   🔥 Hot      (60-74%):  {len(hot):3d} items {len(hot)/len(scored_items)*100:5.1f}%")
    print(f"   🌶️  Spicy    (40-59%):  {len(spicy):3d} items {len(spicy)/len(scored_items)*100:5.1f}%")
    print(f"   📰 Mild     (0-39%):   {len(mild):3d} items {len(mild)/len(scored_items)*100:5.1f}%")
    
    # Show most controversial
    if explosive or hot:
        print(f"\n🔥 MOST CONTROVERSIAL NEWS:")
        print("-" * 70)
        top_controversial = sorted(scored_items, key=lambda x: x['controversy']['score'], reverse=True)[:5]
        for i, item in enumerate(top_controversial, 1):
            score = item['controversy']['score']
            emoji = item['controversy']['emoji']
            print(f"\n   {i}. [{score}% {emoji}] {item['title']}")
            print(f"      Source: {item['source']}")
            print(f"      Summary: {item['summary'][:100]}...")
    
    return scored_items


def generate_category_config(topic_clusters, news_items):
    """Generate code for implementing suggested categories."""
    print("\n" + "=" * 70)
    print("💻 GENERATED CATEGORY CONFIGURATION")
    print("=" * 70)
    
    print("\n📝 Add to news_feed_full.html:")
    print("-" * 70)
    print("```html")
    print('<div class="categories">')
    print('    <button class="category-btn active" data-category="all">')
    print('        <span>🌍</span> Все')
    print('    </button>')
    
    sorted_topics = sorted(
        topic_clusters.items(),
        key=lambda x: len(x[1]['news']),
        reverse=True
    )
    
    for topic, data in sorted_topics:
        count = len(data['news'])
        if count >= 3:  # Only show categories with 3+ items
            category_id = topic.lower().replace(' ', '_').replace('&', 'and')
            print(f'    <button class="category-btn" data-category="{category_id}">')
            print(f'        <span>{data["icon"]}</span> {topic}')
            print('    </button>')
    
    print('</div>')
    print("```")
    
    print("\n📝 Add to api/main.py categorization:")
    print("-" * 70)
    print("```python")
    print("def _categorize_news(item: Dict[str, Any]) -> str:")
    print('    """Categorize news item based on content."""')
    print("    text = f\"{item.get('title', '')} {item.get('summary', '')}\".lower()")
    print()
    
    for topic, data in sorted_topics:
        count = len(data['news'])
        if count >= 3:
            category_id = topic.lower().replace(' ', '_').replace('&', 'and')
            keywords_str = ', '.join([f"'{kw[:10]}'" for kw in data['keywords'][:5]])
            print(f"    # {topic} ({count} items)")
            print(f"    {category_id}_keywords = [{keywords_str}, ...]")
            print(f"    if any(kw in text for kw in {category_id}_keywords):")
            print(f"        return '{category_id}'")
            print()
    
    print("    return 'general'")
    print("```")


def main():
    """Run news analysis."""
    print("\n" + "🔍 NEWS GROUPS ANALYZER" + "\n")
    
    print("📡 Fetching news from all sources...")
    print("   (This may take 5-10 seconds with parallel fetching)")
    
    try:
        aggregator = NewsAggregator(timeout=5)
        
        # Fetch from all sources
        news_items = aggregator.fetch_trending_topics(
            include_russian=True,
            include_international=True,
            include_ai=True,
            include_politics=True,
            include_us=True,
            include_eu=True,
            max_per_source=3,
            parallel=True,
            max_workers=10
        )
        
        if not news_items:
            print("\n❌ No news items fetched!")
            print("   Check internet connection or try again.")
            return 1
        
        print(f"\n✅ Fetched {len(news_items)} news items")
        
        # Analyze sources
        source_counts = analyze_sources(news_items)
        
        # Analyze topics and keywords
        keyword_counts, keyword_to_news = analyze_topics(news_items)
        
        # Suggest groups
        topic_clusters = suggest_groups(news_items, keyword_counts, keyword_to_news)
        
        # Analyze controversy
        scored_items = analyze_controversy(news_items)
        
        # Generate configuration code
        generate_category_config(topic_clusters, news_items)
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY & RECOMMENDATIONS")
        print("=" * 70)
        
        print(f"\n✅ Successfully analyzed {len(news_items)} news items")
        print(f"📰 From {len(source_counts)} different sources")
        print(f"🔤 Extracted {len(keyword_counts)} unique keywords")
        
        # Count categories with content
        active_categories = sum(1 for _, data in topic_clusters.items() if len(data['news']) >= 3)
        print(f"💡 Found {active_categories} meaningful categories (3+ items each)")
        
        print("\n🎯 RECOMMENDED ACTIONS:")
        print("-" * 70)
        print("   1. Review the suggested categories above")
        print("   2. Use the generated code to update news_feed_full.html")
        print("   3. Update categorization logic in api/main.py")
        print("   4. Test with: python run.py")
        print("   5. Open: http://localhost:8003/static/news_feed_full.html")
        
        print("\n💡 TIPS:")
        print("-" * 70)
        print("   • Focus on categories with 10+ items for best UX")
        print("   • Combine similar categories (e.g., War + Politics)")
        print("   • Add emoji icons for visual appeal")
        print("   • Keep category names short (< 15 chars)")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

