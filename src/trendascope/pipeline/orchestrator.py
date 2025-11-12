"""
Pipeline orchestrator - ties all components together.
"""
import os
from typing import List, Dict, Any, Optional

from ..ingest.livejournal import LiveJournalScraper
from ..nlp.analyzer import analyze_text
from ..nlp.style_analyzer import get_style_prompt, analyze_style
from ..index.vector_db import index_documents
from ..trends.engine import get_trending_topics, calculate_viral_potential
from ..gen.generate import generate_summary
from ..storage.style_storage import save_analysis_results


class Pipeline:
    """Main pipeline for Trendoscope."""

    def __init__(
        self,
        lj_username: Optional[str] = None,
        lj_password: Optional[str] = None
    ):
        """
        Initialize pipeline.

        Args:
            lj_username: LiveJournal username
            lj_password: LiveJournal password
        """
        self.lj_username = lj_username or os.getenv("LJ_USERNAME")
        self.lj_password = lj_password or os.getenv("LJ_PASSWORD")

    def fetch_posts(
        self,
        blog_url: str,
        max_posts: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Fetch posts from LiveJournal.

        Args:
            blog_url: Blog URL
            max_posts: Maximum number of posts

        Returns:
            List of posts
        """
        with LiveJournalScraper(
            self.lj_username,
            self.lj_password
        ) as scraper:
            posts = scraper.fetch_all_posts(
                blog_url,
                max_posts=max_posts
            )

        return posts

    def analyze_posts(
        self,
        posts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze posts with NLP.

        Args:
            posts: List of posts

        Returns:
            Posts with analysis added
        """
        analyzed = []

        for post in posts:
            text = post.get('text_plain', '')
            if not text:
                continue

            # Add NLP analysis
            analysis = analyze_text(text)
            post['analysis'] = analysis

            analyzed.append(post)

        return analyzed

    def index_posts(
        self,
        posts: List[Dict[str, Any]]
    ) -> None:
        """
        Index posts in vector database.

        Args:
            posts: List of posts to index
        """
        index_documents(posts)

    def extract_trends(
        self,
        posts: List[Dict[str, Any]],
        top_n: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Extract trending topics.

        Args:
            posts: Analyzed posts
            top_n: Number of top trends

        Returns:
            List of trending topics
        """
        return get_trending_topics(posts, top_n)

    def generate_content(
        self,
        posts: List[Dict[str, Any]],
        mode: str = "logospheric",
        provider: str = "demo",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate content based on posts.

        Args:
            posts: Analyzed posts
            mode: Generation mode
            provider: LLM provider
            model: Model name

        Returns:
            Generated content
        """
        # Add style information
        style_prompt = get_style_prompt(posts)

        # Generate summary
        result = generate_summary(
            posts,
            mode=mode,
            provider=provider,
            model=model
        )

        # Add style info
        result['style_prompt'] = style_prompt

        return result

    def run_full_pipeline(
        self,
        blog_url: str = "https://civil-engineer.livejournal.com",
        max_posts: int = 50,
        mode: str = "logospheric",
        provider: str = "demo",
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run full pipeline.

        Args:
            blog_url: Blog URL to analyze
            max_posts: Maximum posts to fetch
            mode: Generation mode
            provider: LLM provider
            model: Model name

        Returns:
            Complete pipeline results
        """
        # Step 1: Fetch posts
        posts = self.fetch_posts(blog_url, max_posts)

        # Step 2: Analyze posts
        analyzed_posts = self.analyze_posts(posts)

        # Step 3: Index posts
        self.index_posts(analyzed_posts)

        # Step 4: Extract trends
        trends = self.extract_trends(analyzed_posts)

        # Step 5: Calculate viral potential for each post
        for post in analyzed_posts:
            post['viral_potential'] = calculate_viral_potential(
                post,
                trends
            )

        # Step 6: Generate content
        generated = self.generate_content(
            analyzed_posts[:10],  # Use top 10 posts
            mode=mode,
            provider=provider,
            model=model
        )

        # Step 7: Save analysis results for future use
        style_data = analyze_style(analyzed_posts)
        save_analysis_results(
            posts=analyzed_posts,
            style_data=style_data,
            blog_url=blog_url
        )

        return {
            "posts": analyzed_posts,
            "trends": trends,
            "generated": generated,
            "stats": {
                "total_posts": len(posts),
                "analyzed_posts": len(analyzed_posts),
                "top_trends": len(trends)
            }
        }


def run_pipeline(
    blog_url: str = "https://civil-engineer.livejournal.com",
    max_posts: int = 50,
    mode: str = "logospheric",
    provider: str = "demo",
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run full pipeline (convenience function).

    Args:
        blog_url: Blog URL
        max_posts: Maximum posts to fetch
        mode: Generation mode
        provider: LLM provider
        model: Model name

    Returns:
        Pipeline results
    """
    pipeline = Pipeline()
    return pipeline.run_full_pipeline(
        blog_url,
        max_posts,
        mode,
        provider,
        model
    )

