"""Tests para los conectores Oracle Fusion."""

from __future__ import annotations

from connectors.oracle_fusion.mock_client import MockFusionClient


class TestMockFusionClient:
    def setup_method(self) -> None:
        self.client = MockFusionClient()
        self.client.connect()

    def teardown_method(self) -> None:
        self.client.disconnect()

    def test_connect_sets_connected(self) -> None:
        assert self.client._connected is True

    def test_disconnect_clears_connected(self) -> None:
        self.client.disconnect()
        assert self.client._connected is False

    def test_get_purchase_orders(self) -> None:
        result = self.client.get("purchaseOrders")
        assert "items" in result
        assert len(result["items"]) > 0

    def test_get_employees(self) -> None:
        result = self.client.get("employees")
        assert "items" in result
        assert len(result["items"]) > 0

    def test_get_unknown_resource_returns_empty(self) -> None:
        result = self.client.get("unknownResource")
        assert result == {"items": []}

    def test_post_returns_status_created(self) -> None:
        result = self.client.post("invoices", {"amount": 100.0})
        assert result["status"] == "created"
        assert result["resource"] == "invoices"
