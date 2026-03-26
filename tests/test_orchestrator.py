"""Tests para el orquestador FastAPI."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from apps.orchestrator.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestRunAppEndpoint:
    def test_run_procure_to_pay(self, client: TestClient) -> None:
        response = client.post("/apps/procure_to_pay/run", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["app_id"] == "procure_to_pay"
        assert data["status"] in ("completed", "policy_violation")
        assert "steps" in data

    def test_run_hire_to_retire(self, client: TestClient) -> None:
        response = client.post("/apps/hire_to_retire/run", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["app_id"] == "hire_to_retire"
        assert data["status"] in ("completed", "policy_violation")

    def test_run_unknown_app_returns_404(self, client: TestClient) -> None:
        response = client.post("/apps/nonexistent_app/run", json={})
        assert response.status_code == 404

    def test_run_with_params(self, client: TestClient) -> None:
        response = client.post(
            "/apps/procure_to_pay/run",
            json={"params": {"custom_key": "custom_value"}},
        )
        assert response.status_code == 200
