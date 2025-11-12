"""
Check what's currently stored in RAG.
Shows detailed information about vector DB and style guide.

Usage:
    python check_rag.py
"""
import sys
import io
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


def check_rag_status():
    """Display comprehensive RAG status."""
    from trendascope.storage.style_storage import (
        has_saved_style,
        load_style_guide,
        get_storage
    )
    from trendascope.index.vector_db import get_store
    
    print("=" * 70)
    print("📊 RAG STORAGE STATUS - DETAILED REPORT")
    print("=" * 70)
    
    # Check data directory
    data_dir = Path("data")
    if not data_dir.exists():
        print("\n❌ ERROR: data/ directory not found")
        print("   Run analysis first or use load_full_blog.py")
        return
    
    print(f"\n📁 Storage Directory: {data_dir.absolute()}")
    
    # List files in data/
    files = list(data_dir.glob("*"))
    if files:
        print(f"\n   Files ({len(files)}):")
        for f in files:
            size_kb = f.stat().st_size / 1024
            print(f"   - {f.name:<30} {size_kb:>8.1f} KB")
    else:
        print("\n   ⚠️  No files found")
    
    print("\n" + "─" * 70)
    
    # Check Vector DB (FAISS)
    print("\n🔍 VECTOR DATABASE (RAG)")
    print("─" * 70)
    
    try:
        store = get_store()
        
        if hasattr(store, 'documents') and store.documents:
            posts = store.documents
            print(f"\n✅ Status: Loaded")
            print(f"   Posts in RAG: {len(posts)}")
            
            # Statistics
            if posts:
                total_chars = sum(len(p.get('text', '')) for p in posts)
                avg_chars = total_chars / len(posts)
                
                print(f"\n📊 Statistics:")
                print(f"   - Total characters: {total_chars:,}")
                print(f"   - Average post length: {avg_chars:.0f} chars")
                print(f"   - Shortest post: {min(len(p.get('text', '')) for p in posts)} chars")
                print(f"   - Longest post: {max(len(p.get('text', '')) for p in posts)} chars")
                
                # Show sample posts
                print(f"\n📝 Sample Posts (first 3):")
                for i, doc in enumerate(posts[:3], 1):
                    print(f"\n   {i}. {doc.get('title', 'No title')[:60]}")
                    print(f"      URL: {doc.get('url', 'No URL')}")
                    print(f"      Date: {doc.get('published', 'Unknown')}")
                    print(f"      Length: {len(doc.get('text', ''))} chars")
                    if 'keywords' in doc:
                        print(f"      Keywords: {', '.join(doc['keywords'][:5])}")
                
                # Check FAISS index file
                index_file = Path("data/faiss_index.bin")
                if index_file.exists():
                    index_size_kb = index_file.stat().st_size / 1024
                    print(f"\n💾 FAISS Index:")
                    print(f"   - File: {index_file}")
                    print(f"   - Size: {index_size_kb:.1f} KB")
                    print(f"   - Dimension: {store.dimension}d")
                    print(f"   - Model: {store.model.get_sentence_embedding_dimension()}d sentence-transformers")
        else:
            print("\n❌ Status: Empty")
            print("   No posts loaded")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    print("\n" + "─" * 70)
    
    # Check Style Guide
    print("\n🎨 STYLE GUIDE")
    print("─" * 70)
    
    if has_saved_style():
        style_data = load_style_guide()
        
        if style_data:
            print(f"\n✅ Status: Found")
            print(f"   Blog: {style_data.get('blog_url', 'unknown')}")
            print(f"   Saved: {style_data.get('saved_at', 'unknown')}")
            print(f"   Version: {style_data.get('version', 'unknown')}")
            
            style = style_data.get('style', {})
            
            print(f"\n📊 Style Analysis:")
            print(f"   - Common phrases: {len(style.get('common_phrases', []))}")
            print(f"   - Vocabulary words: {len(style.get('vocabulary', []))}")
            print(f"   - Average length: {style.get('avg_length', 0):.0f} chars")
            print(f"   - Sentiment: {style.get('avg_sentiment', {}).get('label', 'unknown')}")
            print(f"   - Typical tags: {len(style.get('typical_tags', []))}")
            print(f"   - Example posts: {len(style.get('examples', []))}")
            
            # Show sample phrases
            phrases = style.get('common_phrases', [])
            if phrases:
                print(f"\n✨ Sample Phrases (top 10):")
                for phrase in phrases[:10]:
                    print(f"   - \"{phrase}\"")
            
            # Show vocabulary
            vocab = style.get('vocabulary', [])
            if vocab:
                print(f"\n📚 Sample Vocabulary (top 10):")
                for word in vocab[:10]:
                    print(f"   - {word}")
            
            # Show tags
            tags = style.get('typical_tags', [])
            if tags:
                print(f"\n🏷️  Typical Tags:")
                print(f"   {', '.join(tags[:15])}")
    else:
        print("\n❌ Status: Not found")
        print("   No style guide saved")
    
    print("\n" + "─" * 70)
    
    # Check Posts Metadata
    print("\n📋 POSTS METADATA")
    print("─" * 70)
    
    storage = get_storage()
    meta = storage.get_posts_metadata()
    
    if meta:
        print(f"\n✅ Status: Found")
        print(f"   Blog: {meta.get('blog_url', 'unknown')}")
        print(f"   Post count: {meta.get('post_count', 0)}")
        print(f"   Saved: {meta.get('saved_at', 'unknown')}")
        
        urls = meta.get('post_urls', [])
        if urls:
            print(f"\n🔗 Sample URLs (first 5):")
            for url in urls[:5]:
                print(f"   - {url}")
    else:
        print("\n❌ Status: Not found")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    
    # Calculate readiness
    has_vector_db = False
    has_style = has_saved_style()
    
    try:
        store = get_store()
        has_vector_db = hasattr(store, 'documents') and len(store.documents) > 0
    except:
        pass
    
    if has_vector_db and has_style:
        print("\n✅ ✅ ✅  READY FOR POST GENERATION! ✅ ✅ ✅")
        print("\n   You can generate posts without re-analyzing:")
        print("   1. Go to http://localhost:8003")
        print("   2. Scroll to 'Генератор постов'")
        print("   3. Select topic and style")
        print("   4. Click 'Сгенерировать пост'")
        print("\n   All data is loaded from RAG storage!")
        
    elif has_vector_db and not has_style:
        print("\n⚠️  PARTIAL: Vector DB ready, but no style guide")
        print("   Run: python load_full_blog.py")
        
    elif not has_vector_db and has_style:
        print("\n⚠️  PARTIAL: Style guide ready, but Vector DB empty")
        print("   Run: python load_full_blog.py")
        
    else:
        print("\n❌ NOT READY: No data in storage")
        print("\n   To populate RAG:")
        print("   1. Option A: python load_full_blog.py")
        print("   2. Option B: Use web UI to analyze blog")
        print("      - Go to http://localhost:8003")
        print("      - Enter blog URL and run analysis")
    
    print()


def main():
    """Main entry point."""
    try:
        check_rag_status()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

