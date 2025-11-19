# FitFlow - Sistema de Gestión Integral para Gimnasios

Sistema open-source diseñado para la gestión integral de operaciones de gimnasios, desarrollado como Trabajo Práctico de Diseño de Sistemas de Software I (2025).

## 🎯 Funcionalidades Implementadas

### Entrega 1: Dominio Base
- ✅ Modelo de dominio completo (Socios, Clases, Planes, Entrenadores)
- ✅ Carga masiva de socios desde CSV
- ✅ Gestión de solicitudes de baja con validadores automáticos
- ✅ Sistema de roles (Socio Registrado, Visualizador, Administrador)

### Entrega 2: Integraciones
- ✅ Sistema de reservas con validación de cupos
- ✅ Proxy para Pasarela de Pagos
- ✅ Proxy para Clases Externas (talleres de terceros)
- ✅ Validación automática de solicitudes (Strategy Pattern)

### Entrega 3: Agregador y Funcionalidades Avanzadas
- ✅ Servicio Agregador de Horarios (consolidación interna + externa)
- ✅ Sistema de Listas de Espera con notificaciones y confirmación
- ✅ CRUD completo de Planes de Membresía
- ✅ Gestión de Solicitudes de Baja

### Entrega 4: Persistencia y Estadísticas
- ✅ Persistencia completa con SQLAlchemy
- ✅ Soporte multimedia (imágenes/videos en clases)
- ✅ Servicio de Estadísticas con Dashboard
- ✅ Exportación de asistencia a CSV

### Entrega 5: Web MVC
- ✅ Interfaz web completa (Flask + Templates)
- ✅ Vistas para socios (calendario, reservas)
- ✅ Panel administrativo

### Entrega 6: Despliegue y Seguridad
- ✅ WebSockets para actualizaciones en tiempo real (Flask-SocketIO)
- ✅ Rate Limiting (Flask-Limiter)
- ✅ Bloqueo de IPs configurable
- ✅ Sistema de logging y observabilidad

## 🚀 Instalación y Ejecución Local

### Requisitos Previos
- Python 3.8+
- pip
- Entorno virtual (venv)

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd FitFlow-TP-DDS
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
```

### 3. Activar Entorno Virtual

**Windows (Git Bash):**
```bash
source venv/Scripts/activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 5. Inicializar Base de Datos
```bash
python -m src.main init-db
```

### 6. Ejecutar la Aplicación
```bash
python -m src.main
```

La aplicación estará disponible en: `http://localhost:5000`

## 🧪 Ejecutar Pruebas

### Ejecutar todos los tests
```bash
pytest
```

### Ejecutar tests con reporte detallado
```bash
pytest -v
```

### Ejecutar tests de una entrega específica
```bash
pytest tests/test_entrega2.py
pytest tests/test_entrega3.py
```

### Test manual completo (todas las entregas)
```bash
python tests/manual_test_completo.py
```

## 📡 API Endpoints Principales

- **`GET /api`** - Información de la API
- **`GET /api/clases`** - Listar clases
- **`POST /api/reservas`** - Crear reserva
- **`GET /api/estadisticas/dashboard`** - Dashboard de estadísticas
- **`GET /api/clases/<id>/reporte-asistencia`** - Descargar CSV de asistencia
- **`GET /health`** - Health check del sistema

## 🔧 Configuración

Puedes configurar la aplicación mediante variables de entorno en un archivo `.env`:

```env
# Base de datos
DATABASE_URL=sqlite:///src/instance/fitflow.db

# Aplicación
SECRET_KEY=tu-clave-secreta
DEBUG=False
PORT=5000

# Seguridad
BLOCKED_IPS=192.168.1.100,10.0.0.5

# Proxies externos
PASARELA_PAGOS_API_KEY=tu-api-key
CLASES_EXTERNAS_API_KEY=tu-api-key
```

## 🏗️ Arquitectura

- **Backend**: Flask (Python)
- **ORM**: SQLAlchemy
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **WebSockets**: Flask-SocketIO
- **Rate Limiting**: Flask-Limiter
- **Patrones**: Repository, Service Layer, Strategy, Proxy

## 📂 Estructura del Proyecto

```
FitFlow-TP-DDS/
├── src/
│   ├── api/controllers/     # Controladores REST
│   ├── models/              # Modelos SQLAlchemy
│   ├── services/            # Lógica de negocio
│   ├── repositories/        # Acceso a datos
│   ├── datasources/proxy/   # Integraciones externas
│   ├── validators/          # Validadores
│   ├── templates/           # Templates HTML
│   ├── config/              # Configuración
│   └── main.py              # Entry point
├── tests/                   # Tests automatizados
└── requirements.txt         # Dependencias
```

## 👥 Autores

Trabajo Práctico - Diseño de Sistemas de Software I (2025)