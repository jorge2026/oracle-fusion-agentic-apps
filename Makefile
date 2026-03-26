.PHONY: run test lint format install install-dev help

PYTHON ?= python
PIP    ?= pip

help:  ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instala las dependencias de producción
	$(PIP) install -r requirements.txt

install-dev:  ## Instala las dependencias de desarrollo (incluye producción)
	$(PIP) install -r requirements.txt -r requirements-dev.txt

run:  ## Inicia la API con uvicorn (modo desarrollo)
	PYTHONPATH=. $(PYTHON) -m uvicorn apps.orchestrator.main:app --reload --host 0.0.0.0 --port 8000

test:  ## Ejecuta los tests con pytest
	PYTHONPATH=. $(PYTHON) -m pytest tests/ -v

lint:  ## Ejecuta el linter ruff
	$(PYTHON) -m ruff check .

format:  ## Formatea el código con ruff
	$(PYTHON) -m ruff format .

docker-build:  ## Construye la imagen Docker
	docker build -t oracle-fusion-agentic-apps .

docker-up:  ## Levanta los servicios con docker compose
	docker compose up --build

docker-down:  ## Detiene los servicios de docker compose
	docker compose down
