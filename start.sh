#!/bin/sh
set -e

echo "Inicializando base de datos..."
python -m app.seed --if-empty

echo "Arrancando FastAPI..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "${PORT:-8000}"
