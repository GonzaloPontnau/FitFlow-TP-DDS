# FitFlow: Sistema de Gestión Integral para Gimnasios

## Trabajo Práctico Anual - Diseño de Sistemas de Software I (2025)

---

## 1. Introducción

### 1.1 Contexto

FitFlow es un sistema de código abierto diseñado para la gestión integral de operaciones de gimnasios. El sistema permite:

- Gestión de socios y membresías
- Administración de clases y horarios
- Sistema de reservas con listas de espera
- Integración con servicios externos (pagos, clases de terceros)
- Panel de estadísticas y reportes

### 1.2 Tecnologías Utilizadas

| Componente | Tecnología |
|------------|------------|
| Backend | Python 3.x + Flask |
| ORM | SQLAlchemy |
| Base de Datos | SQLite (dev) / PostgreSQL (prod) |
| WebSockets | Flask-SocketIO |
| Rate Limiting | Flask-Limiter |
| Servidor WSGI | Gunicorn + gevent |
| Containerización | Docker |

---

## 2. Arquitectura del Sistema

### 2.1 Arquitectura en Capas

```
┌─────────────────────────────────────────────┐
│             Capa de Presentación            │
│     (Templates HTML + API REST + WS)        │
├─────────────────────────────────────────────┤
│              Capa de Servicios              │
│    (Lógica de negocio, validaciones)        │
├─────────────────────────────────────────────┤
│             Capa de Repositorios            │
│        (Acceso a datos, queries)            │
├─────────────────────────────────────────────┤
│               Capa de Modelos               │
│         (Entidades SQLAlchemy)              │
├─────────────────────────────────────────────┤
│           Fuentes de Datos                  │
│   (SQLite, Proxies Externos, CSV)           │
└─────────────────────────────────────────────┘
```

### 2.2 Patrones de Diseño Implementados

1. **Repository Pattern**: Abstracción del acceso a datos
2. **Service Layer**: Lógica de negocio centralizada
3. **Strategy Pattern**: Validadores de solicitudes intercambiables
4. **Proxy Pattern**: Integración con servicios externos
5. **Application Factory**: Creación configurable de la app Flask

### 2.3 Estructura del Proyecto

```
FitFlow-TP-DDS/
├── src/
│   ├── api/controllers/     # Controladores REST
│   ├── models/              # Modelos SQLAlchemy
│   ├── services/            # Lógica de negocio
│   ├── repositories/        # Acceso a datos
│   ├── datasources/proxy/   # Integraciones externas
│   ├── validators/          # Validadores (Strategy)
│   ├── templates/           # Templates HTML
│   ├── config/              # Configuración
│   ├── core/                # Logging, DTOs
│   └── main.py              # Entry point
├── tests/                   # Tests automatizados
├── Dockerfile               # Containerización
├── docker-compose.yml       # Orquestación
├── Procfile                 # Deploy cloud
├── render.yaml              # Render Blueprint
└── requirements.txt         # Dependencias
```

---

## 3. Entregas Implementadas

### 3.1 Entrega 1: Dominio Base

**Objetivo**: Modelar las abstracciones principales del dominio.

**Funcionalidades**:
- Modelo de dominio: Socio, Clase, Plan, Entrenador, Horario
- Carga masiva de socios desde CSV
- Sistema de roles (Administrador, Socio Registrado, Visualizador)
- Solicitudes de baja con validación de 150 caracteres mínimos

**Archivos clave**:
- `src/models/socio.py`
- `src/models/plan_membresia.py`
- `src/models/clase.py`
- `src/services/csv_importer_service.py`

---

### 3.2 Entrega 2: Integraciones

**Objetivo**: Integrar servicios externos y gestión de reservas.

**Funcionalidades**:
- Sistema de reservas con validación de cupos
- Cancelación hasta 24h antes
- Proxy para Pasarela de Pagos externa
- Proxy para Clases Externas (talleres de terceros)
- Rechazo automático de solicitudes inválidas (Strategy Pattern)

**Archivos clave**:
- `src/services/reserva_service.py`
- `src/datasources/proxy/pasarela_pagos_proxy.py`
- `src/datasources/proxy/clases_externas_proxy.py`
- `src/validators/solicitud_validator.py`

**Patrón Strategy para Validadores**:
```python
class ValidadorCompuesto(ValidadorDeSolicitudes):
    def __init__(self):
        self.validadores = [
            ValidadorLongitudMinima(),
            ValidadorPalabrasVacias()
        ]
    
    def es_valida(self, texto: str) -> bool:
        return all(v.es_valida(texto) for v in self.validadores)
```

---

### 3.3 Entrega 3: Agregador y API REST

**Objetivo**: Consolidar datos de múltiples fuentes y exponer API.

**Funcionalidades**:
- Servicio Agregador de Horarios (clases internas + externas)
- Sistema de Listas de Espera con notificaciones
- Modos de visualización: Normal (solo con cupo) y Ocupado (todas)
- API REST completa para todas las operaciones

**Archivos clave**:
- `src/services/agregador_horarios_service.py`
- `src/services/lista_espera_service.py`
- `src/api/controllers/` (todos los controladores)

**Endpoints principales**:
| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /api/clases | Listar clases |
| POST | /api/reservas | Crear reserva |
| GET | /api/calendario | Calendario consolidado |
| POST | /api/planes | Crear plan (admin) |

---

### 3.4 Entrega 4: Persistencia y Estadísticas

**Objetivo**: Persistir datos y generar estadísticas.

**Funcionalidades**:
- Persistencia completa con SQLAlchemy
- Soporte multimedia (imagen/video en clases)
- Servicio de Estadísticas con Dashboard
- Exportación de asistencia a CSV

**Estadísticas implementadas**:
- Franja horaria con más reservas
- Clase más popular históricamente
- Plan que genera más ingresos
- Tasa de presentismo promedio

**Archivos clave**:
- `src/services/estadisticas_service.py`
- `src/models/clase.py` (campos imagen_url, video_url)

---

### 3.5 Entrega 5: Web MVC

**Objetivo**: Interfaz web con Server-Side Rendering.

**Funcionalidades**:
- Templates HTML con Flask/Jinja2
- Vista de calendario semanal/mensual
- Panel administrativo
- Gestión de reservas desde la web

**Templates implementados**:
- `index.html` - Página principal
- `calendario.html` - Calendario de clases
- `socios.html` - Gestión de socios
- `clases.html` - Gestión de clases
- `planes.html` - Planes de membresía
- `reservas.html` - Sistema de reservas

---

### 3.6 Entrega 6: Despliegue y Seguridad

**Objetivo**: Preparar para producción con seguridad y observabilidad.

**Funcionalidades**:
- WebSockets para actualizaciones en tiempo real
- Rate Limiting (10 req/min en /api)
- Bloqueo de IPs configurable
- Sistema de logging con archivos
- Health check mejorado
- Configuración Docker y cloud

**Archivos de deployment**:
- `Dockerfile` - Contenedor Python con Gunicorn
- `docker-compose.yml` - Orquestación con persistencia
- `Procfile` - Para Render/Railway/Heroku
- `render.yaml` - Blueprint para Render

**Health Check mejorado**:
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "timestamp": "2025-12-11T23:45:00",
  "checks": {
    "database": {"status": "connected", "type": "sqlite"},
    "scheduler": {"status": "running"}
  },
  "response_time_ms": 5.23
}
```

---

## 4. Ejecución del Proyecto

### 4.1 Instalación Local

```bash
# Clonar repositorio
git clone <repository-url>
cd FitFlow-TP-DDS

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python -m src.main init-db

# Ejecutar servidor
python -m src.main
```

### 4.2 Ejecución con Docker

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### 4.3 Ejecutar Tests

```bash
# Todos los tests
python -m pytest tests/ -v

# Solo tests de una entrega
python -m pytest tests/test_entrega6.py -v
```

---

## 5. Despliegue en la Nube

### 5.1 Opción: Render

1. Subir código a GitHub
2. Crear cuenta en render.com
3. Nuevo Web Service → conectar repositorio
4. Render detecta automáticamente `render.yaml`
5. Deploy automático

### 5.2 Opción: Docker

```bash
docker build -t fitflow .
docker run -p 5000:5000 fitflow
```

---

## 6. API Reference

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | /health | Estado del servicio |
| GET | /api | Información de la API |
| GET | /api/socios | Listar socios |
| GET | /api/clases | Listar clases |
| POST | /api/reservas | Crear reserva |
| GET | /api/calendario | Calendario consolidado |
| GET | /api/estadisticas/dashboard | Dashboard de estadísticas |
| GET | /api/clases/{id}/reporte-asistencia | CSV de asistencia |

---

## 7. Conclusiones

FitFlow implementa exitosamente todos los requerimientos del Trabajo Práctico Anual:

✅ **Entrega 1**: Dominio modelado con OOP  
✅ **Entrega 2**: Integraciones con Strategy y Proxy patterns  
✅ **Entrega 3**: API REST y Agregador de servicios  
✅ **Entrega 4**: Persistencia SQLAlchemy y estadísticas  
✅ **Entrega 5**: Interfaz Web MVC  
✅ **Entrega 6**: Deployment, seguridad y observabilidad  

El sistema está listo para despliegue en producción con configuración Docker y soporte para plataformas cloud.

---

**Trabajo Práctico - Diseño de Sistemas de Software I (2025)**
