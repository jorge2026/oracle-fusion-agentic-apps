# Oracle Fusion Agentic Apps

> **De agentes sueltos a aplicaciones agénticas** — Starter en Python para orquestar agentes sobre Oracle Fusion (ERP/HCM) con FastAPI, Docker y GitHub Actions CI.

---

## Estructura del proyecto

```
oracle-fusion-agentic-apps/
├── agents/                  # Agentes reutilizables
│   ├── data_agent.py        # Recupera datos de Oracle Fusion
│   ├── policy_agent.py      # Valida políticas de negocio
│   └── action_agent.py      # Ejecuta acciones en Oracle Fusion
├── apps/
│   └── orchestrator/
│       └── main.py          # API FastAPI (GET /health, POST /apps/{app_id}/run)
├── connectors/
│   └── oracle_fusion/
│       ├── client.py        # Interfaz abstracta FusionClient
│       ├── mock_client.py   # Implementación mock (sin credenciales)
│       └── rest_client.py   # Placeholder REST (requiere credenciales)
├── workflows/
│   ├── procure_to_pay.yaml  # Flujo Procure-to-Pay
│   └── hire_to_retire.yaml  # Flujo Hire-to-Retire
├── docs/
│   └── guia_apps_agénticas.md  # Guía ES: de agentes sueltos a apps agénticas
├── tests/                   # Tests con pytest
├── .env.example             # Variables de entorno (sin credenciales)
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── pyproject.toml
├── requirements.txt
└── requirements-dev.txt
```

---

## Requisitos

- Python ≥ 3.11
- Docker + Docker Compose (opcional, para correr con contenedor)

---

## Instalación y uso local

```bash
# 1. Clonar el repositorio
git clone https://github.com/jorge2026/oracle-fusion-agentic-apps.git
cd oracle-fusion-agentic-apps

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt

# 3. Configurar variables de entorno (editar si necesitas credenciales reales)
cp .env.example .env

# 4. Iniciar la API
make run
# ó directamente:
# PYTHONPATH=. uvicorn apps.orchestrator.main:app --reload
```

La API quedará disponible en **http://localhost:8000**.

### Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET`  | `/health` | Estado de la API |
| `POST` | `/apps/{app_id}/run` | Ejecuta un workflow agéntico |
| `GET`  | `/docs` | Documentación interactiva (Swagger UI) |

### Ejemplo de uso

```bash
# Comprobar estado
curl http://localhost:8000/health

# Ejecutar el flujo Procure-to-Pay
curl -X POST http://localhost:8000/apps/procure_to_pay/run \
     -H "Content-Type: application/json" \
     -d '{}'

# Ejecutar el flujo Hire-to-Retire
curl -X POST http://localhost:8000/apps/hire_to_retire/run \
     -H "Content-Type: application/json" \
     -d '{}'
```

---

## Correr con Docker

```bash
# Construir y levantar
docker compose up --build
# ó con el Makefile:
make docker-up
```

La API estará disponible en **http://localhost:8000**.

---

## Tests

```bash
make test
# ó directamente:
PYTHONPATH=. pytest tests/ -v
```

---

## Lint

```bash
make lint
# ó directamente:
python -m ruff check .
```

---

## Conectar con Oracle Fusion real

1. Edita `.env` y rellena `FUSION_BASE_URL`, `FUSION_USERNAME` y `FUSION_PASSWORD`.
2. En `apps/orchestrator/main.py`, reemplaza `MockFusionClient` por `RestFusionClient`.
3. Reinicia la API.

> **Nunca** almacenes credenciales en el código fuente ni en el repositorio.

---

## Documentación adicional

Consulta [`docs/guia_apps_agénticas.md`](docs/guia_apps_agénticas.md) para una guía completa
en español sobre la arquitectura y cómo extender el proyecto.

---

## CI/CD

GitHub Actions ejecuta automáticamente lint + tests en cada push/PR
(ver [`.github/workflows/ci.yml`](.github/workflows/ci.yml)).
