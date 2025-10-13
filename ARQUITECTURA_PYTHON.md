# Arquitectura FitFlow - Sistema de Gestión para Gimnasios

## Versión: Python 1.0.0

### Índice
1. [Visión General](#visión-general)
2. [Arquitectura en Capas](#arquitectura-en-capas)
3. [Modelos del Dominio](#modelos-del-dominio)
4. [Patrones de Diseño Aplicados](#patrones-de-diseño-aplicados)
5. [Flujo de Datos](#flujo-de-datos)
6. [Decisiones Arquitectónicas](#decisiones-arquitectónicas)

---

## Visión General

FitFlow está construido siguiendo una arquitectura en capas que separa las responsabilidades y facilita el mantenimiento y escalabilidad del sistema. La aplicación utiliza Python 3.10+ con Flask como framework web y SQLAlchemy como ORM.

### Stack Tecnológico
- **Backend**: Python 3.10+, Flask
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Procesamiento CSV**: Pandas
- **Testing**: Pytest
- **Calidad de Código**: Flake8, Black

---

## Arquitectura en Capas

```
┌─────────────────────────────────────────────────────┐
│              Presentación (Futura)                  │
│         Controllers / REST API / Web UI             │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              Capa de Servicios                      │
│    - PlanService                                    │
│    - ClaseService                                   │
│    - SolicitudBajaService                           │
│    - CSVImporterService                             │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│            Capa de Repositorios                     │
│    - SocioRepository                                │
│    - PlanRepository                                 │
│    - ClaseRepository                                │
│    - SolicitudBajaRepository                        │
│    - ReservaRepository                              │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│              Capa de Dominio                        │
│    Modelos: Socio, Plan, Clase, Reserva, etc.      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│            Base de Datos (SQLAlchemy)               │
└─────────────────────────────────────────────────────┘
```

## Patrones de Diseño Aplicados

### 1. Repository Pattern
Abstracción del acceso a datos con repositorios genéricos y específicos.

### 2. Service Layer Pattern
Lógica de negocio centralizada en servicios reutilizables.

### 3. Strategy Pattern
Validadores intercambiables para solicitudes de baja.

### 4. Factory Pattern
Creación de la aplicación Flask mediante `create_app()`.

---

## Estructura del Proyecto

```
src/
├── models/              # Entidades del dominio
├── repositories/        # Acceso a datos
├── services/            # Lógica de negocio
├── validators/          # Validaciones
├── config/             # Configuración
└── main.py             # Punto de entrada
```

## Comandos Útiles

```bash
# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos
python -m src.main init-db

# Ejecutar aplicación
python -m src.main

# Ejecutar tests
pytest
```
