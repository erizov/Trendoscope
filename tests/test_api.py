#!/usr/bin/env python3
"""Test API endpoint locally to find the error."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from trendascope.pipeline.orchestrator import run_pipeline

print("Testing API pipeline call...")
print("=" * 60)

try:
    result = run_pipeline(
        blog_url="https://civil-engineer.livejournal.com",
        max_posts=5,  # Small number for testing
        mode="logospheric",
        provider="demo"
    )
    
    print("SUCCESS!")
    print(f"Posts analyzed: {result['stats']['analyzed_posts']}")
    print(f"Trends found: {len(result['trends'])}")
    print(f"Summary: {result['generated']['summary'][:100]}...")
    
except Exception as e:
    print(f"ERROR: {e}")
    print("\nFull traceback:")
    import traceback
    traceback.print_exc()

