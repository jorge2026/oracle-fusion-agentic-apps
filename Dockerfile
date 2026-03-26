# syntax=docker/dockerfile:1

FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias de sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY agents/ agents/
COPY connectors/ connectors/
COPY apps/ apps/
COPY workflows/ workflows/

# Variables de entorno por defecto
ENV WORKFLOWS_DIR=workflows
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["uvicorn", "apps.orchestrator.main:app", "--host", "0.0.0.0", "--port", "8000"]
