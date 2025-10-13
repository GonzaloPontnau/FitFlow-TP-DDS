# Changelog - FitFlow

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/).

## [1.0.0] - 2025-01-XX - Entrega 1

### 🎉 Lanzamiento Inicial

Esta es la primera entrega del sistema FitFlow con la arquitectura base y funcionalidades core.

### ✨ Agregado

#### Modelos del Dominio
- `PlanMembresia`: Gestión de planes de membresía
- `Socio`: Manejo de información de socios
- `Clase`: Definición de clases grupales
- `Horario`: Programación de horarios
- `Entrenador`: Información de entrenadores
- `Reserva`: Sistema de reservas (preparado para Entrega 2)
- `SolicitudBaja`: Gestión de solicitudes de baja

#### Repositorios (Data Access Layer)
- `BaseRepository<T>`: Repositorio genérico con CRUD
- `SocioRepository`: Operaciones específicas de socios
- `PlanRepository`: Gestión de planes
- `ClaseRepository`: Consultas de clases con filtros
- `SolicitudBajaRepository`: Manejo de solicitudes
- `ReservaRepository`: Base para reservas (Entrega 2)

#### Servicios (Business Logic)
- `PlanService`: Lógica de negocio para planes
- `ClaseService`: Operaciones con clases y filtrado
- `SolicitudBajaService`: Procesamiento de solicitudes
- `CSVImporterService`: Importación masiva de socios desde CSV

#### Validadores
- `ValidadorDeSolicitudes`: Interfaz base
- `ValidadorLongitudMinima`: Valida longitud mínima (150 chars)
- `ValidadorPalabrasVacias`: Verifica contenido significativo
- `ValidadorCompuesto`: Combina múltiples validadores (Strategy Pattern)

#### Infraestructura
- Configuración de Flask como framework web
- Integración de SQLAlchemy como ORM
- Soporte para SQLite (desarrollo) y PostgreSQL (producción)
- Sistema de migraciones preparado
- Estructura de proyecto modular

#### Testing
- Suite de tests unitarios con pytest
- Tests de modelos del dominio
- Configuración de cobertura de código
- Fixtures para datos de prueba

#### Documentación
- README completo con guía de instalación
- ARQUITECTURA_PYTHON.md con decisiones de diseño
- QUICKSTART.md para inicio rápido
- Comentarios docstring en todo el código
- Archivo de ejemplo CSV para importación

#### Scripts de Automatización
- `setup.bat`: Instalación automática (Windows)
- `setup.sh`: Instalación automática (Linux/Mac)
- Script de inicialización de base de datos
- Datos de ejemplo pre-cargados

### 🏗️ Arquitectura

- **Patrón Repository**: Abstracción de acceso a datos
- **Service Layer**: Separación de lógica de negocio
- **Strategy Pattern**: Validadores intercambiables
- **Factory Pattern**: Creación de aplicación Flask
- **Dependency Injection**: Desacoplamiento de componentes

### 📋 Requerimientos Implementados (Entrega 1)

1. ✅ Crear Plan de Membresía (Administrador)
2. ✅ Importar socios desde CSV (Administrador)
3. ✅ Navegar clases disponibles (Socio Visualizador)
4. ✅ Filtrar clases por horario/día (Socio Visualizador)
5. ✅ Solicitar baja de membresía (Socio Registrado)
6. ✅ Aprobar/Rechazar solicitudes de baja (Administrador)

### 🔧 Configuración

- Variables de entorno con `.env.example`
- Configuración de Flask modular
- Database URL configurable
- Límites de tamaño para archivos CSV

### 📦 Dependencias Principales

- Flask 3.0.0
- Flask-SQLAlchemy 3.1.1
- Pandas 2.1.4
- Pytest 7.4.3
- Python-dotenv 1.0.0

---

## [Unreleased] - Próximas entregas

### 🚀 Entrega 2 (Planificado)
- [ ] Sistema de reservas funcional
- [ ] Integración con pasarelas de pago (Proxy Pattern)
- [ ] Integración con APIs externas de clases
- [ ] Rechazo automático de solicitudes inválidas
- [ ] Tareas asincrónicas

### 🚀 Entrega 3 (Planificado)
- [ ] API REST completa
- [ ] Servicio agregador de horarios
- [ ] Sistema de listas de espera
- [ ] Procesamiento asincrónico de asignaciones

### 🚀 Entrega 4 (Planificado)
- [ ] Migraciones con Alembic
- [ ] Servicio de estadísticas
- [ ] Soporte para contenido multimedia
- [ ] Exportación de reportes CSV
- [ ] Optimizaciones de queries

### 🚀 Entrega 5 (Planificado)
- [ ] Interfaz web con templates
- [ ] Panel de administración
- [ ] Dashboard de socios
- [ ] Autenticación y sesiones

### 🚀 Entrega 6 (Planificado)
- [ ] Despliegue en la nube
- [ ] Logs centralizados
- [ ] Métricas de rendimiento
- [ ] Rate limiting
- [ ] WebSockets para actualizaciones en tiempo real

---

## Formato de Versiones

- **Major**: Cambios incompatibles en la API
- **Minor**: Nueva funcionalidad compatible con versiones anteriores
- **Patch**: Corrección de bugs compatible con versiones anteriores

[1.0.0]: https://github.com/GonzaloPontnau/FitFlow-TP-DDS/releases/tag/v1.0.0
