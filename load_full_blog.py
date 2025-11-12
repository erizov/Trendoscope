"""
Load entire civil-engineer.livejournal.com blog into RAG.
Creates comprehensive style guide from all available posts.

Usage:
    python load_full_blog.py
    
    # Or with custom parameters:
    python load_full_blog.py --max-posts 500 --blog-url https://custom-blog.livejournal.com
"""
import sys
import io
import argparse
from pathlib import Path

# Fix UTF-8 encoding for console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from trendascope.ingest.livejournal import scrape_livejournal
from trendascope.nlp.analyzer import analyze_text
from trendascope.nlp.style_analyzer import analyze_style
from trendascope.index.vector_db import get_store
from trendascope.storage.style_storage import save_analysis_results


def load_full_blog(
    blog_url: str = "https://civil-engineer.livejournal.com",
    max_posts: int = 500
):
    """
    Load entire blog into RAG storage.
    
    Args:
        blog_url: Blog URL to scrape
        max_posts: Maximum number of posts to load (0 = all)
    """
    print("=" * 60)
    print("📚 LOADING FULL BLOG INTO RAG")
    print("=" * 60)
    print(f"\n🌐 Blog URL: {blog_url}")
    print(f"📊 Max posts: {max_posts if max_posts > 0 else 'ALL'}")
    print()
    
    # Step 1: Scrape blog
    print("🔍 Step 1/5: Scraping blog posts...")
    print("⏳ This may take several minutes...")
    
    try:
        posts = scrape_livejournal(
            blog_url=blog_url,
            max_posts=max_posts
        )
        
        print(f"✅ Scraped {len(posts)} posts")
        
        if not posts:
            print("❌ No posts found! Check blog URL.")
            return
            
    except Exception as e:
        print(f"❌ Error scraping: {e}")
        return
    
    # Step 2: Analyze posts
    print("\n📝 Step 2/5: Analyzing posts with NLP...")
    analyzed_posts = []
    
    for i, post in enumerate(posts, 1):
        if i % 10 == 0:
            print(f"   Analyzed {i}/{len(posts)} posts...")
        
        try:
            # Analyze text
            analysis = analyze_text(post.get('text', ''))
            
            # Merge analysis with post
            analyzed_post = {
                **post,
                'keywords': analysis.get('keywords', []),
                'sentiment': analysis.get('sentiment', {}),
                'entities': analysis.get('entities', [])
            }
            analyzed_posts.append(analyzed_post)
            
        except Exception as e:
            print(f"   ⚠️  Warning: Failed to analyze post {i}: {e}")
            analyzed_posts.append(post)
    
    print(f"✅ Analyzed {len(analyzed_posts)} posts")
    
    # Step 3: Analyze author's style
    print("\n🎨 Step 3/5: Analyzing author's writing style...")
    
    try:
        style_data = analyze_style(analyzed_posts)
        
        print("✅ Style analysis complete:")
        print(f"   - Common phrases: {len(style_data.get('common_phrases', []))}")
        print(f"   - Vocabulary size: {len(style_data.get('vocabulary', []))}")
        print(f"   - Average length: {style_data.get('avg_length', 0):.0f} chars")
        print(f"   - Sentiment: {style_data.get('avg_sentiment', {}).get('label', 'neutral')}")
        
    except Exception as e:
        print(f"❌ Error analyzing style: {e}")
        style_data = {}
    
    # Step 4: Add to vector DB (RAG)
    print("\n💾 Step 4/5: Adding posts to vector database (RAG)...")
    
    try:
        store = get_store()
        
        # Add documents to FAISS with automatic persistence
        store.add_documents(analyzed_posts)
        
        print(f"✅ Added {len(analyzed_posts)} posts to vector DB")
        print(f"   - Storage: data/faiss_index.bin")
        print(f"   - Documents: data/faiss_docs.json")
        
    except Exception as e:
        print(f"❌ Error adding to RAG: {e}")
        return
    
    # Step 5: Save style guide
    print("\n📁 Step 5/5: Saving style guide...")
    
    try:
        save_analysis_results(
            posts=analyzed_posts,
            style_data=style_data,
            blog_url=blog_url
        )
        
        print("✅ Style guide saved:")
        print("   - Style: data/style_guide.json")
        print("   - Metadata: data/posts_metadata.json")
        
    except Exception as e:
        print(f"❌ Error saving style: {e}")
        return
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 SUCCESS! Blog loaded into RAG")
    print("=" * 60)
    print(f"\n📊 Statistics:")
    print(f"   - Total posts: {len(analyzed_posts)}")
    print(f"   - Vector embeddings: {len(analyzed_posts)}")
    print(f"   - Style phrases: {len(style_data.get('common_phrases', []))}")
    print(f"   - Vocabulary: {len(style_data.get('vocabulary', []))}")
    
    print(f"\n💾 Storage location: data/")
    print("   - faiss_index.bin (vector embeddings)")
    print("   - faiss_docs.json (full posts)")
    print("   - style_guide.json (writing style)")
    print("   - posts_metadata.json (metadata)")
    
    print(f"\n✅ Ready for post generation!")
    print("   Go to http://localhost:8003 and generate posts")
    print("   without re-analyzing - it's all in RAG now!")
    print()


def show_current_storage():
    """Show what's currently in storage."""
    from trendascope.storage.style_storage import has_saved_style, load_style_guide
    from trendascope.index.vector_db import get_store
    
    print("=" * 60)
    print("📊 CURRENT RAG STORAGE STATUS")
    print("=" * 60)
    
    # Check style guide
    if has_saved_style():
        style = load_style_guide()
        print("\n✅ Style Guide: Found")
        print(f"   - Blog: {style.get('blog_url', 'unknown')}")
        print(f"   - Saved: {style.get('saved_at', 'unknown')}")
        print(f"   - Version: {style.get('version', 'unknown')}")
    else:
        print("\n❌ Style Guide: Not found")
    
    # Check vector DB
    try:
        store = get_store()
        if hasattr(store, 'documents') and store.documents:
            print(f"\n✅ Vector DB (RAG): {len(store.documents)} posts")
            print(f"   - Storage: data/faiss_index.bin")
            print(f"   - Size: {Path('data/faiss_index.bin').stat().st_size / 1024:.1f} KB")
        else:
            print("\n❌ Vector DB (RAG): Empty")
    except:
        print("\n❌ Vector DB (RAG): Not initialized")
    
    print()


def main():
    """Main function with CLI support."""
    parser = argparse.ArgumentParser(
        description="Load entire blog into RAG storage"
    )
    
    parser.add_argument(
        '--blog-url',
        type=str,
        default='https://civil-engineer.livejournal.com',
        help='Blog URL to load (default: civil-engineer.livejournal.com)'
    )
    
    parser.add_argument(
        '--max-posts',
        type=int,
        default=500,
        help='Maximum posts to load (0 = all, default: 500)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current storage status and exit'
    )
    
    args = parser.parse_args()
    
    # Show status if requested
    if args.status:
        show_current_storage()
        return
    
    # Load blog
    try:
        load_full_blog(
            blog_url=args.blog_url,
            max_posts=args.max_posts
        )
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

