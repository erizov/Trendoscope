#!/usr/bin/env python3
"""
Trendoscope2 startup script.
"""
import sys
import os
import uvicorn

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main():
    """Run the application."""
    print("=" * 60)
    print("Trendoscope2 - Starting...")
    print("=" * 60)
    print()
    print("API will be available at:")
    print("  http://localhost:8004")
    print()
    print("API Documentation:")
    print("  http://localhost:8004/docs")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    uvicorn.run(
        "trendoscope2.api.main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info",
        timeout_keep_alive=1200
    )


if __name__ == "__main__":
    main()

