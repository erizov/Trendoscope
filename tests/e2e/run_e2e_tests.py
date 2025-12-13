#!/usr/bin/env python3
"""
Standalone script to run E2E tests with detailed reporting.
"""
import subprocess
import sys
import json
from pathlib import Path

def main():
    """Run E2E tests and generate report."""
    print("=" * 80)
    print("Trendoscope E2E Test Suite")
    print("=" * 80)
    print()
    
    # Check if server is running
    print("Checking if server is running...")
    try:
        import httpx
        response = httpx.get("http://localhost:8003/api/health", timeout=5)
        if response.status_code in [200, 503]:
            print("✅ Server is running")
        else:
            print("⚠️  Server responded with unexpected status")
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        print("Please start the server with: python run.py")
        sys.exit(1)
    
    print()
    print("Running E2E tests...")
    print()
    
    # Check if pytest-html is available
    html_available = False
    try:
        import pytest_html
        html_available = True
    except ImportError:
        print("⚠️  pytest-html not installed, HTML report will be skipped")
        print("   Install with: pip install pytest-html")
        print()
    
    # Build pytest command
    pytest_cmd = [
        sys.executable, "-m", "pytest",
        "tests/e2e/test_full_system.py",
        "-v",
        "--tb=short"
    ]
    
    # Add HTML report if available
    if html_available:
        pytest_cmd.extend([
            "--html=test_results/e2e_report.html",
            "--self-contained-html"
        ])
    
    # Run pytest
    result = subprocess.run(pytest_cmd, capture_output=False)
    
    print()
    print("=" * 80)
    
    # Load and display report
    report_path = Path("test_results/e2e_report.json")
    if report_path.exists():
        with open(report_path, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        summary = report['summary']
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {summary['total']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']:.2f}%")
        print(f"Duration: {summary['duration_seconds']:.2f}s")
        print()
        
        stats = report['statistics']
        print("DETAILED STATISTICS")
        print("=" * 80)
        print(f"Categories Tested: {len(stats['categories_tested'])}")
        print(f"  - {', '.join(stats['categories_tested'])}")
        print()
        print(f"Authors Tested: {len(stats['authors_tested'])}")
        print(f"  - {', '.join(stats['authors_tested'])}")
        print()
        print(f"Translations Tested: {stats['translations_tested']}")
        print(f"API Endpoints Tested: {len(stats['api_endpoints_tested'])}")
        print(f"  - {', '.join(stats['api_endpoints_tested'])}")
        print()
        print(f"Articles Fetched: {stats['articles_fetched']}")
        print(f"Posts Generated: {stats['posts_generated']}")
        print()
        
        if stats['errors']:
            print("ERRORS")
            print("=" * 80)
            for error in stats['errors']:
                print(f"❌ {error['test']}")
                print(f"   {error['error']}")
                print()
        
        print(f"Full report saved to: {report_path}")
        if html_available:
            print(f"HTML report saved to: test_results/e2e_report.html")
    
    print("=" * 80)
    
    # Exit with pytest exit code
    sys.exit(result.returncode)

if __name__ == "__main__":
    main()

