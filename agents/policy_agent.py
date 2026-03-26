"""
PolicyAgent – agente responsable de evaluar políticas de negocio sobre los datos.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Políticas predefinidas
# ---------------------------------------------------------------------------

_POLICIES: dict[str, Any] = {
    "max_po_amount": 5000.00,          # Importe máximo de una orden de compra sin aprobación adicional
    "allowed_po_statuses": ["Approved", "Pending"],
    "allowed_employee_statuses": ["Active"],
}


class PolicyAgent:
    """
    Agente de políticas: valida datos contra reglas de negocio configurables.
    """

    def __init__(self, policies: dict[str, Any] | None = None) -> None:
        self._policies: dict[str, Any] = policies or _POLICIES

    # ------------------------------------------------------------------
    # Operaciones públicas
    # ------------------------------------------------------------------

    def validate(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Valida el contexto dado contra las políticas configuradas.

        Args:
            context: Diccionario con los datos a validar.
                     Claves esperadas: ``resource`` y ``data``.

        Returns:
            Diccionario con ``passed`` (bool), ``violations`` (list) y ``context`` original.
        """
        resource: str = context.get("resource", "")
        data: list[Any] = context.get("data", [])
        violations: list[str] = []

        logger.info("PolicyAgent: validando %d registros del recurso '%s'", len(data), resource)

        for item in data:
            # Regla: importe máximo para órdenes de compra
            if "Amount" in item:
                amount = float(item["Amount"])
                max_amount: float = self._policies.get("max_po_amount", float("inf"))
                if amount > max_amount:
                    msg = (
                        f"El importe {amount} supera el máximo permitido "
                        f"{max_amount} en el registro {item.get('OrderId', item)}"
                    )
                    violations.append(msg)
                    logger.warning("PolicyAgent: %s", msg)

            # Regla: estado de órdenes de compra
            if "Status" in item and "OrderId" in item:
                allowed: list[str] = self._policies.get("allowed_po_statuses", [])
                if allowed and item["Status"] not in allowed:
                    msg = f"Estado '{item['Status']}' no permitido para la orden {item.get('OrderId')}"
                    violations.append(msg)
                    logger.warning("PolicyAgent: %s", msg)

        passed = len(violations) == 0
        logger.info("PolicyAgent: validación completada – passed=%s violations=%d", passed, len(violations))
        return {"passed": passed, "violations": violations, "context": context}
