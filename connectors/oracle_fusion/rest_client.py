"""
RestFusionClient – placeholder de implementación REST real para Oracle Fusion.

⚠️  Este módulo NO contiene credenciales reales.
    Configure las variables de entorno indicadas en `.env.example` antes de usarlo.
"""

from __future__ import annotations

import logging
import os
from typing import Any

import httpx

from connectors.oracle_fusion.client import FusionClient

logger = logging.getLogger(__name__)


class RestFusionClient(FusionClient):
    """
    Implementación REST de FusionClient basada en httpx.

    Variables de entorno requeridas (ver .env.example):
        FUSION_BASE_URL  – URL base de la instancia Oracle Fusion (sin barra final).
        FUSION_USERNAME  – Usuario con acceso a la API REST.
        FUSION_PASSWORD  – Contraseña del usuario (almacenar en secreto, nunca en código).
    """

    def __init__(self) -> None:
        self._base_url: str = os.environ.get("FUSION_BASE_URL", "")
        self._username: str = os.environ.get("FUSION_USERNAME", "")
        self._password: str = os.environ.get("FUSION_PASSWORD", "")
        self._client: httpx.Client | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def connect(self) -> None:
        if not self._base_url:
            raise RuntimeError("La variable de entorno FUSION_BASE_URL no está definida.")
        self._client = httpx.Client(
            base_url=self._base_url,
            auth=(self._username, self._password),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30.0,
        )
        logger.info("RestFusionClient: cliente HTTP inicializado para %s", self._base_url)

    def disconnect(self) -> None:
        if self._client:
            self._client.close()
            self._client = None
            logger.info("RestFusionClient: cliente HTTP cerrado.")

    # ------------------------------------------------------------------
    # Operaciones genéricas
    # ------------------------------------------------------------------

    def get(self, resource: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("Llame a connect() antes de realizar peticiones.")
        response = self._client.get(resource, params=params or {})
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]

    def post(self, resource: str, payload: dict[str, Any]) -> dict[str, Any]:
        if self._client is None:
            raise RuntimeError("Llame a connect() antes de realizar peticiones.")
        response = self._client.post(resource, json=payload)
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]
