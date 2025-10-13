# Guía de Inicio Rápido - FitFlow

## 🚀 Configuración Inicial (5 minutos)

### Paso 1: Preparar el Entorno

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### Paso 2: Verificar la Instalación

```bash
# Activar entorno virtual
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Verificar que todo funciona
python -m pytest tests/
```

### Paso 3: Ejecutar la Aplicación

```bash
python -m src.main
```

Navega a: `http://localhost:5000`

## 📝 Ejemplos Prácticos

### 1. Crear Datos de Prueba

La base de datos ya viene con datos de ejemplo:
- 2 Planes de membresía
- 2 Entrenadores
- 2 Clases

### 2. Importar Socios desde CSV

```python
from src.services import CSVImporterService

service = CSVImporterService()
stats = service.importar_socios('data/socios_ejemplo.csv')

print(f"✓ {stats['creados']} socios creados")
print(f"✓ {stats['actualizados']} socios actualizados")
if stats['errores']:
    print(f"❌ Errores: {stats['errores']}")
```

### 3. Trabajar con Planes

```python
from src.services import PlanService

plan_service = PlanService()

# Listar planes activos
planes = plan_service.listar_planes_activos()
for plan in planes:
    print(f"{plan.titulo}: ${plan.precio}")

# Crear nuevo plan
nuevo_plan = plan_service.crear_plan(
    titulo="Plan Estudiantes",
    descripcion="Plan especial con descuento para estudiantes",
    precio=8000.0
)
print(f"✓ Plan creado: {nuevo_plan.id}")
```

### 4. Filtrar Clases

```python
from src.services import ClaseService
from src.utils.enums import DiaSemana

clase_service = ClaseService()

# Clases del lunes
clases = clase_service.listar_clases_por_dia(DiaSemana.LUNES)
for clase in clases:
    print(f"{clase.titulo} - {clase.horario.hora_inicio}")

# Clases de un plan específico
clases_plan = clase_service.listar_clases_por_plan(plan_id=1)

# Solo clases con cupo disponible
clases_disponibles = clase_service.listar_clases_con_cupo()
```

### 5. Gestionar Solicitudes de Baja

```python
from src.services import SolicitudBajaService

solicitud_service = SolicitudBajaService()

# Crear solicitud
justificacion = """
Me mudo a otra ciudad por trabajo y no podré continuar
asistiendo al gimnasio. Agradezco la atención recibida
durante estos meses y espero que consideren mi solicitud
de baja de membresía.
"""

solicitud = solicitud_service.crear_solicitud(
    socio_id=1,
    justificacion=justificacion
)
print(f"✓ Solicitud creada: #{solicitud.id}")

# Listar solicitudes pendientes
pendientes = solicitud_service.listar_solicitudes_pendientes()
print(f"Hay {len(pendientes)} solicitudes pendientes")

# Aprobar solicitud
solicitud_service.aprobar_solicitud(
    solicitud_id=1,
    comentario_admin="Solicitud aprobada. Baja efectiva desde hoy."
)
```

## 🐛 Solución de Problemas Comunes

### Error: "Module not found"
```bash
# Asegúrate de estar en el entorno virtual
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "Database not found"
```bash
# Reinicializar la base de datos
python -m src.main init-db
```

### Error: "Port 5000 already in use"
```python
# Edita src/main.py y cambia el puerto:
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📊 Estructura de Datos CSV

Para importar socios, tu archivo CSV debe tener este formato:

```csv
Nombre,Apellido,DNI,Email,ID Plan Membresía
Juan,Pérez,12345678,juan.perez@example.com,1
María,García,23456789,maria.garcia@example.com,2
```

**Importante:**
- Los headers deben ser exactamente como se muestran
- El DNI debe ser único (se actualizará si ya existe)
- El ID Plan Membresía debe existir en la base de datos

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests específicos
pytest tests/test_models.py

# Con cobertura
pytest --cov=src tests/

# Con output detallado
pytest -v
```

## 📚 Siguiente Paso

Lee la [documentación de arquitectura](ARQUITECTURA_PYTHON.md) para entender mejor el diseño del sistema.
