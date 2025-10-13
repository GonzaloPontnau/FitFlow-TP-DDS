# FitFlow - Sistema de Gestión Integral para Gimnasios

## Arquitectura del Proyecto (Python)

### Estructura del Proyecto

```
FitFlow-TP-DDS/
├── src/
│   ├── __init__.py
│   ├── main.py                      # Punto de entrada de la aplicación
│   ├── config/
│   │   ├── __init__.py
│   │   └── database.py              # Configuración de base de datos
│   ├── models/                      # Entidades del dominio
│   │   ├── __init__.py
│   │   ├── socio.py
│   │   ├── plan_membresia.py
│   │   ├── clase.py
│   │   ├── entrenador.py
│   │   ├── horario.py
│   │   ├── reserva.py
│   │   └── solicitud_baja.py
│   ├── repositories/                # Acceso a datos
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── socio_repository.py
│   │   ├── plan_repository.py
│   │   ├── clase_repository.py
│   │   └── solicitud_baja_repository.py
│   ├── services/                    # Lógica de negocio
│   │   ├── __init__.py
│   │   ├── socio_service.py
│   │   ├── plan_service.py
│   │   ├── clase_service.py
│   │   ├── csv_importer_service.py
│   │   └── solicitud_baja_service.py
│   ├── datasources/                 # Fuentes de datos
│   │   ├── __init__.py
│   │   ├── static_datasource.py     # Carga desde CSV
│   │   └── dynamic_datasource.py    # Datos dinámicos
│   ├── controllers/                 # Controladores (para futuro REST API)
│   │   ├── __init__.py
│   │   ├── admin_controller.py
│   │   └── socio_controller.py
│   ├── validators/                  # Validaciones
│   │   ├── __init__.py
│   │   └── solicitud_validator.py
│   └── utils/                       # Utilidades
│       ├── __init__.py
│       └── enums.py
├── tests/                           # Tests unitarios
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   └── test_repositories.py
├── data/                            # Datos de prueba
│   └── socios_ejemplo.csv
├── requirements.txt
├── .env.example
├── .gitignore
└── README_PYTHON.md
```

### Alcance - Entrega 1

**Fuentes estáticas:** Carga masiva de socios desde CSV
**Planes de Membresía:** CRUD de planes
**Clases:** Listado y filtrado por plan y horario
**Roles:** Administrador y Socio (modo visualizador)
**Solicitudes de baja:** Gestión de solicitudes con validación

### Instalación

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env

# Inicializar la base de datos
python -m src.main init-db
```

### Uso

```bash
# Ejecutar la aplicación
python -m src.main

# Ejecutar tests
pytest

# Ejecutar tests con cobertura
pytest --cov=src tests/
```

### Principios de Diseño

1. **Separación de Responsabilidades**: Modelo en capas (Models, Repositories, Services, Controllers)
2. **SOLID**: Aplicación de principios de diseño orientado a objetos
3. **Repository Pattern**: Abstracción del acceso a datos
4. **Service Layer**: Lógica de negocio centralizada
5. **Dependency Injection**: Desacoplamiento de componentes

### Tecnologías

- **Python 3.10+**
- **Flask**: Framework web
- **SQLAlchemy**: ORM para persistencia
- **Pandas**: Procesamiento de archivos CSV
- **Pytest**: Testing
