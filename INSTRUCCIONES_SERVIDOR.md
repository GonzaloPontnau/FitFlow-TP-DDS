# 🚀 Guía Rápida - Levantar FitFlow en Local

## ✅ Completado

### 1. SECRET_KEY Generada
```
SECRET_KEY=0cbcd1bb6a....
```
✓ Ya configurada en `.env`

---

## 🏃 Instrucciones para Levantar el Servidor

### Opción A: Script Personalizado (RECOMENDADO)
```bash
# Desde el directorio raíz del proyecto
python run_server.py
```

### Opción B: Desde el terminal bash (Windows Git Bash)
```bash
# Ejecutar en segundo plano
python run_server.py &

# El servidor quedará corriendo en background
```

### Opción C: Flask CLI
```bash
export FLASK_APP=src.main
flask run --host=0.0.0.0 --port=5000
```

---

## 🔍 Verificar que Funciona

### 1. Health Check
```bash
curl http://localhost:5000/health
```

**Respuesta esperada:**
```json
{
  "status": "healthy",
  "version": "3.0.0",
  "database": "connected"
}
```

### 2. Info de la API
```bash
curl http://localhost:5000/
```

**Respuesta esperada:**
```json
{
  "message": "FitFlow API - Sistema de Gestión para Gimnasios",
  "version": "3.0.0",
  "status": "active",
  "endpoints": {
    "socios": "/api/socios",
    "clases": "/api/clases",
    "reservas": "/api/reservas",
    "pagos": "/api/pagos",
    "planes": "/api/planes",
    "solicitudes": "/api/solicitudes",
    "calendario": "/api/calendario",
    "health": "/health"
  }
}
```

### 3. Abrir en el Navegador
```
http://localhost:5000
```

---

## 📋 Características del Servidor

- **Puerto:** 5000
- **Host:** 0.0.0.0 (accesible desde cualquier interfaz)
- **Servidor:** Waitress (servidor WSGI de producción)
- **Base de Datos:** SQLite en `src/instance/fitflow.db`
- **Logs:** Salida estándar con formato estructurado
- **Scheduler:** APScheduler para tareas asincrónicas
  - Procesamiento de listas de espera: 02:00 AM
  - Actualización de calendario: cada hora en punto

---

## 🛠️ Solución de Problemas

### El servidor no inicia
```bash
# Verificar que el entorno virtual está activado
which python  # Debe mostrar la ruta dentro de venv/

# Verificar que las dependencias están instaladas
pip list | grep Flask
pip list | grep waitress

# Si falta waitress:
pip install waitress
```

### Puerto 5000 ya en uso
```bash
# Opción 1: Cambiar puerto en .env
PORT=5001

# Opción 2: Matar proceso en puerto 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Error de base de datos
```bash
# La carpeta instance debe existir
mkdir -p src/instance

# Verificar ruta en .env (debe ser ruta ABSOLUTA)
DATABASE_URL=sqlite:///C:/ruta/completa/src/instance/fitflow.db
```

---

## 📊 Endpoints Disponibles

### Socios
- `GET /api/socios` - Listar todos los socios
- `POST /api/socios` - Crear nuevo socio
- `GET /api/socios/<id>` - Obtener socio específico
- `PUT /api/socios/<id>` - Actualizar socio
- `DELETE /api/socios/<id>` - Eliminar socio
- `POST /api/socios/import-csv` - Importación masiva

### Clases
- `GET /api/clases` - Listar todas las clases
- `POST /api/clases` - Crear nueva clase
- `GET /api/clases/<id>` - Obtener clase específica
- `PUT /api/clases/<id>` - Actualizar clase
- `DELETE /api/clases/<id>` - Eliminar clase

### Planes de Membresía
- `GET /api/planes` - Listar todos los planes
- `POST /api/planes` - Crear nuevo plan
- `GET /api/planes/<id>` - Obtener plan específico
- `PUT /api/planes/<id>` - Actualizar plan
- `DELETE /api/planes/<id>` - Eliminar plan

### Reservas
- `GET /api/reservas` - Listar todas las reservas
- `POST /api/reservas` - Crear nueva reserva
- `GET /api/reservas/<id>` - Obtener reserva específica
- `DELETE /api/reservas/<id>` - Cancelar reserva

### Solicitudes de Baja
- `GET /api/solicitudes` - Listar todas las solicitudes
- `POST /api/solicitudes` - Crear nueva solicitud
- `GET /api/solicitudes/<id>` - Obtener solicitud específica
- `PUT /api/solicitudes/<id>/aprobar` - Aprobar solicitud
- `PUT /api/solicitudes/<id>/rechazar` - Rechazar solicitud

### Calendario Consolidado
- `GET /api/calendario` - Obtener calendario consolidado
- `GET /api/calendario/actualizar` - Forzar actualización

### Pagos
- `GET /api/pagos` - Listar todos los pagos
- `POST /api/pagos` - Registrar nuevo pago
- `GET /api/pagos/<id>` - Obtener pago específico

---

## 🧪 Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con verbosidad
pytest -v

# Tests de una entrega específica
pytest tests/test_entrega3.py

# Con cobertura
pytest --cov=src --cov-report=term-missing
```

---

## 📚 Documentación Adicional

- **ARQUITECTURA.md** - Arquitectura completa del proyecto
- **README.md** - Documentación principal
- **ENTREGA3.md** - Especificaciones de la Entrega 3
- **ENTREGAS.md** - Resumen de todas las entregas

---

## 💡 Tips

1. **Para desarrollo:** Usa `DEBUG=true` en `.env`
2. **Para producción:** Usa `DEBUG=false` y configura PostgreSQL
3. **Logs:** Los logs se muestran en la consola con formato estructurado
4. **Hot reload:** Desactivado por compatibilidad con APScheduler
5. **Threads:** Waitress usa múltiples threads para manejar requests concurrentes

---

## 🎯 Próximos Pasos

1. ✅ SECRET_KEY generada y configurada
2. ✅ Servidor levantado en http://localhost:5000
3. ✅ Arquitectura documentada en ARQUITECTURA.md
4. 🔄 Probar endpoints con curl o Postman
5. 🔄 Ejecutar tests: `pytest -v`
6. 🔄 Importar socios de ejemplo: `POST /api/socios/import-csv`

---

**Estado:** ✅ SERVIDOR CORRIENDO  
**URL:** http://localhost:5000  
**Puerto:** 5000  
**Fecha:** 10 de noviembre de 2025
