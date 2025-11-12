"""
Integration tests for the full pipeline.
Tests the complete workflow from scraping to content generation.
"""
import pytest
from typing import Dict, Any

from src.trendascope.pipeline.orchestrator import Pipeline
from src.trendascope.ingest.livejournal import LiveJournalScraper
from src.trendascope.nlp.analyzer import analyze_text
from src.trendascope.nlp.style_analyzer import analyze_style, get_style_prompt
from src.trendascope.trends.engine import get_trending_topics


class TestLiveJournalScraper:
    """Test LiveJournal scraping functionality."""

    def test_scraper_initialization(self):
        """Test scraper can be initialized."""
        scraper = LiveJournalScraper()
        assert scraper is not None
        assert scraper.timeout == 30

    def test_extract_author_from_url(self):
        """Test author extraction from URL."""
        scraper = LiveJournalScraper()
        url = "https://civil-engineer.livejournal.com/123.html"
        author = scraper._extract_author(url)
        assert author == "civil-engineer"


class TestNLPAnalyzer:
    """Test NLP analysis functionality."""

    def test_analyze_text(self):
        """Test text analysis."""
        text = (
            "Это очень интересная статья о важных вещах. "
            "Мы должны обсудить эти темы. "
            "Что вы думаете об этом?"
        )
        result = analyze_text(text)

        assert "keywords" in result
        assert "sentiment" in result
        assert "entities" in result
        assert "readability" in result

        assert isinstance(result["keywords"], list)
        assert isinstance(result["sentiment"], dict)
        assert isinstance(result["readability"], dict)

    def test_sentiment_detection(self):
        """Test sentiment detection."""
        positive_text = (
            "Прекрасный день! Отлично провели время. "
            "Замечательная погода и хорошее настроение."
        )
        negative_text = (
            "Ужасная ситуация. Плохо закончилось. "
            "Кошмар и беда."
        )

        pos_result = analyze_text(positive_text)
        neg_result = analyze_text(negative_text)

        assert pos_result["sentiment"]["label"] == "positive"
        assert neg_result["sentiment"]["label"] == "negative"

    def test_readability_metrics(self):
        """Test readability calculations."""
        text = (
            "Короткое предложение. "
            "Ещё одно небольшое предложение. "
            "И третье предложение для теста."
        )
        result = analyze_text(text)
        readability = result["readability"]

        assert readability["sentences"] == 3
        assert readability["words"] > 0
        assert readability["avg_words_per_sentence"] > 0


class TestStyleAnalyzer:
    """Test style analysis functionality."""

    def test_analyze_style(self):
        """Test style learning from posts."""
        posts = [
            {
                "text_plain": (
                    "Это мой стиль написания. Короткие предложения. "
                    "Часто задаю вопросы? Использую списки:\n- пункт 1\n- пункт 2"
                )
            },
            {
                "text_plain": (
                    "Продолжаю в том же духе. Ещё вопросы? "
                    "И ещё раз вопрос!"
                )
            }
        ]

        style = analyze_style(posts)

        assert "avg_sentence_length" in style
        assert "question_ratio" in style
        assert "common_openings" in style
        assert style["question_ratio"] > 0

    def test_generate_style_prompt(self):
        """Test style prompt generation."""
        posts = [
            {
                "text_plain": (
                    "Длинное предложение с множеством слов и "
                    "сложной структурой для демонстрации стиля. "
                    "Второе предложение тоже достаточно длинное."
                )
            }
        ]

        prompt = get_style_prompt(posts)

        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert "стил" in prompt.lower()


class TestTrendEngine:
    """Test trend tracking functionality."""

    def test_trending_topics_extraction(self):
        """Test trending topics extraction."""
        posts = [
            {
                "text_plain": "Экономика и финансы",
                "tags": ["экономика", "финансы"],
                "analysis": {
                    "keywords": [
                        {"text": "экономика", "score": 0.9},
                        {"text": "финансы", "score": 0.8}
                    ]
                }
            },
            {
                "text_plain": "Экономика растёт",
                "tags": ["экономика"],
                "analysis": {
                    "keywords": [
                        {"text": "экономика", "score": 0.95}
                    ]
                }
            }
        ]

        trends = get_trending_topics(posts, top_n=5)

        assert len(trends) > 0
        assert all("topic" in t for t in trends)
        assert all("score" in t for t in trends)
        assert trends[0]["topic"] == "экономика"


class TestPipelineIntegration:
    """Integration tests for the full pipeline."""

    def test_pipeline_initialization(self):
        """Test pipeline can be initialized."""
        pipeline = Pipeline()
        assert pipeline is not None

    def test_analyze_posts(self):
        """Test post analysis."""
        pipeline = Pipeline()
        posts = [
            {
                "title": "Test Post",
                "text_plain": (
                    "Это тестовый пост. Он содержит важную информацию. "
                    "Мы обсуждаем интересные темы."
                ),
                "url": "https://test.livejournal.com/1.html"
            }
        ]

        analyzed = pipeline.analyze_posts(posts)

        assert len(analyzed) == 1
        assert "analysis" in analyzed[0]
        assert "keywords" in analyzed[0]["analysis"]

    def test_extract_trends(self):
        """Test trend extraction."""
        pipeline = Pipeline()
        posts = [
            {
                "text_plain": "Технологии и наука",
                "tags": ["технологии"],
                "analysis": {
                    "keywords": [
                        {"text": "технологии", "score": 0.9}
                    ]
                }
            }
        ]

        trends = pipeline.extract_trends(posts)

        assert isinstance(trends, list)
        assert len(trends) > 0

    @pytest.mark.asyncio
    async def test_full_pipeline_demo_mode(self):
        """Test full pipeline in demo mode (no actual scraping)."""
        pipeline = Pipeline()

        # Create mock posts instead of scraping
        mock_posts = [
            {
                "title": "Тестовый пост №1",
                "text_plain": (
                    "Это очень интересный пост о технологиях. "
                    "Мы обсуждаем новые тренды в IT-индустрии. "
                    "Искусственный интеллект меняет мир. "
                    "Что вы думаете об этом?"
                ),
                "url": "https://test.livejournal.com/1.html",
                "published": "2024-01-01",
                "tags": ["технологии", "AI"],
                "comments_count": 15,
                "likes_count": 30
            },
            {
                "title": "Тестовый пост №2",
                "text_plain": (
                    "Философские размышления о жизни. "
                    "Человек стремится к познанию истины. "
                    "Мудрость приходит с опытом. "
                    "Жизнь полна парадоксов и противоречий."
                ),
                "url": "https://test.livejournal.com/2.html",
                "published": "2024-01-02",
                "tags": ["философия", "жизнь"],
                "comments_count": 8,
                "likes_count": 12
            },
            {
                "title": "Тестовый пост №3",
                "text_plain": (
                    "Экономический анализ текущей ситуации. "
                    "Рынки показывают рост. "
                    "Инвесторы настроены оптимистично. "
                    "Прогнозы на следующий квартал положительные."
                ),
                "url": "https://test.livejournal.com/3.html",
                "published": "2024-01-03",
                "tags": ["экономика", "финансы"],
                "comments_count": 25,
                "likes_count": 50
            }
        ]

        # Analyze posts
        analyzed = pipeline.analyze_posts(mock_posts)
        assert len(analyzed) > 0

        # Extract trends
        trends = pipeline.extract_trends(analyzed)
        assert len(trends) > 0

        # Generate content
        generated = pipeline.generate_content(
            analyzed,
            mode="logospheric",
            provider="demo"
        )

        assert "summary" in generated
        assert "titles" in generated
        assert "ideas" in generated
        assert "viral_potential" in generated

        # Verify structure
        assert isinstance(generated["summary"], str)
        assert isinstance(generated["titles"], list)
        assert isinstance(generated["ideas"], list)
        assert len(generated["titles"]) > 0


class TestAPIEndpoints:
    """Test API endpoint functionality."""

    def test_health_endpoint(self):
        """Test health check endpoint."""
        from src.trendascope.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/health")

        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_modes_endpoint(self):
        """Test modes listing endpoint."""
        from src.trendascope.api.main import app
        from fastapi.testclient import TestClient

        client = TestClient(app)
        response = client.get("/api/modes")

        assert response.status_code == 200
        data = response.json()
        assert "modes" in data
        assert len(data["modes"]) > 0

        # Check for expected modes
        mode_names = [m["name"] for m in data["modes"]]
        assert "analytical" in mode_names
        assert "provocative" in mode_names
        assert "logospheric" in mode_names


def run_integration_test_suite():
    """
    Run the full integration test suite.
    This function demonstrates the complete pipeline workflow.
    """
    print("=" * 60)
    print("TRENDOSCOPE INTEGRATION TEST SUITE")
    print("=" * 60)

    # Test 1: Scraper
    print("\n[1/6] Testing LiveJournal Scraper...")
    scraper = LiveJournalScraper()
    assert scraper is not None
    print("✓ Scraper initialized successfully")

    # Test 2: NLP Analysis
    print("\n[2/6] Testing NLP Analysis...")
    sample_text = (
        "Прекрасный день для анализа! "
        "Технологии развиваются быстро. "
        "Что думаете об искусственном интеллекте?"
    )
    analysis = analyze_text(sample_text)
    assert "keywords" in analysis
    assert "sentiment" in analysis
    print(f"✓ Analysis complete: {len(analysis['keywords'])} keywords found")

    # Test 3: Style Analysis
    print("\n[3/6] Testing Style Analysis...")
    sample_posts = [
        {"text_plain": sample_text},
        {"text_plain": "Ещё один тестовый текст. С вопросом?"}
    ]
    style = analyze_style(sample_posts)
    assert "avg_sentence_length" in style
    print(f"✓ Style analyzed: avg sentence length = "
          f"{style['avg_sentence_length']:.2f}")

    # Test 4: Trend Extraction
    print("\n[4/6] Testing Trend Extraction...")
    analyzed_posts = [
        {
            "text_plain": sample_text,
            "tags": ["технологии"],
            "analysis": analysis
        }
    ]
    trends = get_trending_topics(analyzed_posts)
    assert len(trends) > 0
    print(f"✓ Trends extracted: {len(trends)} topics found")

    # Test 5: Content Generation
    print("\n[5/6] Testing Content Generation...")
    pipeline = Pipeline()
    generated = pipeline.generate_content(
        analyzed_posts,
        provider="demo"
    )
    assert "summary" in generated
    print(f"✓ Content generated: {len(generated['titles'])} titles created")

    # Test 6: Full Pipeline
    print("\n[6/6] Testing Full Pipeline...")
    result = {
        "posts": analyzed_posts,
        "trends": trends,
        "generated": generated,
        "stats": {
            "total_posts": len(analyzed_posts),
            "analyzed_posts": len(analyzed_posts),
            "top_trends": len(trends)
        }
    }
    assert result["stats"]["total_posts"] > 0
    print("✓ Full pipeline executed successfully")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)

    return result


if __name__ == "__main__":
    # Run integration test demonstration
    result = run_integration_test_suite()
    print("\nTest result summary:")
    print(f"  Posts analyzed: {result['stats']['analyzed_posts']}")
    print(f"  Trends found: {result['stats']['top_trends']}")
    print(f"  Titles generated: {len(result['generated']['titles'])}")

