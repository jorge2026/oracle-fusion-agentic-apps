"""Tests para los agentes."""

from __future__ import annotations

import pytest

from agents.action_agent import ActionAgent
from agents.data_agent import DataAgent
from agents.policy_agent import PolicyAgent
from connectors.oracle_fusion.mock_client import MockFusionClient


@pytest.fixture
def client() -> MockFusionClient:
    c = MockFusionClient()
    c.connect()
    yield c
    c.disconnect()


class TestDataAgent:
    def test_fetch_returns_data_key(self, client: MockFusionClient) -> None:
        agent = DataAgent(client)
        result = agent.fetch("purchaseOrders")
        assert "data" in result
        assert "count" in result
        assert result["count"] > 0

    def test_fetch_sets_resource(self, client: MockFusionClient) -> None:
        agent = DataAgent(client)
        result = agent.fetch("employees")
        assert result["resource"] == "employees"


class TestPolicyAgent:
    def test_passes_when_no_violations(self) -> None:
        agent = PolicyAgent()
        context = {
            "resource": "purchaseOrders",
            "data": [{"OrderId": "PO-001", "Amount": 100.0, "Status": "Approved"}],
        }
        result = agent.validate(context)
        assert result["passed"] is True
        assert result["violations"] == []

    def test_fails_when_amount_exceeds_max(self) -> None:
        agent = PolicyAgent()
        context = {
            "resource": "purchaseOrders",
            "data": [{"OrderId": "PO-999", "Amount": 99999.0, "Status": "Approved"}],
        }
        result = agent.validate(context)
        assert result["passed"] is False
        assert len(result["violations"]) > 0

    def test_fails_when_status_not_allowed(self) -> None:
        agent = PolicyAgent()
        context = {
            "resource": "purchaseOrders",
            "data": [{"OrderId": "PO-100", "Amount": 50.0, "Status": "Rejected"}],
        }
        result = agent.validate(context)
        assert result["passed"] is False

    def test_empty_data_passes(self) -> None:
        agent = PolicyAgent()
        result = agent.validate({"resource": "anything", "data": []})
        assert result["passed"] is True

    def test_custom_policies(self) -> None:
        agent = PolicyAgent(policies={"max_po_amount": 10.0, "allowed_po_statuses": ["Approved"]})
        context = {
            "resource": "purchaseOrders",
            "data": [{"OrderId": "PO-X", "Amount": 20.0, "Status": "Approved"}],
        }
        result = agent.validate(context)
        assert result["passed"] is False


class TestActionAgent:
    def test_execute_returns_result_key(self, client: MockFusionClient) -> None:
        agent = ActionAgent(client)
        result = agent.execute("invoices", {"amount": 500.0})
        assert "result" in result
        assert result["action"] == "invoices"

    def test_execute_result_has_status(self, client: MockFusionClient) -> None:
        agent = ActionAgent(client)
        result = agent.execute("invoices", {"amount": 500.0})
        assert result["result"]["status"] == "created"
