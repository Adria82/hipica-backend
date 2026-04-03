# Imagen base de Python ligera
FROM python:3.10-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiamos el fichero de dependencias
# Esto permite aprovechar la cache de Docker si no cambian
COPY requirements.txt .

# Instalamos las dependencias del proyecto
# --no-cache-dir reduce el tamaño final de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código de la aplicación
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

# Comando de arranque del contenedor
# - uvicorn: servidor ASGI
# - app.main:app -> módulo y objeto FastAPI
# - --host 0.0.0.0 permite acceso desde fuera del contenedor
# - --reload habilita recarga automática (ideal en desarrollo)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]