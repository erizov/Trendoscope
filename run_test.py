#!/usr/bin/env python3
"""
Trendoscope2 startup script for testing (no reload).
"""
import sys
import os
import uvicorn

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main():
    """Run the application without reload for testing."""
    print("=" * 60)
    print("Trendoscope2 - Starting (Test Mode, no reload)...")
    print("=" * 60)
    print()
    print("API will be available at:")
    print("  http://localhost:8004")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    uvicorn.run(
        "trendoscope2.api.main:app",
        host="0.0.0.0",
        port=8004,
        reload=False,  # No reload for testing
        log_level="info",
        timeout_keep_alive=1200
    )


if __name__ == "__main__":
    main()
