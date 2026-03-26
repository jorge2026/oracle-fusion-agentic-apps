"""
FusionClient – interfaz base para conectores Oracle Fusion.

Todos los métodos son abstractos; las implementaciones concretas deben
sobreescribirlos.  No contiene credenciales reales.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class FusionClient(ABC):
    """Interfaz abstracta para el conector Oracle Fusion."""

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    @abstractmethod
    def connect(self) -> None:
        """Establece la conexión con el endpoint de Fusion."""

    @abstractmethod
    def disconnect(self) -> None:
        """Cierra la conexión con el endpoint de Fusion."""

    # ------------------------------------------------------------------
    # Operaciones genéricas
    # ------------------------------------------------------------------

    @abstractmethod
    def get(self, resource: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Recupera un recurso de la API REST de Oracle Fusion.

        Args:
            resource: Ruta relativa del recurso (p. ej. "fscmRestApi/resources/11.13.18.05/purchaseOrders").
            params:   Parámetros de consulta opcionales.

        Returns:
            Diccionario con la respuesta del servidor.
        """

    @abstractmethod
    def post(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Crea o ejecuta una acción sobre un recurso de Oracle Fusion.

        Args:
            resource: Ruta relativa del recurso.
            payload:  Cuerpo de la petición.

        Returns:
            Diccionario con la respuesta del servidor.
        """
