# 🏗️ Arquitectura FitFlow - Sistema de Gestión para Gimnasios

## 📋 Índice
- [Información General](#información-general)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Arquitectura en Capas](#arquitectura-en-capas)
- [Componentes Principales](#componentes-principales)
- [Flujo de Datos](#flujo-de-datos)
- [Tecnologías](#tecnologías)

---

## 📌 Información General

**Proyecto:** FitFlow - TP Diseño de Sistemas 2025  
**Universidad:** Universidad Tecnológica Nacional (UTN)  
**Versión:** 3.0.0  
**Stack:** Python 3.10+, Flask 3.0, SQLAlchemy, SQLite

---

## 📂 Estructura del Proyecto

```
FitFlow-TP-DDS/
│
├── 📄 .env                          # Configuración de entorno (SECRET_KEY, DB, etc.)
├── 📄 run_server.py                 # Script principal para levantar el servidor
├── 📄 requirements.txt              # Dependencias del proyecto
├── 📄 README.md                     # Documentación principal
├── 📄 ARQUITECTURA.md              # Este archivo
├── 📄 ENTREGA3.md                  # Documentación de la Entrega 3
├── 📄 ENTREGAS.md                  # Resumen de todas las entregas
│
├── 📁 data/                         # Datos de entrada
│   └── socios_ejemplo.csv           # CSV de ejemplo para importación masiva
│
├── 📁 src/                          # Código fuente principal
│   ├── 📄 __init__.py
│   ├── 📄 main.py                   # Punto de entrada de la aplicación Flask
│   │
│   ├── 📁 api/                      # 🌐 Capa de Presentación (REST API)
│   │   ├── __init__.py
│   │   └── 📁 controllers/          # Controladores REST (Blueprints de Flask)
│   │       ├── __init__.py
│   │       ├── base_controller.py            # Controlador base con métodos comunes
│   │       ├── calendario_controller.py       # Calendario consolidado
│   │       ├── clase_controller.py           # CRUD de clases
│   │       ├── pago_controller.py            # Gestión de pagos
│   │       ├── plan_controller.py            # CRUD de planes de membresía
│   │       ├── reserva_controller.py         # Gestión de reservas
│   │       ├── socio_controller.py           # CRUD de socios
│   │       └── solicitud_baja_controller.py  # Gestión de solicitudes de baja
│   │
│   ├── 📁 services/                 # 🎯 Capa de Lógica de Negocio
│   │   ├── __init__.py
│   │   ├── agregador_horarios_service.py   # Servicio agregador (Entrega 3)
│   │   ├── clase_service.py               # Lógica de clases
│   │   ├── csv_importer_service.py        # Importación masiva CSV
│   │   ├── lista_espera_service.py        # Gestión de listas de espera
│   │   ├── pago_service.py                # Lógica de pagos
│   │   ├── plan_service.py                # Lógica de planes
│   │   ├── reserva_service.py             # Lógica de reservas
│   │   └── solicitud_baja_service.py      # Lógica de solicitudes
│   │
│   ├── 📁 repositories/             # 💾 Capa de Acceso a Datos
│   │   ├── __init__.py
│   │   ├── base_repository.py            # Repositorio base con operaciones CRUD
│   │   ├── clase_repository.py          # Acceso a datos de clases
│   │   ├── pago_repository.py           # Acceso a datos de pagos
│   │   ├── plan_repository.py           # Acceso a datos de planes
│   │   ├── reserva_repository.py        # Acceso a datos de reservas
│   │   ├── socio_repository.py          # Acceso a datos de socios
│   │   └── solicitud_baja_repository.py # Acceso a datos de solicitudes
│   │
│   ├── 📁 models/                   # 📊 Capa de Dominio (Entidades)
│   │   ├── __init__.py
│   │   ├── clase.py                 # Modelo de Clase
│   │   ├── clase_externa.py        # Modelo de Clase Externa
│   │   ├── entrenador.py           # Modelo de Entrenador
│   │   ├── horario.py              # Modelo de Horario
│   │   ├── lista_espera.py         # Modelo de Lista de Espera
│   │   ├── pago.py                 # Modelo de Pago
│   │   ├── plan_membresia.py       # Modelo de Plan de Membresía
│   │   ├── reserva.py              # Modelo de Reserva
│   │   ├── socio.py                # Modelo de Socio
│   │   └── solicitud_baja.py       # Modelo de Solicitud de Baja
│   │
│   ├── 📁 datasources/              # 🔌 Integraciones Externas
│   │   ├── __init__.py
│   │   └── 📁 proxy/
│   │       ├── __init__.py
│   │       ├── base_proxy.py              # Proxy base
│   │       ├── clases_externas_proxy.py   # API de clases externas (simulado)
│   │       └── pasarela_pagos_proxy.py    # Pasarela de pagos (simulado)
│   │
│   ├── 📁 validators/               # ✅ Validaciones de Negocio
│   │   ├── __init__.py
│   │   └── solicitud_validator.py   # Validación de solicitudes
│   │
│   ├── 📁 config/                   # ⚙️ Configuración
│   │   ├── __init__.py
│   │   ├── database.py              # Configuración de SQLAlchemy
│   │   ├── scheduler.py             # Configuración de tareas asincrónicas
│   │   └── settings.py              # Settings centralizados (Singleton)
│   │
│   ├── 📁 core/                     # 🔧 Utilidades Core
│   │   ├── __init__.py
│   │   ├── dtos.py                  # Data Transfer Objects
│   │   └── logging_config.py        # Configuración de logging
│   │
│   ├── 📁 utils/                    # 🛠️ Utilidades
│   │   ├── __init__.py
│   │   └── enums.py                 # Enumeraciones (EstadoPago, DiaSemana, etc.)
│   │
│   ├── 📁 exceptions/               # ⚠️ Excepciones Personalizadas
│   │   ├── __init__.py
│   │   └── base_exceptions.py       # Excepciones del dominio
│   │
│   └── 📁 instance/                 # 💾 Base de Datos
│       └── fitflow.db               # SQLite database (generado automáticamente)
│
└── 📁 tests/                        # 🧪 Pruebas
    ├── __init__.py
    ├── test_completo.py             # Tests integrales
    ├── test_entrega2.py             # Tests específicos Entrega 2
    ├── test_entrega3.py             # Tests específicos Entrega 3
    ├── test_models.py               # Tests de modelos
    └── test_simple.py               # Tests simples
```

---

## 🏛️ Arquitectura en Capas

El proyecto sigue una **arquitectura en capas** (Layered Architecture) con separación clara de responsabilidades:

### 1️⃣ Capa de Presentación (API Layer)
- **Ubicación:** `src/api/controllers/`
- **Responsabilidad:** Exponer endpoints REST, manejar requests/responses HTTP
- **Tecnología:** Flask Blueprints
- **Componentes:**
  - Controladores REST para cada entidad
  - Serialización/Deserialización JSON
  - Validación de entrada
  - Manejo de errores HTTP

### 2️⃣ Capa de Lógica de Negocio (Service Layer)
- **Ubicación:** `src/services/`
- **Responsabilidad:** Implementar reglas de negocio, orquestar operaciones
- **Patrones:** Service Pattern, Transaction Script
- **Componentes:**
  - Servicios por dominio (socios, clases, reservas, etc.)
  - Validaciones de negocio
  - Coordinación entre repositorios
  - Integración con servicios externos

### 3️⃣ Capa de Acceso a Datos (Repository Layer)
- **Ubicación:** `src/repositories/`
- **Responsabilidad:** Abstracción de acceso a la base de datos
- **Patrones:** Repository Pattern, Unit of Work
- **Componentes:**
  - Repositorios CRUD genéricos
  - Consultas especializadas
  - Gestión de transacciones

### 4️⃣ Capa de Dominio (Domain Layer)
- **Ubicación:** `src/models/`
- **Responsabilidad:** Definir entidades y modelos del negocio
- **Tecnología:** SQLAlchemy ORM
- **Componentes:**
  - Modelos de dominio con relaciones
  - Lógica de entidad
  - Validaciones a nivel de modelo

### 5️⃣ Capa de Infraestructura (Infrastructure Layer)
- **Ubicación:** `src/datasources/proxy/`, `src/config/`
- **Responsabilidad:** Integraciones externas, configuración
- **Patrones:** Proxy Pattern, Singleton Pattern
- **Componentes:**
  - Proxies para servicios externos
  - Configuración centralizada
  - Scheduler de tareas
  - Logging

---

## 🎯 Componentes Principales

### 🌐 API REST
```
Endpoints disponibles:

GET    /                           # Info de la API
GET    /health                     # Health check

SOCIOS:
GET    /api/socios                 # Listar socios
POST   /api/socios                 # Crear socio
GET    /api/socios/<id>            # Obtener socio
PUT    /api/socios/<id>            # Actualizar socio
DELETE /api/socios/<id>            # Eliminar socio
POST   /api/socios/import-csv      # Importación masiva

CLASES:
GET    /api/clases                 # Listar clases
POST   /api/clases                 # Crear clase
GET    /api/clases/<id>            # Obtener clase
PUT    /api/clases/<id>            # Actualizar clase
DELETE /api/clases/<id>            # Eliminar clase
POST   /api/clases/<id>/reservar   # Reservar clase

PLANES:
GET    /api/planes                 # Listar planes
POST   /api/planes                 # Crear plan
GET    /api/planes/<id>            # Obtener plan
PUT    /api/planes/<id>            # Actualizar plan
DELETE /api/planes/<id>            # Eliminar plan

RESERVAS:
GET    /api/reservas               # Listar reservas
POST   /api/reservas               # Crear reserva
GET    /api/reservas/<id>          # Obtener reserva
DELETE /api/reservas/<id>          # Cancelar reserva

SOLICITUDES DE BAJA:
GET    /api/solicitudes            # Listar solicitudes
POST   /api/solicitudes            # Crear solicitud
GET    /api/solicitudes/<id>       # Obtener solicitud
PUT    /api/solicitudes/<id>/aprobar   # Aprobar solicitud
PUT    /api/solicitudes/<id>/rechazar  # Rechazar solicitud

CALENDARIO:
GET    /api/calendario             # Calendario consolidado
GET    /api/calendario/actualizar  # Forzar actualización

PAGOS:
GET    /api/pagos                  # Listar pagos
POST   /api/pagos                  # Registrar pago
GET    /api/pagos/<id>             # Obtener pago
```

### 🔄 Servicios Principales

#### AgregadorHorariosService
- Consolida horarios de múltiples fuentes (internas y externas)
- Modos: NORMAL (solo con cupo) y OCUPADO (todas)
- Actualización automática cada hora

#### ListaEsperaService
- Gestión de listas de espera por clase
- Procesamiento nocturno automático (2:00 AM)
- Notificaciones de liberación de cupos

#### CSVImporterService
- Importación masiva de socios
- Validación de datos
- Procesamiento en lote

#### PagoService
- Integración con pasarela de pagos
- Procesamiento de transacciones
- Registro histórico

### ⏰ Tareas Asincrónicas (APScheduler)

```python
# Tareas programadas:
- Procesamiento de listas de espera: 02:00 AM diario
- Actualización de calendario: cada hora en punto
```

### 🔌 Integraciones (Proxies)

1. **PasarelaPagosProxy**
   - Simula integración con pasarela de pagos
   - Métodos: procesar_pago(), consultar_estado()

2. **ClasesExternasProxy**
   - Simula integración con API de clases externas
   - Métodos: obtener_clases_disponibles()

---

## 🔀 Flujo de Datos

### Ejemplo: Crear una Reserva

```
1. Cliente HTTP
   ↓ POST /api/reservas
   
2. ReservaController
   ↓ Validación de entrada
   ↓ Transformación a DTO
   
3. ReservaService
   ↓ Validación de negocio (cupo disponible, plan válido)
   ↓ Coordinación con otros servicios
   
4. ReservaRepository + ClaseRepository
   ↓ Consultas a la base de datos
   ↓ Creación de registros
   
5. SQLAlchemy ORM
   ↓ SQL generado
   
6. SQLite Database
   ↓ Persistencia
   
← Response JSON al cliente
```

---

## 🛠️ Tecnologías

### Backend
- **Python 3.10+**: Lenguaje principal
- **Flask 3.0.0**: Framework web
- **Flask-SQLAlchemy 3.1.1**: ORM
- **Waitress**: Servidor WSGI de producción
- **APScheduler 3.10+**: Tareas asincrónicas
- **python-dotenv 1.0.0**: Gestión de variables de entorno

### Datos
- **SQLite**: Base de datos (desarrollo)
- **Pandas 2.2+**: Procesamiento de CSV

### Testing
- **Pytest 8.0+**: Framework de testing
- **pytest-cov 4.1+**: Cobertura de código

### Calidad de Código
- **Flake8 6.1+**: Linter
- **Black 23.12+**: Formateador

---

## 🎨 Patrones de Diseño Implementados

1. **Repository Pattern**: Abstracción del acceso a datos
2. **Service Layer Pattern**: Encapsulación de lógica de negocio
3. **Singleton Pattern**: Configuración centralizada (Settings)
4. **Proxy Pattern**: Integración con servicios externos
5. **Factory Pattern**: Creación de la aplicación Flask (create_app)
6. **DTO Pattern**: Transferencia de datos entre capas
7. **MVC Pattern**: Separación Modelo-Vista-Controlador

---

## 🚀 Cómo Levantar el Proyecto

### 1. Configuración Inicial
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
```

### 2. Configuración de Variables de Entorno
Editar `.env` con tu configuración:
```env
DATABASE_URL=sqlite:///C:/ruta/absoluta/src/instance/fitflow.db
DEBUG=true
SECRET_KEY=tu-secret-key-generada
```

### 3. Levantar el Servidor
```bash
# Opción 1: Script personalizado (recomendado)
python run_server.py

# Opción 2: Flask CLI
export FLASK_APP=src.main
flask run

# Opción 3: Python directo
python -m src.main
```

El servidor estará disponible en: **http://localhost:5000**

### 4. Verificar Funcionamiento
```bash
# Health check
curl http://localhost:5000/health

# Info de la API
curl http://localhost:5000/
```

---

## 📊 Modelo de Datos

### Entidades Principales

1. **Socio**: Miembros del gimnasio
2. **PlanMembresia**: Planes de suscripción
3. **Clase**: Clases disponibles
4. **Entrenador**: Instructores
5. **Horario**: Horarios de clases
6. **Reserva**: Reservas de socios a clases
7. **Pago**: Transacciones de pago
8. **SolicitudBaja**: Solicitudes de baja de socios
9. **ListaEspera**: Colas de espera por clase
10. **ClaseExterna**: Clases de proveedores externos

### Relaciones Principales
- Socio ← many-to-one → PlanMembresia
- Clase ← many-to-one → Entrenador
- Clase ← many-to-one → Horario
- Clase ← many-to-many → PlanMembresia
- Reserva ← many-to-one → Socio
- Reserva ← many-to-one → Clase
- ListaEspera ← many-to-one → Socio
- ListaEspera ← many-to-one → Clase

---

## 📝 Documentos Adicionales

- **README.md**: Documentación principal y guía de uso
- **ENTREGA3.md**: Especificaciones de la Entrega 3
- **ENTREGAS.md**: Resumen de todas las entregas
- **requirements.txt**: Listado de dependencias
- **.env**: Configuración de entorno (no versionado)

---

## 👥 Equipo

**Proyecto:** Trabajo Práctico Anual Integrador  
**Materia:** Diseño de Sistemas  
**Universidad:** Universidad Tecnológica Nacional (UTN)  
**Año:** 2025

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico de la UTN.

---

**Última actualización:** 10 de noviembre de 2025
