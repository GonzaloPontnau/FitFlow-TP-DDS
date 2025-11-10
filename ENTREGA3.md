# FitFlow - Entrega 3: API REST y Servicios Agregadores

## 📋 Resumen de la Entrega

La Entrega 3 implementa una API REST completa, servicios agregadores de horarios y gestión avanzada de listas de espera con tareas asincrónicas.

## ✨ Nuevas Funcionalidades

### 1. Servicio Agregador de Horarios

El sistema ahora consolida horarios de múltiples fuentes en una vista unificada:

- **Clases internas**: Del gimnasio FitFlow
- **Talleres externos**: De proveedores externos vía API
- **Actualización automática**: Cada hora
- **Modos de visualización**:
  - `normal`: Solo clases con cupo disponible
  - `ocupado`: Todas las clases, incluso sin cupo

**Endpoint:** `GET /api/calendario?modo=normal`

### 2. Gestión de Listas de Espera

Sistema completo para gestionar listas de espera en clases sin cupo:

- Inscripción automática cuando no hay cupo
- Notificación por email al liberarse un lugar
- Tiempo limitado (24h) para confirmar el lugar
- Procesamiento nocturno automatizado (2:00 AM)
- Reasignación automática si no se confirma

**Endpoints:**
- `POST /api/clases/:id/lista-espera` - Habilitar lista de espera
- `GET /api/clases/:id/lista-espera` - Ver lista de espera

### 3. API REST Completa

#### Gestión de Clases (CRUD Completo)

```bash
# Listar clases
GET /api/clases?dia=lunes&con_cupo=true

# Obtener clase
GET /api/clases/:id

# Crear clase
POST /api/clases
{
  "titulo": "Spinning Avanzado",
  "descripcion": "Clase intensiva de spinning",
  "cupo_maximo": 20,
  "entrenador_id": 1,
  "horario_id": 5,
  "tiene_lista_espera": true
}

# Actualizar clase
PUT /api/clases/:id
{
  "titulo": "Spinning Pro",
  "cupo_maximo": 25
}

# Eliminar clase
DELETE /api/clases/:id
```

#### Gestión de Planes (CRUD Completo)

```bash
# Listar planes
GET /api/planes

# Obtener plan
GET /api/planes/:id

# Crear plan
POST /api/planes
{
  "titulo": "Plan Premium",
  "descripcion": "Acceso a todas las clases",
  "precio": 15000.00
}

# Actualizar plan
PUT /api/planes/:id
{
  "precio": 16000.00
}

# Eliminar plan
DELETE /api/planes/:id

# Agregar clase a plan
POST /api/planes/:id/clases/:clase_id

# Quitar clase de plan
DELETE /api/planes/:id/clases/:clase_id
```

#### Gestión de Solicitudes de Baja

```bash
# Listar solicitudes pendientes
GET /api/solicitudes

# Crear solicitud
POST /api/solicitudes
{
  "socio_id": 123,
  "justificacion": "Me mudo de ciudad por trabajo..."
}

# Aprobar solicitud
PUT /api/solicitudes/:id/aprobar
{
  "comentario_admin": "Solicitud aprobada"
}

# Rechazar solicitud
PUT /api/solicitudes/:id/rechazar
{
  "comentario_admin": "No cumple requisitos"
}

# Ver solicitudes de un socio
GET /api/solicitudes/socio/:id
```

#### Calendario Consolidado

```bash
# Obtener calendario (modo normal)
GET /api/calendario?modo=normal

# Obtener calendario completo (modo ocupado)
GET /api/calendario?modo=ocupado

# Filtrar por fechas
GET /api/calendario?fecha_desde=2025-11-10&fecha_hasta=2025-11-17

# Estadísticas del calendario
GET /api/calendario/estadisticas

# Forzar actualización
POST /api/calendario/actualizar
```

### 4. Tareas Asincrónicas

El sistema ejecuta automáticamente:

#### Procesamiento de Lista de Espera
- **Cuándo**: 2:00 AM diariamente
- **Qué hace**:
  - Procesa entradas expiradas
  - Notifica a personas en espera
  - Asigna lugares liberados

#### Actualización de Calendario
- **Cuándo**: Cada hora en punto
- **Qué hace**:
  - Consulta fuentes externas
  - Actualiza caché del calendario
  - Consolida horarios

## 🏗️ Arquitectura

### Nuevos Componentes

```
src/
├── models/
│   └── lista_espera.py          # Modelo de lista de espera
├── services/
│   ├── agregador_horarios_service.py  # Agregador de horarios
│   └── lista_espera_service.py        # Gestión de listas de espera
├── api/controllers/
│   ├── plan_controller.py             # CRUD de planes
│   ├── solicitud_baja_controller.py   # Gestión de solicitudes
│   └── calendario_controller.py       # Calendario consolidado
└── config/
    └── scheduler.py                    # Tareas programadas
```

### Flujo del Servicio Agregador

```
┌─────────────────┐
│ Clases Internas │
└────────┬────────┘
         │
         ├─────────> ┌──────────────────┐      ┌──────────────┐
┌────────┴────────┐  │    Agregador     │─────>│  Calendario  │
│ Talleres        │─>│   de Horarios    │      │ Consolidado  │
│ Externos (API)  │  └──────────────────┘      └──────────────┘
└─────────────────┘
```

### Flujo de Lista de Espera

```
1. Clase sin cupo
   ↓
2. Socio se inscribe en lista de espera
   ↓
3. Se libera un lugar
   ↓
4. [TAREA NOCTURNA] Notifica al primero en la lista
   ↓
5. Socio tiene 24h para confirmar
   ↓
6a. Confirma → Se crea la reserva
6b. No confirma → Se notifica al siguiente
```

## 🚀 Cómo Usar

### Iniciar el Sistema

```bash
# Instalar dependencias
pip install -r requirements.txt

# Iniciar servidor
python -m src.main
```

El servidor iniciará en `http://localhost:5000` con:
- ✅ API REST completa
- ✅ Scheduler de tareas activado
- ✅ Agregador de horarios operativo

### Ejemplos de Uso

#### 1. Crear una clase con lista de espera

```bash
curl -X POST http://localhost:5000/api/clases \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Yoga Avanzado",
    "descripcion": "Clase de yoga nivel avanzado",
    "cupo_maximo": 10,
    "entrenador_id": 1,
    "horario_id": 3,
    "tiene_lista_espera": true
  }'
```

#### 2. Ver calendario en modo normal

```bash
curl http://localhost:5000/api/calendario?modo=normal
```

#### 3. Gestionar plan de membresía

```bash
# Crear plan
curl -X POST http://localhost:5000/api/planes \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "Plan Platinum",
    "descripcion": "Todas las clases + talleres externos",
    "precio": 20000.00
  }'

# Agregar clase al plan
curl -X POST http://localhost:5000/api/planes/1/clases/5
```

#### 4. Procesar solicitud de baja

```bash
# Aprobar
curl -X PUT http://localhost:5000/api/solicitudes/10/aprobar \
  -H "Content-Type: application/json" \
  -d '{
    "comentario_admin": "Solicitud aprobada correctamente"
  }'
```

## 📊 Respuestas de API

Todas las respuestas siguen el formato:

```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": { ... }
}
```

En caso de error:

```json
{
  "success": false,
  "message": "Descripción del error"
}
```

## 🔧 Configuración

### APScheduler

Las tareas se configuran en `src/config/scheduler.py`:

```python
# Procesamiento de lista de espera: 2:00 AM
scheduler.agregar_tarea_nocturna(
    func=procesar_lista_espera_nocturna,
    hora=2,
    minuto=0,
    job_id='procesar_lista_espera'
)

# Actualización de calendario: cada hora
scheduler.agregar_tarea_horaria(
    func=actualizar_calendario_horario,
    minuto=0,
    job_id='actualizar_calendario'
)
```

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

## 📝 Notas Importantes

1. **Lista de Espera**: Solo funciona para clases que tengan `tiene_lista_espera=True`
2. **Tiempo de Confirmación**: Por defecto 24 horas, configurable en `ListaEsperaService`
3. **Calendario**: Se actualiza automáticamente cada hora, pero puede forzarse manualmente
4. **Notificaciones**: Actualmente simuladas en logs, listas para integración con email real

## 🎯 Próximos Pasos (Entrega 4)

- Persistencia con PostgreSQL
- Servicio de estadísticas
- Contenido multimedia en clases
- Exportación de reportes CSV

---

**Versión**: 3.0.0  
**Fecha**: Noviembre 2025  
**Estado**: ✅ Completada
