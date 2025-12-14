# 📰 News Coverage & Architecture Improvement Plan

## 🎯 Executive Summary

This plan outlines improvements to expand news coverage, enhance content quality, and modernize the architecture for better scalability, performance, and maintainability.

**Goals:**
- Expand news sources from ~40 to 100+ sources
- Improve content quality and relevance
- Reduce API response time by 50%
- Increase system reliability to 99.9% uptime
- Enable real-time news updates
- Support 10x current traffic

---

## 📊 Current State Analysis

### News Coverage
- **Sources**: ~40 RSS feeds (Russian, International, AI, Politics, US, EU, Legal)
- **Update Frequency**: On-demand (no background jobs)
- **Coverage Gaps**: 
  - Limited regional news
  - No social media sources
  - No video/audio content aggregation
  - Limited non-English sources
  - No real-time breaking news

### Architecture
- **Pattern**: Monolithic FastAPI application
- **Database**: SQLite (development) + PostgreSQL (production)
- **Caching**: Basic Redis + in-memory
- **News Fetching**: Synchronous with ThreadPoolExecutor
- **Translation**: On-demand, no caching
- **Storage**: News database with FTS5 search

### Performance Metrics
- **API Response Time**: 2-5 seconds (news feed)
- **News Fetch Time**: 5-10 seconds (40 sources)
- **Translation Time**: 1-3 seconds per article
- **Database Queries**: No optimization, full table scans

---

## 🚀 Phase 1: News Coverage Expansion (Weeks 1-4)

### 1.1 Add New News Sources (Target: 100+ sources)

#### Russian Sources (Add 20+)
```python
# New sources to add:
RUSSIAN_REGIONAL_SOURCES = [
    "https://www.fontanka.ru/rss/news.xml",  # St. Petersburg
    "https://www.nsk.aif.ru/rss/all.xml",    # Novosibirsk
    "https://www.ekb.aif.ru/rss/all.xml",    # Yekaterinburg
    "https://www.kp.ru/rss/news.xml",        # Komsomolskaya Pravda
    "https://www.mk.ru/rss/news.xml",        # Moskovsky Komsomolets
    "https://www.rg.ru/rss.xml",             # Rossiyskaya Gazeta
]

RUSSIAN_ECONOMY_SOURCES = [
    "https://www.rbc.ru/rss.xml",
    "https://www.vedomosti.ru/rss/news",
    "https://www.kommersant.ru/RSS/main.xml",
    "https://www.forbes.ru/rss.xml",
]

RUSSIAN_CULTURE_SOURCES = [
    "https://www.colta.ru/rss.xml",
    "https://www.afisha.ru/rss/news.xml",
    "https://www.kinopoisk.ru/rss/news.xml",
]

RUSSIAN_SPORTS_SOURCES = [
    "https://www.sport-express.ru/rss/news.xml",
    "https://www.championat.com/rss/news.xml",
]
```

#### International Sources (Add 30+)
```python
INTERNATIONAL_REGIONAL_SOURCES = [
    # Asia-Pacific
    "https://www.scmp.com/rss/feed",
    "https://www.japantimes.co.jp/rss/news/",
    "https://www.straitstimes.com/rss",
    
    # Middle East
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://www.haaretz.com/rss",
    
    # Latin America
    "https://www.bbc.com/mundo/rss.xml",
    "https://www.eluniverso.com/rss/noticias.xml",
    
    # Africa
    "https://www.bbc.com/africa/rss.xml",
]

INTERNATIONAL_BUSINESS_SOURCES = [
    "https://www.bloomberg.com/feed/topics/economics",
    "https://www.ft.com/rss",
    "https://www.wsj.com/xml/rss/3_7085.xml",
    "https://www.reuters.com/rssFeed/worldNews",
]

INTERNATIONAL_TECH_SOURCES = [
    "https://techcrunch.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://arstechnica.com/feed/",
    "https://www.wired.com/feed/rss",
]
```

#### Social Media & Alternative Sources (Add 10+)
```python
SOCIAL_MEDIA_SOURCES = [
    # Twitter/X trending topics (via API)
    # Reddit r/worldnews, r/news (via RSS)
    "https://www.reddit.com/r/worldnews/.rss",
    "https://www.reddit.com/r/news/.rss",
    "https://www.reddit.com/r/technology/.rss",
    
    # Telegram channels (via RSS bridges)
    # YouTube trending (via yt-dlp)
]

VIDEO_SOURCES = [
    # YouTube news channels
    # Rutube news channels
    # Vimeo news
]
```

### 1.2 Implement Source Priority & Quality Scoring

```python
# New module: trendascope/ingest/source_manager.py
class SourceManager:
    """Manage news sources with priority and quality scoring."""
    
    SOURCE_PRIORITY = {
        'high': 1,    # Major news outlets (NYT, BBC, etc.)
        'medium': 2,  # Regional/niche sources
        'low': 3,     # Aggregators, social media
    }
    
    SOURCE_QUALITY_METRICS = {
        'reliability': 0.0,  # Fact-checking score
        'freshness': 0.0,    # Update frequency
        'completeness': 0.0, # Article quality
        'relevance': 0.0,    # Topic relevance
    }
    
    def score_source(self, source_url: str) -> Dict[str, float]:
        """Calculate quality score for a source."""
        # Analyze historical data:
        # - Article completeness (title + summary + full_text)
        # - Update frequency
        # - Controversy score distribution
        # - User engagement
        pass
    
    def get_priority_sources(self, category: str) -> List[str]:
        """Get sources ordered by priority for a category."""
        pass
```

### 1.3 Add News Source Health Monitoring

```python
# New module: trendascope/ingest/source_health.py
class SourceHealthMonitor:
    """Monitor news source availability and quality."""
    
    def check_source_health(self, source_url: str) -> Dict[str, Any]:
        """Check if source is healthy."""
        return {
            'available': True/False,
            'response_time': float,
            'last_success': datetime,
            'error_rate': float,
            'feed_quality': 'good' | 'degraded' | 'broken'
        }
    
    def auto_disable_broken_sources(self):
        """Temporarily disable sources with high error rates."""
        pass
    
    def alert_on_source_issues(self):
        """Send alerts when sources degrade."""
        pass
```

### 1.4 Implement News Deduplication

```python
# New module: trendascope/ingest/deduplicator.py
class NewsDeduplicator:
    """Detect and merge duplicate news articles."""
    
    def find_duplicates(self, news_items: List[Dict]) -> List[List[int]]:
        """Find duplicate articles using:
        - URL matching (exact)
        - Title similarity (fuzzy matching)
        - Content similarity (embeddings)
        - Published time proximity
        """
        pass
    
    def merge_duplicates(self, duplicates: List[Dict]) -> Dict:
        """Merge duplicate articles:
        - Combine sources
        - Keep best summary
        - Aggregate metadata
        """
        pass
```

---

## 🏗️ Phase 2: Architecture Improvements (Weeks 5-8)

### 2.1 Background News Fetching Service

**Problem**: News is fetched on-demand, causing slow API responses.

**Solution**: Background worker that continuously fetches and caches news.

```python
# New module: trendascope/services/news_fetcher_service.py
class NewsFetcherService:
    """Background service for continuous news fetching."""
    
    async def start_fetching_loop(self):
        """Continuously fetch news from all sources."""
        while True:
            # Fetch news in batches
            # Store in database
            # Update cache
            # Sleep for interval
            await asyncio.sleep(60)  # Fetch every minute
    
    async def fetch_category(self, category: str):
        """Fetch news for specific category."""
        pass
```

**Implementation:**
- Use `asyncio` for async fetching
- Celery or RQ for background jobs
- Schedule with APScheduler or Celery Beat
- Store results in database + Redis cache

### 2.2 Async News Aggregation

**Current**: ThreadPoolExecutor (blocking)
**New**: Fully async with `httpx.AsyncClient`

```python
# Refactor: trendascope/ingest/news_sources_async.py
class AsyncNewsAggregator:
    """Fully async news aggregator."""
    
    async def fetch_all_sources(self, sources: List[str]) -> List[Dict]:
        """Fetch all sources concurrently."""
        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = [
                self.fetch_rss_feed_async(client, url)
                for url in sources
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            return self.process_results(results)
    
    async def fetch_rss_feed_async(
        self, 
        client: httpx.AsyncClient, 
        url: str
    ) -> List[Dict]:
        """Fetch single RSS feed asynchronously."""
        try:
            response = await client.get(url)
            return self.parse_rss(response.text)
        except Exception as e:
            logger.error(f"Failed to fetch {url}: {e}")
            return []
```

**Benefits:**
- 3-5x faster fetching
- Better resource utilization
- Non-blocking I/O

### 2.3 Multi-Tier Caching Strategy

```python
# New module: trendascope/core/multi_tier_cache.py
class MultiTierCache:
    """L1 (in-memory) + L2 (Redis) + L3 (database) caching."""
    
    def __init__(self):
        self.l1_cache = {}  # In-memory LRU cache
        self.l2_cache = Redis()  # Distributed cache
        self.l3_cache = NewsDatabase()  # Database
    
    async def get(self, key: str) -> Optional[Any]:
        """Get from cache, trying L1 → L2 → L3."""
        # Try L1
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # Try L2
        value = await self.l2_cache.get(key)
        if value:
            self.l1_cache[key] = value  # Populate L1
            return value
        
        # Try L3
        value = await self.l3_cache.get(key)
        if value:
            await self.l2_cache.set(key, value)  # Populate L2
            self.l1_cache[key] = value  # Populate L1
            return value
        
        return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 3600,
        tags: List[str] = None
    ):
        """Set in all cache tiers."""
        self.l1_cache[key] = value
        await self.l2_cache.set(key, value, ttl)
        # L3 (database) is write-through
    
    async def invalidate_by_tags(self, tags: List[str]):
        """Invalidate cache entries by tags."""
        # Find keys with tags
        # Invalidate in L1, L2, L3
        pass
```

**Cache Keys:**
- `news:feed:{category}:{language}` - News feed
- `news:article:{url_hash}` - Individual article
- `news:translation:{source_lang}:{target_lang}:{text_hash}` - Translations
- `news:controversy:{url_hash}` - Controversy scores

### 2.4 Database Optimization

#### Indexes
```sql
-- Add indexes for common queries
CREATE INDEX idx_news_published_category ON news(published_at DESC, category);
CREATE INDEX idx_news_controversy ON news(controversy_score DESC);
CREATE INDEX idx_news_source_language ON news(source, language);
CREATE INDEX idx_news_fts_title ON news_fts(title);
```

#### Query Optimization
```python
# Optimize common queries
class OptimizedNewsDatabase(NewsDatabase):
    def get_recent_news_optimized(
        self, 
        category: str, 
        limit: int = 20
    ) -> List[Dict]:
        """Optimized query with proper indexes."""
        query = """
            SELECT * FROM news
            WHERE category = ?
            ORDER BY published_at DESC
            LIMIT ?
        """
        # Use prepared statements
        # Use connection pooling
        # Batch operations
        pass
```

#### Connection Pooling
```python
# Use SQLAlchemy connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    "sqlite:///news.db",
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 2.5 Translation Caching & Batching

**Current**: Translate on-demand, no caching
**New**: Cache translations + batch processing

```python
# New module: trendascope/nlp/translation_cache.py
class TranslationCache:
    """Cache translations to avoid re-translating."""
    
    async def translate_with_cache(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate with caching."""
        cache_key = f"translation:{source_lang}:{target_lang}:{hash(text)}"
        
        # Check cache
        cached = await cache.get(cache_key)
        if cached:
            return cached
        
        # Translate
        translated = await translator.translate(text, source_lang, target_lang)
        
        # Cache result
        await cache.set(cache_key, translated, ttl=86400)  # 24 hours
        
        return translated
    
    async def batch_translate(
        self,
        texts: List[str],
        source_lang: str,
        target_lang: str
    ) -> List[str]:
        """Batch translate multiple texts efficiently."""
        # Check cache for all
        # Translate only uncached
        # Batch API calls if possible
        pass
```

### 2.6 News Update Webhooks/SSE

**Real-time updates** for breaking news:

```python
# New endpoint: /api/news/stream
@app.get("/api/news/stream")
async def stream_news_updates(
    category: str = "all",
    last_update: Optional[datetime] = None
):
    """Server-Sent Events for real-time news updates."""
    async def event_generator():
        while True:
            # Check for new news
            new_items = await get_new_news_since(last_update)
            if new_items:
                yield f"data: {json.dumps(new_items)}\n\n"
            await asyncio.sleep(5)  # Check every 5 seconds
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

---

## 🔄 Phase 3: Advanced Features (Weeks 9-12)

### 3.1 News Clustering & Topic Detection

```python
# New module: trendascope/nlp/news_clustering.py
class NewsClusterer:
    """Cluster related news articles."""
    
    def cluster_news(self, news_items: List[Dict]) -> List[Dict]:
        """Group related articles:
        - Use embeddings for similarity
        - DBSCAN or K-means clustering
        - Create topic groups
        """
        pass
    
    def detect_trending_topics(self, news_items: List[Dict]) -> List[str]:
        """Detect trending topics from news."""
        # Extract keywords
        # Count frequency
        # Identify emerging topics
        pass
```

### 3.2 News Sentiment Analysis

```python
# New module: trendascope/nlp/sentiment_analyzer.py
class NewsSentimentAnalyzer:
    """Analyze sentiment of news articles."""
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment:
        - Positive/negative/neutral
        - Emotion detection
        - Bias detection
        """
        return {
            'sentiment': 'positive' | 'negative' | 'neutral',
            'score': float,  # -1 to 1
            'emotions': List[str],
            'bias_score': float
        }
```

### 3.3 News Fact-Checking Integration

```python
# New module: trendascope/nlp/fact_checker.py
class NewsFactChecker:
    """Integrate with fact-checking services."""
    
    def check_facts(self, article: Dict) -> Dict[str, Any]:
        """Check article facts:
        - Cross-reference with trusted sources
        - Flag potential misinformation
        - Provide fact-check links
        """
        return {
            'verified': bool,
            'fact_check_score': float,
            'sources': List[str],
            'warnings': List[str]
        }
```

### 3.4 Personalized News Feed

```python
# New module: trendascope/services/personalized_feed.py
class PersonalizedNewsFeed:
    """Generate personalized news feed."""
    
    def get_personalized_feed(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> List[Dict]:
        """Generate feed based on:
        - User reading history
        - Preferred topics
        - Engagement patterns
        - Time of day
        """
        # Use ML model to rank articles
        # Filter by preferences
        # Boost relevant content
        pass
```

---

## 📈 Phase 4: Performance & Scale (Weeks 13-16)

### 4.1 Database Sharding

```python
# Shard news database by category or date
class ShardedNewsDatabase:
    """Sharded database for horizontal scaling."""
    
    def __init__(self):
        self.shards = {
            'recent': NewsDatabase('news_recent.db'),  # Last 30 days
            'archive': NewsDatabase('news_archive.db'),  # Older
        }
    
    def get_shard(self, date: datetime) -> NewsDatabase:
        """Get appropriate shard for date."""
        if date > datetime.now() - timedelta(days=30):
            return self.shards['recent']
        return self.shards['archive']
```

### 4.2 CDN Integration

- Cache static content (images, CSS, JS)
- Cache API responses at edge
- Use CloudFlare or AWS CloudFront

### 4.3 Load Balancing

```yaml
# nginx.conf
upstream trendoscope_backend {
    least_conn;
    server api1:8003;
    server api2:8003;
    server api3:8003;
}

server {
    listen 80;
    location / {
        proxy_pass http://trendoscope_backend;
    }
}
```

### 4.4 Monitoring & Alerting

```python
# Enhanced monitoring
class NewsSystemMonitor:
    """Monitor news system health."""
    
    METRICS = {
        'news_fetch_duration': Histogram,
        'news_fetch_errors': Counter,
        'cache_hit_rate': Gauge,
        'translation_duration': Histogram,
        'api_response_time': Histogram,
    }
    
    def alert_on_anomalies(self):
        """Alert on:
        - High error rates
        - Slow response times
        - Cache misses
        - Source failures
        """
        pass
```

---

## 🎯 Implementation Priority

### High Priority (Do First)
1. ✅ Background news fetching service
2. ✅ Async news aggregation
3. ✅ Translation caching
4. ✅ Database indexes
5. ✅ Multi-tier caching

### Medium Priority
1. Add 50+ new news sources
2. News deduplication
3. Source health monitoring
4. News clustering
5. Personalized feeds

### Low Priority (Nice to Have)
1. Real-time streaming (SSE)
2. Fact-checking integration
3. Database sharding
4. CDN integration

---

## 📊 Success Metrics

### News Coverage
- **Sources**: 40 → 100+ sources
- **Update Frequency**: On-demand → Every 1-5 minutes
- **Coverage**: Add regional, social media, video sources

### Performance
- **API Response Time**: 2-5s → <1s (80% cache hit)
- **News Fetch Time**: 5-10s → 1-2s (async + caching)
- **Translation Time**: 1-3s → <0.5s (caching)

### Reliability
- **Uptime**: 99% → 99.9%
- **Error Rate**: <1%
- **Source Availability**: 95%+

### User Experience
- **Freshness**: News updated every 1-5 minutes
- **Relevance**: Personalized feeds
- **Quality**: Better deduplication and clustering

---

## 🛠️ Technical Stack Updates

### New Dependencies
```txt
# Background jobs
celery==5.3.4
redis==5.0.1  # Already have

# Async HTTP
httpx==0.26.0  # Already have

# Caching
cachetools==5.3.2

# Monitoring
prometheus-client==0.19.0  # Already have
```

### Infrastructure
- **Background Worker**: Celery + Redis
- **Cache**: Redis Cluster
- **Database**: PostgreSQL (production) with connection pooling
- **Load Balancer**: Nginx or Traefik
- **Monitoring**: Prometheus + Grafana

---

## 📝 Next Steps

1. **Week 1**: Implement background news fetching service
2. **Week 2**: Refactor to async news aggregation
3. **Week 3**: Add multi-tier caching
4. **Week 4**: Optimize database with indexes
5. **Week 5+**: Add new sources, implement advanced features

---

*This plan is a living document and should be updated as implementation progresses.*

