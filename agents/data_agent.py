"""
DataAgent – agente responsable de recuperar y normalizar datos de Oracle Fusion.
"""

from __future__ import annotations

import logging
from typing import Any

from connectors.oracle_fusion.client import FusionClient

logger = logging.getLogger(__name__)


class DataAgent:
    """
    Agente de datos: obtiene información de Oracle Fusion y la devuelve
    en un formato normalizado para el orquestador.
    """

    def __init__(self, client: FusionClient) -> None:
        self._client = client

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------

    def fetch(self, resource: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Recupera un recurso de Oracle Fusion.

        Args:
            resource: Identificador del recurso (p. ej. "purchaseOrders").
            params:   Parámetros de filtrado opcionales.

        Returns:
            Diccionario con la clave ``data`` conteniendo la lista de items.
        """
        logger.info("DataAgent: recuperando recurso '%s'", resource)
        try:
            raw = self._client.get(resource, params)
            items: list[Any] = raw.get("items", [])
            logger.info("DataAgent: %d registros obtenidos de '%s'", len(items), resource)
            return {"data": items, "count": len(items), "resource": resource}
        except Exception as exc:
            logger.error("DataAgent: error al recuperar '%s': %s", resource, exc)
            raise
