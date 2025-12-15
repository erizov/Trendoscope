"""
FastAPI application for Trendoscope2.
Minimal setup with essential endpoints.
"""
from fastapi import FastAPI, HTTPException, Query, Request, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional
import logging
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from ..ingest.news_sources import NewsAggregator
from ..nlp.translator import translate_and_summarize_news
from ..storage.news_db import NewsDatabase
from ..config import DATA_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Trendoscope2 API",
    description="Improved news aggregation and content generation",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Trendoscope2",
        "version": "2.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    try:
        # Check Redis
        redis_ok = False
        try:
            import redis
            r = redis.Redis(host='localhost', port=6379, decode_responses=True)
            r.ping()
            redis_ok = True
        except:
            pass
        
        # Check database
        db_ok = False
        try:
            with NewsDatabase() as db:
                stats = db.get_statistics()
                db_ok = True
        except:
            pass
        
        return {
            "status": "healthy" if (redis_ok and db_ok) else "degraded",
            "redis": "ok" if redis_ok else "unavailable",
            "database": "ok" if db_ok else "unavailable"
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/api/news/feed")
async def get_news_feed(
    category: str = Query(default="all", description="Category filter"),
    limit: int = Query(default=20, ge=5, le=100, description="Maximum items"),
    language: str = Query(default="all", description="Language filter (all, ru, en)"),
    translate_to: str = Query(default="none", description="Translate to (none, ru, en)")
):
    """Get news feed."""
    try:
        logger.info(f"Fetching news: category={category}, limit={limit}")
        
        aggregator = NewsAggregator(timeout=5)
        news_items = aggregator.fetch_trending_topics(
            include_russian=True,
            include_international=True,
            include_ai=True,
            include_politics=True,
            include_us=True,
            include_eu=True,
            max_per_source=2,
            parallel=True,
            max_workers=10
        )
        
        logger.info(f"Fetched {len(news_items)} news items")
        
        # Detect and set language for each item
        for item in news_items:
            text = f"{item.get('title', '')} {item.get('summary', '')}"
            cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
            latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
            total_chars = cyrillic_chars + latin_chars
            
            if total_chars > 0:
                cyrillic_ratio = cyrillic_chars / total_chars
                item['language'] = 'ru' if cyrillic_ratio > 0.3 else 'en'
            else:
                item['language'] = 'en'
        
        # Filter by language
        if language != 'all':
            news_items = [item for item in news_items if item.get('language') == language]
        
        # Translate if requested
        if translate_to != 'none' and news_items:
            try:
                items_to_translate = [
                    item for item in news_items
                    if item.get('language') != translate_to
                ]
                if items_to_translate:
                    translated = translate_and_summarize_news(
                        items_to_translate[:3],  # Limit to 3
                        target_language=translate_to,
                        provider="free",
                        max_items=3
                    )
                    # Update in list
                    translated_map = {item.get('link'): item for item in translated}
                    for i, item in enumerate(news_items):
                        if item.get('link') in translated_map:
                            news_items[i] = translated_map[item.get('link')]
            except Exception as e:
                logger.warning(f"Translation failed: {e}")
        
        return {
            "success": True,
            "count": len(news_items),
            "category": category,
            "news": news_items[:limit]
        }
    except Exception as e:
        logger.error(f"Error fetching news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/news/translate")
async def translate_article(
    article: Dict[str, Any] = Body(...),
    target_language: str = Query(..., description="Target language (ru, en)")
):
    """Translate a single article."""
    try:
        title = article.get('title', '').strip()
        summary = article.get('summary', '').strip()
        source_lang = article.get('source_language', article.get('language', 'en'))
        
        if not title and not summary:
            raise HTTPException(status_code=400, detail="Title or summary required")
        
        news_item = {
            'title': title,
            'summary': summary,
            'language': source_lang
        }
        
        translated_items = translate_and_summarize_news(
            [news_item],
            target_language=target_language,
            provider="free",
            max_items=1
        )
        
        if not translated_items:
            raise HTTPException(status_code=500, detail="Translation failed")
        
        translated = translated_items[0]
        
        return {
            "success": True,
            "translated": {
                "title": translated.get('title', title),
                "summary": translated.get('summary', summary)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Translation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/api/rutube/generate")
async def generate_text_from_rutube(
    url: str = Body(..., embed=True, description="Rutube video URL")
):
    """Generate text from Rutube video."""
    try:
        # Import here to avoid errors if dependencies missing
        from ..ingest.rutube_processor import process_rutube_video, validate_rutube_url
        from ..nlp.transcriber import transcribe_audio, detect_language
        import asyncio
        from pathlib import Path
        import shutil
        
        if not validate_rutube_url(url):
            raise HTTPException(status_code=400, detail="Invalid Rutube URL")
        
        temp_dir = None
        try:
            logger.info(f"Processing Rutube video: {url}")
            video_path, audio_path, video_info = await asyncio.to_thread(
                process_rutube_video, url
            )
            temp_dir = video_path.parent
            
            # Detect language
            try:
                audio_path_obj = Path(audio_path) if not isinstance(audio_path, Path) else audio_path
                language = await asyncio.to_thread(detect_language, audio_path_obj, "base")
                lang_code = "ru" if language == "ru" else "en"
            except:
                language = None
                lang_code = "auto"
            
            # Transcribe
            audio_path_obj = Path(audio_path) if not isinstance(audio_path, Path) else audio_path
            transcript_result = await asyncio.to_thread(
                transcribe_audio,
                audio_path_obj,
                language=language,
                model_size="base"
            )
            transcript = transcript_result["text"]
            detected_lang = transcript_result.get("language", language or "en")
            lang_code = "ru" if detected_lang == "ru" else "en"
            
            return {
                "success": True,
                "video_info": video_info,
                "transcript": transcript,
                "language": lang_code,
                "transcript_length": len(transcript)
            }
        finally:
            if temp_dir and temp_dir.exists():
                try:
                    await asyncio.to_thread(shutil.rmtree, temp_dir, ignore_errors=True)
                except:
                    pass
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rutube processing error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to process video: {str(e)}")

