# FitFlow - Sistema de Gestión para Gimnasios

Sistema de gestión integral de operaciones para gimnasios y centros de fitness.

**Trabajo Práctico Anual Integrador - Diseño de Sistemas 2025**  
Universidad Tecnológica Nacional (UTN)

---

## 🚀 Instalación

### Requisitos
- Python 3.10+
- pip

### Setup

```bash
# Clonar repositorio
git clone https://github.com/GonzaloPontnau/FitFlow-TP-DDS.git
cd FitFlow-TP-DDS

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Crear archivo .env (opcional para desarrollo)
# Para desarrollo, el sistema usa valores por defecto
```

### Ejecutar Aplicación

```bash
python -m src.main
```

Disponible en: `http://localhost:5000`

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
python -m pytest

# Con detalles
python -m pytest -v

# Con cobertura
python -m pytest --cov=src

# Cobertura detallada
python -m pytest --cov=src --cov-report=term-missing

# Generar reporte HTML
python -m pytest --cov=src --cov-report=html
```

## 📋 Funcionalidades

### Entrega 1 ✅
- Carga masiva de socios desde CSV
- CRUD de Planes de Membresía
- Gestión y filtrado de Clases
- Sistema de Solicitudes de Baja
- Roles: Administrador, Socio Registrado, Visualizador

### Entrega 2 ✅
- Gestión de Reservas a clases
- Integración con Pasarela de Pagos (simulada)
- Integración con API de Clases Externas (simulada)
- Validación automática de solicitudes

### Próximas Entregas
Ver [ENTREGAS.md](ENTREGAS.md) para detalles completos.

---

## 🏗️ Arquitectura

```
src/
├── api/                    # Controladores REST
├── models/                 # Modelos del dominio
├── repositories/           # Acceso a datos
├── services/               # Lógica de negocio
├── datasources/proxy/      # Integraciones externas
├── validators/             # Validaciones de negocio
├── config/                 # Configuración
└── main.py                 # Punto de entrada
```

---

## 🛠️ Stack Tecnológico

- **Backend:** Python 3.10+, Flask 3.0.0
- **ORM:** SQLAlchemy
- **Base de Datos:** SQLite (dev)
- **Testing:** Pytest
- **Procesamiento:** Pandas

---

## 📝 Variables de Entorno

Para desarrollo, el sistema funciona con valores por defecto. Para producción, crear archivo `.env`:

```bash
# Base de Datos
DATABASE_URL=sqlite:///src/instance/fitflow.db

# Aplicación
DEBUG=true
SECRET_KEY=tu-clave-secreta

# Servicios Externos (simulados por defecto)
PASARELA_PAGOS_API_KEY=test_api_key
CLASES_EXTERNAS_API_KEY=test_key
``