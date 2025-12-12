# ================================
# FitFlow - Dockerfile
# Sistema de Gestión para Gimnasios
# ================================

# Imagen base Python slim para menor tamaño
FROM python:3.10-slim

# Establecer variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    HOST=0.0.0.0

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero para aprovechar cache de Docker
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorio para logs
RUN mkdir -p logs

# Crear directorio para base de datos
RUN mkdir -p src/instance

# Exponer puerto
EXPOSE 5000

# Comando por defecto: inicializar DB y correr con Gunicorn
CMD ["sh", "-c", "python -m src.main init-db && gunicorn --worker-class gevent -w 1 -b 0.0.0.0:${PORT} 'src.main:create_app()'"]
