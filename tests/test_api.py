#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test API endpoint locally to find the error."""
import sys
import os
import io

# Fix UTF-8 encoding for Windows console
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.buffer,
        encoding='utf-8',
        errors='replace'
    )

# Add src to path (go up one level from tests/ folder)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

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

