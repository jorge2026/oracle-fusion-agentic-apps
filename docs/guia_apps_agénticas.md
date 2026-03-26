# De Agentes Sueltos a Aplicaciones Agénticas con Oracle Fusion

## Introducción

Esta guía explica cómo evolucionar desde **agentes aislados** —scripts o microservicios independientes que realizan una tarea concreta— hasta **aplicaciones agénticas completas** que orquestan múltiples agentes para cubrir procesos de negocio de extremo a extremo sobre Oracle Fusion.

---

## 1. ¿Qué es un agente suelto?

Un **agente suelto** es una unidad de código autónoma que:

- Se conecta a una fuente de datos (p. ej. Oracle Fusion REST API).
- Ejecuta una tarea concreta (leer órdenes, crear facturas, validar políticas).
- Devuelve un resultado sin coordinarse con otros agentes.

**Ejemplo:** `DataAgent` recupera órdenes de compra y las devuelve normalizadas.

```python
agent = DataAgent(client=MockFusionClient())
result = agent.fetch("purchaseOrders")
```

---

## 2. Limitaciones de los agentes sueltos

| Problema | Descripción |
|---|---|
| **Falta de contexto compartido** | Cada agente trabaja con su propio estado; no hay memoria compartida. |
| **Coordinación manual** | Quien llama a los agentes debe conocer el orden correcto y manejar errores. |
| **Sin guardarraíles** | No hay capa de políticas que detenga acciones indebidas. |
| **Difícil de auditar** | No queda registro centralizado del flujo completo. |

---

## 3. Arquitectura de una Aplicación Agéntica

Una **aplicación agéntica** añade:

1. **Orquestador** – coordina la secuencia de agentes y gestiona el contexto compartido.
2. **Definición declarativa** – el flujo se describe en YAML/JSON (no en código imperativo).
3. **Capa de políticas** – `PolicyAgent` actúa como guardarraíl antes de ejecutar acciones.
4. **API** – el orquestador expone endpoints REST para que cualquier sistema lo invoque.

```
┌─────────────────────────────────────────────────────┐
│                   Orquestador (FastAPI)              │
│                                                     │
│  POST /apps/{app_id}/run                            │
│          │                                          │
│          ▼                                          │
│   ┌──────────────┐   contexto   ┌───────────────┐  │
│   │  DataAgent   │ ──────────► │  PolicyAgent  │  │
│   └──────────────┘              └───────┬───────┘  │
│                                         │ aprobado  │
│                                         ▼           │
│                                  ┌─────────────┐   │
│                                  │ ActionAgent │   │
│                                  └─────────────┘   │
└─────────────────────────────────────────────────────┘
```

---

## 4. Flujo Procure-to-Pay (ejemplo)

El workflow `procure_to_pay.yaml` implementa el ciclo completo:

```
Paso 1 – DataAgent     →  Recupera órdenes de compra aprobadas
Paso 2 – PolicyAgent   →  Valida importes y estados contra políticas
Paso 3 – ActionAgent   →  Crea la factura correspondiente en Fusion
```

Para ejecutarlo:

```bash
curl -X POST http://localhost:8000/apps/procure_to_pay/run \
     -H "Content-Type: application/json" \
     -d '{}'
```

---

## 5. Cómo añadir un nuevo workflow

1. Crea el archivo `workflows/mi_proceso.yaml`:

```yaml
id: mi_proceso
name: "Mi Proceso"
description: "Descripción del proceso"
steps:
  - name: fetch_data
    agent: data_agent
    params:
      resource: myResource
  - name: validate
    agent: policy_agent
    params: {}
  - name: act
    agent: action_agent
    params:
      action: myAction
      payload: {}
```

2. Llama al endpoint:

```bash
curl -X POST http://localhost:8000/apps/mi_proceso/run -d '{}'
```

---

## 6. Cómo añadir un nuevo agente

1. Crea `agents/my_agent.py` con la lógica del agente.
2. Regístralo en `agents/__init__.py`.
3. Instáncialo en `apps/orchestrator/main.py` (sección `run_app`).
4. Añade el tipo de agente al `elif` del orquestador.

---

## 7. Conectar con Oracle Fusion real

Cuando dispongas de credenciales:

1. Copia `.env.example` → `.env` y rellena las variables.
2. Sustituye `MockFusionClient` por `RestFusionClient` en `main.py`.
3. Prueba con el endpoint `/apps/{app_id}/run`.

---

## 8. Buenas prácticas

- **Nunca** almacenes credenciales en el código fuente.  Usa variables de entorno o un gestor de secretos.
- Añade **type hints** en todos los métodos nuevos.
- Usa **logging** en lugar de `print` para facilitar la observabilidad.
- Escribe **tests** para cada agente y para el orquestador.
- Documenta los nuevos workflows en esta guía.
