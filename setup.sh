#!/bin/bash
# Script de instalación y setup para FitFlow

echo "========================================="
echo "  FitFlow - Setup Inicial"
echo "========================================="

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado"
    exit 1
fi

echo "✓ Python encontrado: $(python3 --version)"

# Crear entorno virtual
echo ""
echo "Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "Activando entorno virtual..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Instalar dependencias
echo ""
echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

# Copiar archivo .env
if [ ! -f .env ]; then
    echo ""
    echo "Creando archivo .env..."
    cp .env.example .env
    echo "✓ Archivo .env creado"
fi

# Inicializar base de datos
echo ""
echo "Inicializando base de datos..."
python -m src.main init-db

echo ""
echo "========================================="
echo "  ✓ Setup completado exitosamente"
echo "========================================="
echo ""
echo "Para iniciar la aplicación:"
echo "  1. Activa el entorno virtual:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "     source venv/Scripts/activate"
else
    echo "     source venv/bin/activate"
fi
echo "  2. Ejecuta: python -m src.main"
echo ""
