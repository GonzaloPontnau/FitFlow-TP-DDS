@echo off
REM Script de instalación y setup para FitFlow (Windows)

echo =========================================
echo   FitFlow - Setup Inicial
echo =========================================

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado
    exit /b 1
)

echo OK: Python encontrado

REM Crear entorno virtual
echo.
echo Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
echo Activando entorno virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo.
echo Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Copiar archivo .env
if not exist .env (
    echo.
    echo Creando archivo .env...
    copy .env.example .env
    echo OK: Archivo .env creado
)

REM Inicializar base de datos
echo.
echo Inicializando base de datos...
python -m src.main init-db

echo.
echo =========================================
echo   OK: Setup completado exitosamente
echo =========================================
echo.
echo Para iniciar la aplicacion:
echo   1. Activa el entorno virtual:
echo      venv\Scripts\activate
echo   2. Ejecuta: python -m src.main
echo.
pause
