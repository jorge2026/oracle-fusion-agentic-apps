"""
Orquestador de aplicaciones agénticas – FastAPI.

Endpoints:
    GET  /health              – comprobación de estado
    POST /apps/{app_id}/run  – ejecuta una app agéntica definida en YAML/JSON
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

import yaml
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.action_agent import ActionAgent
from agents.data_agent import DataAgent
from agents.policy_agent import PolicyAgent
from connectors.oracle_fusion.mock_client import MockFusionClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Oracle Fusion Agentic Apps – Orchestrator",
    description="API de orquestación para aplicaciones agénticas sobre Oracle Fusion.",
    version="0.1.0",
)

# Directorio donde residen las definiciones de workflows
WORKFLOWS_DIR = Path(os.environ.get("WORKFLOWS_DIR", "workflows"))


# ---------------------------------------------------------------------------
# Modelos de request/response
# ---------------------------------------------------------------------------


class RunRequest(BaseModel):
    """Parámetros opcionales para la ejecución de una app agéntica."""

    params: dict[str, Any] = {}


class RunResponse(BaseModel):
    """Resultado de la ejecución de una app agéntica."""

    app_id: str
    status: str
    steps: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/health", tags=["infra"])
def health() -> dict[str, str]:
    """Devuelve el estado de la API."""
    return {"status": "ok"}


@app.post("/apps/{app_id}/run", response_model=RunResponse, tags=["apps"])
def run_app(app_id: str, request: RunRequest) -> RunResponse:
    """
    Ejecuta la app agéntica identificada por ``app_id``.

    La definición de la app se busca en ``WORKFLOWS_DIR/<app_id>.yaml`` o
    ``WORKFLOWS_DIR/<app_id>.json``.  El orquestador ejecuta los pasos
    definidos en el workflow usando los agentes disponibles.
    """
    logger.info("Ejecutando app '%s' con params=%s", app_id, request.params)

    workflow = _load_workflow(app_id)

    # Instanciar conector y agentes
    client = MockFusionClient()
    client.connect()
    data_agent = DataAgent(client)
    policy_agent = PolicyAgent()
    action_agent = ActionAgent(client)

    steps_results: list[dict[str, Any]] = []
    context: dict[str, Any] = dict(request.params)

    try:
        for step in workflow.get("steps", []):
            step_name: str = step.get("name", "unnamed")
            agent_type: str = step.get("agent", "")
            step_params: dict[str, Any] = step.get("params", {})

            logger.info("  Paso '%s' (agente: %s)", step_name, agent_type)

            result: dict[str, Any] = {}

            if agent_type == "data_agent":
                resource = step_params.get("resource", "")
                result = data_agent.fetch(resource, step_params.get("query_params"))
                context.update(result)

            elif agent_type == "policy_agent":
                result = policy_agent.validate(context)
                if not result["passed"]:
                    steps_results.append({"step": step_name, "agent": agent_type, "result": result})
                    return RunResponse(
                        app_id=app_id,
                        status="policy_violation",
                        steps=steps_results,
                        summary={"violations": result["violations"]},
                    )

            elif agent_type == "action_agent":
                action = step_params.get("action", "")
                payload = {**context, **step_params.get("payload", {})}
                result = action_agent.execute(action, payload)

            else:
                logger.warning("  Tipo de agente desconocido: '%s'", agent_type)
                result = {"warning": f"Agente '{agent_type}' no reconocido"}

            steps_results.append({"step": step_name, "agent": agent_type, "result": result})

    finally:
        client.disconnect()

    return RunResponse(
        app_id=app_id,
        status="completed",
        steps=steps_results,
        summary={"steps_executed": len(steps_results)},
    )


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------


def _load_workflow(app_id: str) -> dict[str, Any]:
    """Carga la definición del workflow desde YAML o JSON."""
    for suffix in (".yaml", ".yml", ".json"):
        path = WORKFLOWS_DIR / f"{app_id}{suffix}"
        if path.exists():
            logger.info("Cargando workflow desde '%s'", path)
            with path.open(encoding="utf-8") as fh:
                return yaml.safe_load(fh)  # type: ignore[no-any-return]

    raise HTTPException(
        status_code=404,
        detail=f"No se encontró la definición del workflow '{app_id}' en '{WORKFLOWS_DIR}'.",
    )
