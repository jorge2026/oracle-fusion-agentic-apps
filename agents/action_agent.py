"""
ActionAgent – agente responsable de ejecutar acciones en Oracle Fusion.
"""

from __future__ import annotations

import logging
from typing import Any

from connectors.oracle_fusion.client import FusionClient

logger = logging.getLogger(__name__)


class ActionAgent:
    """
    Agente de acciones: ejecuta operaciones de escritura en Oracle Fusion
    solo si las políticas han sido aprobadas.
    """

    def __init__(self, client: FusionClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------

    def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Ejecuta una acción en Oracle Fusion.

        Args:
            action:  Identificador de la acción / recurso destino
                     (p. ej. "invoices", "purchaseOrders/approve").
            payload: Datos de la acción.

        Returns:
            Respuesta del conector con clave ``result``.
        """
        logger.info("ActionAgent: ejecutando acción '%s'", action)
        try:
            response = self._client.post(action, payload)
            logger.info("ActionAgent: acción '%s' completada – status=%s", action, response.get("status"))
            return {"result": response, "action": action}
        except Exception as exc:
            logger.error("ActionAgent: error ejecutando acción '%s': %s", action, exc)
            raise
