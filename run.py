#!/usr/bin/env python3
"""
Trendoscope startup script.
Quick launcher for the application.
"""
import sys
import os
import uvicorn


def main():
    """Run the application."""
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

    print("=" * 60)
    print("Запуск Трендоскоп (Trendoscope)")
    print("=" * 60)
    print()
    print("API будет доступен по адресу:")
    print("  http://localhost:8003")
    print()
    print("Документация API:")
    print("  http://localhost:8003/docs")
    print()
    print("Web UI:")
    print("  http://localhost:8003")
    print()
    print("Нажмите Ctrl+C для остановки")
    print("=" * 60)
    print()

    # Run uvicorn
    uvicorn.run(
        "trendascope.api.main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )


if __name__ == "__main__":
    main()

