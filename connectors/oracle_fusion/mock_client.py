"""
MockFusionClient – implementación simulada de FusionClient para tests y desarrollo local.

No realiza peticiones de red reales ni requiere credenciales.
"""

from __future__ import annotations

import logging
from typing import Any

from connectors.oracle_fusion.client import FusionClient

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Datos de ejemplo que el mock devuelve
# ---------------------------------------------------------------------------

_MOCK_DATA: dict[str, Any] = {
    "purchaseOrders": {
        "items": [
            {"OrderId": "PO-001", "Supplier": "Acme Corp", "Amount": 1500.00, "Status": "Approved"},
            {"OrderId": "PO-002", "Supplier": "Globex", "Amount": 3200.00, "Status": "Pending"},
        ]
    },
    "employees": {
        "items": [
            {"EmployeeId": "EMP-101", "Name": "Ana García", "Department": "Finance", "Status": "Active"},
            {"EmployeeId": "EMP-102", "Name": "Carlos López", "Department": "HR", "Status": "Active"},
        ]
    },
    "invoices": {
        "items": [
            {"InvoiceId": "INV-501", "Supplier": "Acme Corp", "Amount": 1500.00, "Status": "Matched"},
        ]
    },
}


class MockFusionClient(FusionClient):
    """Implementación simulada de FusionClient para entornos sin credenciales reales."""

    def __init__(self) -> None:
        self._connected: bool = False

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        self._connected = True
        logger.info("MockFusionClient: conexión simulada establecida.")

    def disconnect(self) -> None:
        self._connected = False
        logger.info("MockFusionClient: conexión simulada cerrada.")

    # ------------------------------------------------------------------
    # Operaciones genéricas
    # ------------------------------------------------------------------

    def get(self, resource: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        logger.debug("MockFusionClient.get resource=%s params=%s", resource, params)
        # Devuelve datos mock si el recurso coincide; en caso contrario, vacío.
        for key, value in _MOCK_DATA.items():
            if key in resource:
                return value
        return {"items": []}

    def post(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        logger.debug("MockFusionClient.post resource=%s payload=%s", resource, payload)
        return {"status": "created", "resource": resource, "payload": payload}
