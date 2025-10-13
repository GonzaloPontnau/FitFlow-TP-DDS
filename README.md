# FitFlow - Sistema de Gestión Integral para Gimnasios

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Sistema de código abierto para la gestión integral de operaciones en gimnasios y centros de fitness.

## 🚀 Inicio Rápido

### Requisitos Previos
- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git

### Instalación Automática

**Windows:**
```bash
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Instalación Manual

1. **Clonar el repositorio**
```bash
git clone https://github.com/GonzaloPontnau/FitFlow-TP-DDS.git
cd FitFlow-TP-DDS
```

2. **Crear entorno virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. **Inicializar base de datos**
```bash
python -m src.main init-db
```

6. **Ejecutar la aplicación**
```bash
python -m src.main
```

La aplicación estará disponible en: `http://localhost:5000`

## 📋 Alcance - Entrega 1

### Funcionalidades Implementadas

✅ **Fuentes Estáticas**: Carga masiva de socios desde archivos CSV  
✅ **Gestión de Planes**: CRUD completo de planes de membresía  
✅ **Gestión de Clases**: Creación y filtrado de clases  
✅ **Roles**: Soporte para Administrador, Socio Registrado y Visualizador  
✅ **Solicitudes de Baja**: Sistema completo de solicitudes con validación  

### Requerimientos Cubiertos

1. ✅ Como administrador, deseo crear un Plan de Membresía
2. ✅ Como administrador, deseo importar socios desde un archivo CSV
3. ✅ Como socio visualizador, deseo navegar todas las clases disponibles de un Plan
4. ✅ Como socio visualizador, deseo filtrar las clases por horario o día
5. ✅ Como socio registrado, deseo poder solicitar la baja de mi membresía
6. ✅ Como administrador, deseo poder aceptar o rechazar una solicitud de baja

## 🏗️ Arquitectura

El proyecto sigue una arquitectura en capas con separación de responsabilidades:

```
src/
├── models/              # Entidades del dominio (Socio, Clase, Plan, etc.)
├── repositories/        # Acceso a datos (Repository Pattern)
├── services/            # Lógica de negocio (Service Layer)
├── validators/          # Validaciones de negocio
├── config/             # Configuración de la aplicación
└── main.py             # Punto de entrada
```

Para más detalles, consulta [ARQUITECTURA_PYTHON.md](ARQUITECTURA_PYTHON.md)

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Tests con cobertura
pytest --cov=src tests/

# Tests con reporte HTML
pytest --cov=src --cov-report=html tests/
```

## 📊 Uso

### Importar Socios desde CSV

```python
from src.services import CSVImporterService

service = CSVImporterService()
resultado = service.importar_socios('data/socios_ejemplo.csv')

print(f"Creados: {resultado['creados']}")
print(f"Actualizados: {resultado['actualizados']}")
```

### Crear un Plan de Membresía

```python
from src.services import PlanService

service = PlanService()
plan = service.crear_plan(
    titulo="Plan Premium",
    descripcion="Acceso total al gimnasio",
    precio=15000.0
)
```

### Filtrar Clases

```python
from src.services import ClaseService
from src.utils.enums import DiaSemana

service = ClaseService()

# Todas las clases activas
clases = service.listar_clases_activas()

# Clases de un día específico
clases_lunes = service.listar_clases_por_dia(DiaSemana.LUNES)

# Clases con cupo disponible
clases_con_cupo = service.listar_clases_con_cupo()
```

## 🛠️ Tecnologías

- **Backend**: Python 3.10+
- **Framework Web**: Flask 3.0.0
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)
- **Base de Datos**: SQLite (desarrollo), PostgreSQL (producción)
- **Procesamiento CSV**: Pandas
- **Testing**: Pytest
- **Code Quality**: Flake8, Black

## 📁 Estructura del Proyecto

```
FitFlow-TP-DDS/
├── src/
│   ├── models/              # Modelos del dominio
│   ├── repositories/        # Repositorios de datos
│   ├── services/            # Servicios de negocio
│   ├── validators/          # Validadores
│   ├── config/             # Configuración
│   └── main.py             # Aplicación principal
├── tests/                   # Tests unitarios
├── data/                    # Datos de ejemplo
├── requirements.txt         # Dependencias
├── setup.bat/.sh           # Scripts de instalación
└── README.md               # Este archivo
```

## 🎯 Roadmap

### Entrega 2 (Próxima)
- [ ] Gestión de reservas a clases
- [ ] Integración con pasarelas de pago
- [ ] Integración con APIs externas
- [ ] Rechazo automático de solicitudes

### Entrega 3
- [ ] API REST completa
- [ ] Servicio agregador de horarios
- [ ] Gestión de listas de espera

### Entrega 4
- [ ] Persistencia avanzada
- [ ] Servicio de estadísticas
- [ ] Soporte multimedia

### Entrega 5
- [ ] Interfaz web (UI/UX)
- [ ] Panel de administración
- [ ] Dashboard de socios

### Entrega 6
- [ ] Despliegue en la nube
- [ ] Observabilidad y monitoreo
- [ ] Medidas de seguridad

## 👥 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto es de código abierto y está disponible bajo la Licencia MIT.

## 📧 Contacto

Gonzalo Pontnau - [GitHub](https://github.com/GonzaloPontnau)

Proyecto: [https://github.com/GonzaloPontnau/FitFlow-TP-DDS](https://github.com/GonzaloPontnau/FitFlow-TP-DDS)

---

**Trabajo Práctico Anual Integrador - Diseño de Sistemas 2025**  
Universidad Tecnológica Nacional (UTN)