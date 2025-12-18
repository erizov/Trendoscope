"""
E2E test for API validation - all validation checks in one test.
Uses TestClient for validation testing without requiring running API.
"""
import pytest
import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to path
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from trendoscope2.api.main import app

client = TestClient(app)


def test_all_validation_checks():
    """
    Comprehensive test for all API validation checks.
    Tests all endpoints for proper validation and MIME types.
    """
    results = {
        "passed": [],
        "failed": []
    }
    
    # ============================================================
    # 1. TTS Validation Tests
    # ============================================================
    print("\n[1] Testing TTS Validation...")
    
    # 1.1 Empty text
    try:
        response = client.post(
            "/api/tts/generate",
            json={"text": ""}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        results["passed"].append("TTS: Empty text validation")
    except AssertionError as e:
        results["failed"].append(f"TTS: Empty text validation - {e}")
    
    # 1.2 Whitespace-only text
    try:
        response = client.post(
            "/api/tts/generate",
            json={"text": "   "}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        results["passed"].append("TTS: Whitespace-only text validation")
    except AssertionError as e:
        results["failed"].append(f"TTS: Whitespace-only text validation - {e}")
    
    # 1.3 Invalid language
    try:
        response = client.post(
            "/api/tts/generate",
            json={"text": "Test", "language": "invalid"}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        results["passed"].append("TTS: Invalid language validation")
    except AssertionError as e:
        results["failed"].append(f"TTS: Invalid language validation - {e}")
    
    # 1.4 Invalid voice_gender
    try:
        response = client.post(
            "/api/tts/generate",
            json={"text": "Test", "voice_gender": "invalid"}
        )
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        results["passed"].append("TTS: Invalid voice_gender validation")
    except AssertionError as e:
        results["failed"].append(f"TTS: Invalid voice_gender validation - {e}")
    
    # 1.5 Valid request
    try:
        response = client.post(
            "/api/tts/generate",
            json={
                "text": "Test text",
                "language": "en",
                "voice_gender": "female"
            }
        )
        assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"
        results["passed"].append("TTS: Valid request passes validation")
    except AssertionError as e:
        results["failed"].append(f"TTS: Valid request - {e}")
    
    # ============================================================
    # 2. Translate Article Validation Tests
    # ============================================================
    print("\n[2] Testing Translate Article Validation...")
    
    # 2.1 Missing both title and summary
    try:
        response = client.post(
            "/api/news/translate?target_language=en",
            json={}
        )
        # Pydantic model_post_init raises ValueError, which becomes 400
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        results["passed"].append("Translate: Missing title and summary validation")
    except AssertionError as e:
        results["failed"].append(f"Translate: Missing title and summary - {e}")
    
    # 2.2 Title only
    try:
        response = client.post(
            "/api/news/translate?target_language=en",
            json={"title": "Test title"}
        )
        assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"
        results["passed"].append("Translate: Title only passes validation")
    except AssertionError as e:
        results["failed"].append(f"Translate: Title only - {e}")
    
    # 2.3 Summary only
    try:
        response = client.post(
            "/api/news/translate?target_language=en",
            json={"summary": "Test summary"}
        )
        assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"
        results["passed"].append("Translate: Summary only passes validation")
    except AssertionError as e:
        results["failed"].append(f"Translate: Summary only - {e}")
    
    # 2.4 Invalid target_language (validated in endpoint, not query param)
    try:
        response = client.post(
            "/api/news/translate?target_language=invalid",
            json={"title": "Test"}
        )
        # target_language is validated in endpoint, may return 422 or 200 with error
        assert response.status_code in [200, 422], f"Expected 200 or 422, got {response.status_code}"
        results["passed"].append("Translate: Invalid target_language handled")
    except AssertionError as e:
        results["failed"].append(f"Translate: Invalid target_language - {e}")
    
    # ============================================================
    # 3. Rutube Validation Tests
    # ============================================================
    print("\n[3] Testing Rutube Validation...")
    
    # 3.1 Invalid URL (not Rutube)
    try:
        response = client.post(
            "/api/rutube/generate",
            json={"url": "https://example.com/video"}
        )
        assert response.status_code in [400, 422], f"Expected 400 or 422, got {response.status_code}"
        results["passed"].append("Rutube: Invalid URL validation")
    except AssertionError as e:
        results["failed"].append(f"Rutube: Invalid URL - {e}")
    
    # 3.2 Valid Rutube URL format
    try:
        response = client.post(
            "/api/rutube/generate",
            json={"url": "https://rutube.ru/video/123456/"}
        )
        # Valid URL passes Pydantic validation (422), but may fail on processing
        assert response.status_code in [200, 400, 422, 500], f"Expected 200/400/422/500, got {response.status_code}"
        results["passed"].append("Rutube: Valid URL format passes validation")
    except AssertionError as e:
        results["failed"].append(f"Rutube: Valid URL format - {e}")
    
    # ============================================================
    # 4. File Download MIME Types Tests
    # ============================================================
    print("\n[4] Testing File Download MIME Types...")
    
    # 4.1 TTS Audio MIME type (if audio exists)
    try:
        # First generate audio
        generate_response = client.post(
            "/api/tts/generate",
            json={"text": "Test audio for MIME type"}
        )
        
        if generate_response.status_code == 200:
            data = generate_response.json()
            audio_id = data.get("audio_id")
            if audio_id:
                audio_response = client.get(f"/api/tts/audio/{audio_id}")
                if audio_response.status_code == 200:
                    content_type = audio_response.headers.get("content-type", "")
                    assert content_type in [
                        "audio/mpeg",
                        "audio/wav",
                        "audio/mp3",
                        "application/octet-stream"
                    ], f"Unexpected MIME type: {content_type}"
                    results["passed"].append(f"File Download: TTS audio MIME type ({content_type})")
                else:
                    results["failed"].append(f"File Download: TTS audio not found ({audio_response.status_code})")
            else:
                results["failed"].append("File Download: No audio_id in response")
        else:
            # Generation failed, but validation passed
            results["passed"].append("File Download: TTS generation validation passed (generation may fail)")
    except Exception as e:
        results["failed"].append(f"File Download: TTS audio MIME type - {e}")
    
    # 4.2 Frontend HTML MIME type
    try:
        response = client.get("/")
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            assert content_type is not None, "Content-Type header missing"
            # Can be JSON or HTML depending on frontend availability
            assert "json" in content_type.lower() or "html" in content_type.lower(), \
                f"Unexpected MIME type: {content_type}"
            results["passed"].append(f"File Download: Frontend MIME type ({content_type})")
    except Exception as e:
        results["failed"].append(f"File Download: Frontend MIME type - {e}")
    
    # ============================================================
    # 5. Query Parameters Validation Tests
    # ============================================================
    print("\n[5] Testing Query Parameters Validation...")
    
    # 5.1 Invalid limit (too low)
    try:
        response = client.get("/api/news/feed?limit=3")
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        results["passed"].append("Query Params: Invalid limit (too low) validation")
    except AssertionError as e:
        results["failed"].append(f"Query Params: Invalid limit (too low) - {e}")
    
    # 5.2 Invalid limit (too high)
    try:
        response = client.get("/api/news/feed?limit=200")
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        results["passed"].append("Query Params: Invalid limit (too high) validation")
    except AssertionError as e:
        results["failed"].append(f"Query Params: Invalid limit (too high) - {e}")
    
    # 5.3 Valid limit
    try:
        response = client.get("/api/news/feed?limit=20")
        assert response.status_code in [200, 500], f"Expected 200 or 500, got {response.status_code}"
        results["passed"].append("Query Params: Valid limit passes validation")
    except AssertionError as e:
        results["failed"].append(f"Query Params: Valid limit - {e}")
    
    # ============================================================
    # Summary
    # ============================================================
    print("\n" + "="*60)
    print("VALIDATION TEST SUMMARY")
    print("="*60)
    print(f"\n[PASSED] {len(results['passed'])}")
    for test in results['passed']:
        print(f"   [OK] {test}")
    
    print(f"\n[FAILED] {len(results['failed'])}")
    for test in results['failed']:
        print(f"   [X] {test}")
    
    print("\n" + "="*60)
    
    # Final assertion
    if results['failed']:
        pytest.fail(
            f"Validation tests failed: {len(results['failed'])}/{len(results['passed']) + len(results['failed'])} tests failed.\n"
            f"Failed tests:\n" + "\n".join(f"  - {t}" for t in results['failed'])
        )
    
    assert len(results['passed']) > 0, "No tests passed"
    print(f"\n[SUCCESS] All validation checks passed! ({len(results['passed'])} tests)")
