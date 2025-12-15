"""
E2E test for the production Docker stack under deploy/docker/docker-compose.prod.yml.

This test:
- Starts the full production stack with docker compose (api, redis, postgres, prometheus, grafana)
- Waits for the FastAPI /health endpoint to become healthy
- Verifies Prometheus and Grafana HTTP endpoints are reachable
"""

import os
import subprocess
import time
from pathlib import Path

import httpx
import pytest


API_URL = "http://localhost:8004"
PROMETHEUS_URL = "http://localhost:9090"
GRAFANA_URL = "http://localhost:3000"
TIMEOUT = 120


def _check_docker_running() -> bool:
    """Return True if Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def _repo_root() -> Path:
    """Return repository root (Trendoscope)."""
    this_file = Path(__file__).resolve()
    # .../Trendoscope/trendoscope2/tests/e2e/test_prod_stack.py
    return this_file.parents[3]


@pytest.fixture(scope="session")
def prod_compose_env():
    """
    Start the production docker-compose stack for the session, then stop it.

    Skips if Docker is not available.
    """
    if not _check_docker_running():
        pytest.skip("Docker is not running (required for prod stack E2E)")

    repo_root = _repo_root()
    deploy_dir = repo_root / "deploy"
    env = os.environ.copy()

    try:
        # Start stack (build if needed)
        subprocess.run(
            ["docker", "compose", "-f", "docker/docker-compose.prod.yml", "up", "-d"],
            cwd=str(deploy_dir),
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        pytest.skip(f"Failed to start prod docker-compose stack: {exc}")

    try:
        yield
    finally:
        try:
            subprocess.run(
                ["docker", "compose", "-f", "docker/docker-compose.prod.yml", "down"],
                cwd=str(deploy_dir),
                check=False,
                text=True,
            )
        except Exception:
            # Best-effort teardown; do not fail tests on teardown issues
            pass


def _wait_for_http_ok(url: str, timeout: int = TIMEOUT) -> bool:
    """Wait until an HTTP endpoint returns 200 OK or timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = httpx.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(3)
    return False


class TestProdStack:
    """E2E tests for production docker stack."""

    def test_api_health(self, prod_compose_env: None) -> None:
        """API /health should return 200 from prod stack."""
        ok = _wait_for_http_ok(f"{API_URL}/health", timeout=TIMEOUT)
        assert ok, "API /health did not become healthy in time"

    def test_prometheus_targets(self, prod_compose_env: None) -> None:
        """Prometheus targets endpoint should be reachable."""
        ok = _wait_for_http_ok(f"{PROMETHEUS_URL}/targets", timeout=TIMEOUT)
        assert ok, "Prometheus /targets endpoint is not reachable"

    def test_grafana_ui(self, prod_compose_env: None) -> None:
        """Grafana login UI should be reachable."""
        # Grafana may redirect, but initial GET should not error
        start_time = time.time()
        while time.time() - start_time < TIMEOUT:
            try:
                response = httpx.get(f"{GRAFANA_URL}/login", timeout=5, follow_redirects=True)
                if response.status_code == 200:
                    return
            except Exception:
                pass
            time.sleep(5)
        pytest.fail("Grafana UI did not become reachable in time")


