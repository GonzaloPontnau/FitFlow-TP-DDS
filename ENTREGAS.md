# FitFlow - Plan de Entregas 2025

Sistema de Gestión Integral para Gimnasios - Trabajo Práctico Anual Integrador

---

##  ENTREGA 1: Arquitectura y Modelado en Objetos - Parte I

### Objetivos
- Entrar en contacto con el dominio y sus principales abstracciones (Socio, Clase, Plan)
- Incorporar conceptos y principios de Diseño Orientado a Objetos
- Familiarizarse con el entorno de desarrollo y la arquitectura del sistema

### Alcance
- ✅ **Fuentes estáticas:** Carga masiva de socios
- ✅ **Planes de Membresía**
- ✅ **Clases:** Listado y filtrado por plan y horario
- ✅ **Roles:** Administrador y Socio (en modo visualizador)
- ✅ **Solicitudes de baja de membresía**

### Funcionalidades a Implementar

#### 1. Fuentes Estáticas
- Lectura de archivos CSV para carga masiva de socios
- Formato: "Nombre", "Apellido", "DNI", "Email", "ID Plan Membresía"
- Detección de duplicados por DNI (actualizar datos del existente)

#### 2. Planes de Membresía
- Título, descripción y precio
- Administradores pueden crear múltiples planes
- Asociación de clases a planes

#### 3. Gestión de Clases
- Título, descripción, entrenador, horario y cupo máximo
- Asociación a uno o más Planes de Membresía
- Visibilidad según plan del socio

#### 4. Roles de Usuario
- **Visualizador:** Persona no registrada que puede ver horarios
- **Administrador:** Gestiona planes y clases
- **Socio Registrado:** Accede a su perfil y funcionalidades completas

#### 5. Solicitudes de Baja
- Solicitud con texto justificado (mínimo 150 caracteres)
- Estado pendiente hasta aprobación del administrador
- Aprobación/rechazo por administrador

### Requerimientos
1. ✅ Como **administrador**, deseo crear un Plan de Membresía
2. ✅ Como **administrador**, deseo importar socios desde un archivo CSV
3. ✅ Como **socio visualizador**, deseo navegar todas las clases disponibles de un Plan
4. ✅ Como **socio visualizador**, deseo filtrar las clases por horario o día
5. ✅ Como **socio registrado**, deseo poder solicitar la baja de mi membresía
6. ✅ Como **administrador**, deseo poder aceptar o rechazar una solicitud de baja

---

##  ENTREGA 2: Arquitectura y Modelado en Objetos - Parte II

### Objetivos
- Diseñar e implementar nuevas funcionalidades de forma incremental
- Incorporar nociones de ejecuciones de tareas asincrónicas
- Familiarizarse con la integración de servicios externos a través de APIs

### Alcance
- ✅ **Fuentes dinámicas:** Gestión de reservas a clases
- ✅ **Fuentes proxy:** Integración con sistemas externos
- ✅ **Rechazo automático de solicitudes de baja incompletas**

### Funcionalidades a Implementar

#### 1. Gestión de Reservas (Fuentes Dinámicas)
- Socios registrados pueden realizar reservas en clases de su plan
- Cancelación de reservas hasta 24 horas antes del inicio
- Validación de cupos disponibles
- Restricción: socios no registrados solo pueden visualizar

#### 2. Integración con Pasarela de Pagos (Fuente Proxy)
- Componente Fuente Proxy para pasarela de pagos
- Verificación diaria del estado de pagos de membresías
- Actualización automática del estado de pago de socios

#### 3. Integración con Clases Externas (Fuente Proxy)
- Consumo de API REST de empresa de talleres especiales
- Integración en tiempo real
- Visualización de talleres externos en calendario general

#### 4. Validación Automática de Solicitudes
- Validador de texto para solicitudes de baja
- Rechazo automático si no cumple criterios mínimos
- Criterios: longitud mínima, palabras clave, etc.

### Requerimientos
1. ✅ Como **socio registrado**, deseo poder reservar un cupo en una clase de mi plan
2. ✅ Como **administrador**, quiero que el sistema actualice el estado de pago de los socios diariamente
3. ✅ Como **socio**, quiero ver en el calendario los talleres especiales externos en tiempo real
4. ✅ El sistema debe rechazar automáticamente solicitudes de baja con justificación inválida

---

##  ENTREGA 3: Integración y Modelado en Objetos - Parte III

### Objetivos
- Exponer un servicio propio a través de un protocolo de red (API REST)
- Incorporar flujos de trabajo asincrónicos para tareas pesadas
- Modelar un servicio agregador

### Alcance
- **Servicio Agregador de Horarios**
- **Gestión de Cupos y Listas de Espera**
- **Exposición de una API REST propia**

### Funcionalidades a Implementar

#### 1. Servicio de Agregación de Horarios
- Consolidar horarios de clases propias (fuente dinámica)
- Consolidar talleres externos (fuentes proxy)
- Actualización automática cada hora del calendario consolidado
- Vista única unificada

#### 2. Modos de Visualización del Calendario
- **Modo Normal:** Mostrar solo clases con cupo disponible
- **Modo Ocupado:** Mostrar también clases sin cupo

#### 3. Gestión de Listas de Espera
- Configuración de lista de espera al crear una clase
- Inscripción en lista de espera cuando no hay cupo
- Notificación automática al liberarse un lugar
- Tiempo limitado para confirmar lugar
- Proceso asincrónico en horarios de baja carga (noche)

#### 4. API REST
**API Administrativa:**
- CRUD completo sobre Clases y Planes
- Agregar/quitar clases de un plan
- Aprobar/denegar solicitudes de baja

**API Pública para Socios:**
- Consulta de clases dentro de un plan
- Generar reserva para una clase
- Navegación filtrada sobre el calendario

### Requerimientos
1. Como **socio**, deseo elegir si ver todas las clases o solo las con cupo
2. Como **administrador**, quiero asociar una lista de espera a una clase
3. Como **administrador**, quiero modificar las clases incluidas en un plan
4. El sistema debe permitir operaciones a través de endpoints REST

---

##  ENTREGA 4: Persistencia

### Objetivos
- Incorporar persistencia de datos en un motor de base de datos relacional usando ORM
- Incorporar nociones de desnormalización para optimizar consultas
- Desarrollar un servicio de estadísticas

### Alcance
- **Persistencia del modelo de objetos**
- **Soporte para contenido multimedia en clases**
- **Exportación de datos en formato CSV**
- **Servicio de Estadísticas**

### Funcionalidades a Implementar

#### 1. Persistencia con ORM
- Mapeo de todas las entidades del modelo
- Socio, Clase, Plan, Reserva, Pago, etc.
- Relaciones entre entidades
- Optimización de consultas

#### 2. Servicio de Estadísticas
Generar periódicamente estadísticas para responder:
- ¿En qué franja horaria se concentra la mayor cantidad de reservas?
- ¿Cuál es la clase con mayor cantidad de inscriptos históricamente?
- ¿Qué plan de membresía genera más ingresos?
- ¿Cuál es la tasa de presentismo promedio en las clases?

#### 3. Contenido Multimedia
- Asociar videos a clases (demostrativos de ejercicios)
- Asociar imágenes a clases
- Gestión por administradores y entrenadores

#### 4. Exportación de Datos
- Exportar reportes de asistencia a CSV
- Formato estandarizado
- Disponible para administradores

### Requerimientos
1. Persistir todas las entidades del modelo utilizando ORM
2. Implementar el servicio de estadísticas
3. Como **administrador**, deseo agregar una imagen o video a una clase
4. Como **administrador**, deseo exportar un reporte de asistencia en CSV

---

##  ENTREGA 5: Arquitectura Web MVC y Maquetado de UI

### Objetivos
- Incorporar nociones de Diseño UI/UX y maquetado Web (HTML5/CSS)
- Implementar un Cliente Liviano (Server-Side Rendering)

### Alcance
- **Diseño y maquetado de interfaces de usuario**
- **Implementación de un Cliente Liviano**

### Funcionalidades a Implementar

#### 1. Interfaz de Usuario para Socios
- Calendario de clases en vista semanal
- Calendario de clases en vista mensual
- Navegación intuitiva y responsiva
- Visualización de cupos disponibles

#### 2. Panel de Administración
- Sistema de inicio de sesión
- Panel de control centralizado
- Gestión de planes desde la interfaz
- Gestión de clases desde la interfaz
- Interfaz para aprobar/rechazar solicitudes de baja

#### 3. Diseño UI/UX
- Interfaz moderna y atractiva
- Experiencia de usuario optimizada
- Responsive design (móvil, tablet, desktop)
- Accesibilidad

### Requerimientos
1. Como **socio**, deseo visualizar el calendario en vista semanal/mensual
2. Como **administrador**, deseo iniciar sesión en un panel de control
3. Como **administrador**, deseo configurar planes y clases desde mi panel
4. Como **administrador**, deseo aprobar/rechazar solicitudes desde la interfaz

---

##  ENTREGA 6: Despliegue, Observabilidad y Seguridad

### Objetivos
- Familiarizarse con técnicas de despliegue en la nube
- Incorporar herramientas de monitoreo, observabilidad y seguridad

### Alcance
- **Sistema desplegado en la nube**
- **Herramientas de observabilidad y monitoreo**
- **Implementar medidas de seguridad**

### Funcionalidades a Implementar

#### 1. Despliegue en la Nube
- Configuración de infraestructura cloud
- Sistema accesible públicamente
- Alta disponibilidad
- Escalabilidad

#### 2. Observabilidad
- Logs centralizados
- Métricas de rendimiento
- Trazabilidad de requests
- Dashboards de monitoreo

#### 3. Monitoreo y Supervisión
- Health checks automáticos
- Reinicio automático ante caídas
- Alertas de incidentes
- Métricas de uptime

#### 4. Medidas de Seguridad
- **Rate Limiting:** Protección de API de reservas contra abusos
- **Bloqueo de IPs:** Sistema de blacklist
- Autenticación y autorización robusta
- Protección contra ataques comunes (SQL Injection, XSS, CSRF)

#### 5. Actualizaciones en Tiempo Real
- Implementación de WebSockets
- Actualización de cupos en tiempo real
- Sin necesidad de recargar la página
- Experiencia de usuario mejorada

### Requerimientos
1. Desplegar el sistema en la nube con acceso público
2. Incorporar herramientas de **observabilidad** (logs, métricas)
3. Incorporar herramientas de **monitoreo** (reinicio automático)
4. Implementar **Rate Limiting** para proteger la API
5. Incorporar sistema de **Bloqueo de IPs**
6. Implementar **WebSockets** para actualizaciones en tiempo real del calendario

---

## 📊 Resumen de Estado

| Entrega | Estado | Progreso |
|---------|--------|----------|
| Entrega 1 | ✅ Completada | 100% |
| Entrega 2 | ✅ Completada | 100% |
| Entrega 3 | 🔄 En Progreso | 0% |
| Entrega 4 | ⏳ Pendiente | 0% |
| Entrega 5 | ⏳ Pendiente | 0% |
| Entrega 6 | ⏳ Pendiente | 0% |

---

## 🎯 Tecnologías por Entrega

### Entrega 1 y 2
- Python 3.10+
- Flask
- SQLAlchemy (ORM)
- SQLite (desarrollo)
- Pandas (CSV)
- Pytest (testing)

### Entrega 3
- Flask REST API
- JSON serialización
- Tareas asincrónicas (Celery/APScheduler)

### Entrega 4
- PostgreSQL (producción)
- Migraciones de base de datos
- Almacenamiento de archivos multimedia
- Generación de CSV

### Entrega 5
- HTML5/CSS3
- JavaScript
- Jinja2 Templates
- Bootstrap/Tailwind CSS

### Entrega 6
- Docker
- Cloud Provider (AWS/GCP/Azure)
- Prometheus/Grafana (monitoreo)
- ELK Stack o similar (logs)
- WebSockets
- Nginx/Redis (rate limiting)

---

*Última actualización: Noviembre 2025*

