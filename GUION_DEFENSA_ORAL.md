# Guión para Defensa Oral - FitFlow

## Trabajo Práctico Anual - Diseño de Sistemas de Software I (2025)

---

## INTRODUCCIÓN (2-3 minutos)

### Presentación del Sistema

> "Buenas tardes. Voy a presentar **FitFlow**, un sistema de gestión integral para gimnasios desarrollado como trabajo práctico de la materia.
>
> FitFlow está diseñado para centralizar todas las operaciones de un gimnasio: desde la gestión de socios y membresías, hasta la administración de clases, reservas, pagos y estadísticas.
>
> El sistema está pensado como **código abierto**, lo que permite que diferentes gimnasios o franquicias puedan instalarlo en sus propios servidores."

### Contexto del Problema

> "El problema que resuelve FitFlow es la fragmentación de información típica de los gimnasios:
> - Horarios de clases dispersos
> - Inscripciones manuales
> - Falta de visibilidad de ocupación en tiempo real
> - Dificultad para gestionar membresías y pagos
>
> Nuestro sistema centraliza todo esto en una única plataforma."

---

## ENTREGA 1: DOMINIO BASE (5-7 minutos)

*[Mostrar diagrama de clases o página principal]*

### Modelado del Dominio

> "En la primera entrega nos enfocamos en modelar las **abstracciones principales** del dominio:
>
> - **Socio**: Representa a una persona inscripta en el gimnasio, con sus datos personales y el plan de membresía asociado
> - **Plan de Membresía**: Define qué clases puede tomar un socio y a qué precio (ej: Plan Básico, Plan Premium)
> - **Clase**: Actividad grupal con entrenador, horario y cupo máximo
> - **Entrenador**: Profesional que dicta las clases
> - **Horario**: Día de la semana y franja horaria"

### Carga de Socios desde CSV

*[Mostrar ejemplo de archivo CSV o la funcionalidad de importación]*

> "Implementamos una **fuente estática** para la carga inicial de datos. El sistema puede importar socios desde archivos CSV, lo cual es útil para migrar datos de otros sistemas.
>
> Si un socio con el mismo DNI ya existe, el sistema actualiza sus datos en lugar de duplicarlo."

### Sistema de Roles

> "Definimos tres tipos de usuarios:
> - **Visualizador**: Cualquier persona que consulta horarios sin registrarse
> - **Socio Registrado**: Puede hacer reservas y gestionar su membresía
> - **Administrador**: Gestiona planes, clases y aprueba solicitudes"

### Solicitudes de Baja

> "Un socio puede solicitar la baja de su membresía. La solicitud requiere una **justificación de al menos 150 caracteres** y queda pendiente de aprobación por un administrador."

---

## ENTREGA 2: INTEGRACIONES (5-7 minutos)

*[Mostrar diagrama de arquitectura con proxies]*

### Gestión de Reservas

> "En la segunda entrega implementamos el **sistema de reservas**. Un socio registrado puede:
> - Reservar un cupo en cualquier clase de su plan
> - Cancelar la reserva hasta **24 horas antes** del inicio de la clase
> - El sistema valida automáticamente que haya cupo disponible"

### Integración con Pasarela de Pagos

> "Diseñamos un componente **Proxy** que se integra con una pasarela de pagos externa. Este proxy:
> - Verifica el estado de los pagos de membresías
> - Puede ejecutarse diariamente para actualizar estados
> - Está preparado para conectarse a pasarelas reales como MercadoPago o Stripe"

### Integración con Clases Externas

> "El gimnasio tiene convenios con empresas que dictan talleres especiales. Implementamos otro **Proxy** que:
> - Consume una API REST externa en tiempo real
> - Integra los talleres de terceros en el calendario general
> - Permite a los socios ver toda la oferta unificada"

### Rechazo Automático con Patrón Strategy

> "Para las solicitudes de baja, implementamos el **patrón Strategy** con validadores intercambiables:
> - **Validador de Longitud Mínima**: Verifica los 150 caracteres
> - **Validador de Palabras Vacías**: Detecta texto sin contenido significativo
> - **Validador Compuesto**: Combina múltiples validadores
>
> Si la solicitud no cumple los criterios, se rechaza automáticamente sin intervención de un administrador."

---

## ENTREGA 3: AGREGADOR Y API REST (5-7 minutos)

*[Mostrar el calendario consolidado o el endpoint de la API]*

### Servicio Agregador de Horarios

> "Desarrollamos un **servicio de agregación** que consolida información de múltiples fuentes:
> - Clases propias del gimnasio (fuente dinámica)
> - Talleres de proveedores externos (fuentes proxy)
>
> El resultado es un **calendario unificado** que se actualiza cada hora."

### Modos de Visualización

> "El calendario soporta dos modos:
> - **Modo Normal**: Muestra solo las clases con cupo disponible
> - **Modo Ocupado**: Muestra todas las clases, incluso las completas
>
> Esto permite a los socios elegir cómo quieren ver la información."

### Sistema de Lista de Espera

> "Cuando una clase está llena, los socios pueden inscribirse en una **lista de espera**:
> - Si se libera un lugar, el primer socio en la lista es notificado
> - Tiene un tiempo límite para confirmar su lugar
> - El procesamiento se ejecuta en horarios de baja carga (de noche)"

### API REST

> "Expusimos todas las operaciones a través de una **API REST**:
> - Endpoints administrativos: CRUD de clases y planes, gestión de solicitudes
> - Endpoints públicos: consulta de clases, creación de reservas, navegación del calendario
>
> Esto permite que otras aplicaciones puedan integrarse con FitFlow."

---

## ENTREGA 4: PERSISTENCIA Y ESTADÍSTICAS (5-7 minutos)

*[Mostrar el dashboard de estadísticas]*

### Persistencia con ORM

> "Implementamos la persistencia de datos utilizando **SQLAlchemy** como ORM:
> - Todas las entidades se mapean a tablas en la base de datos
> - Usamos SQLite para desarrollo y PostgreSQL para producción
> - El patrón Repository abstrae el acceso a datos"

### Contenido Multimedia

> "Las clases ahora pueden tener contenido multimedia asociado:
> - Una **imagen** representativa
> - Un **video demostrativo** de los ejercicios
>
> Esto mejora la experiencia del socio al elegir clases."

### Servicio de Estadísticas

> "Desarrollamos un dashboard con métricas clave:
> - **¿En qué franja horaria hay más reservas?**
> - **¿Cuál es la clase más popular?**
> - **¿Qué plan genera más ingresos?**
> - **¿Cuál es la tasa de presentismo?**
>
> Estas estadísticas ayudan a los administradores a tomar decisiones."

### Exportación de Reportes

> "Los administradores pueden **exportar reportes de asistencia a CSV**, lo cual es útil para análisis externos o reportes a la gerencia."

---

## ENTREGA 5: INTERFAZ WEB (3-5 minutos)

*[Navegar por las diferentes páginas de la aplicación]*

### Cliente Liviano (MVC)

> "Implementamos una interfaz web utilizando Server-Side Rendering con Flask y templates Jinja2:
> 
> - **Página Principal**: Vista general del gimnasio
> - **Calendario**: Vista semanal/mensual de todas las clases
> - **Reservas**: Los socios pueden hacer y gestionar sus reservas
> - **Panel Administrativo**: Gestión de clases, planes y solicitudes"

### Experiencia de Usuario

> "El diseño se enfoca en la usabilidad:
> - Navegación clara entre secciones
> - Formularios validados del lado del cliente y servidor
> - Feedback visual sobre el estado de las operaciones"

---

## ENTREGA 6: DESPLIEGUE Y SEGURIDAD (5-7 minutos)

*[Mostrar el health check o el docker-compose]*

### WebSockets para Tiempo Real

> "Implementamos **WebSockets** para que los socios vean actualizaciones de cupos en tiempo real:
> - Cuando alguien reserva o cancela, todos los usuarios conectados ven el cambio
> - No es necesario recargar la página
> - Usamos Flask-SocketIO para la implementación"

### Rate Limiting

> "Para proteger la API de abusos, implementamos **Rate Limiting**:
> - El endpoint /api tiene un límite de 10 requests por minuto
> - Si se excede, el sistema responde con error 429
> - Configurable según las necesidades"

### Bloqueo de IPs

> "El sistema permite bloquear IPs maliciosas:
> - Se configura mediante variables de entorno
> - Las IPs bloqueadas reciben error 403
> - Protege contra ataques de fuerza bruta"

### Sistema de Logging

> "Implementamos un sistema de **observabilidad**:
> - Logs en consola con colores para desarrollo
> - Archivos de log rotados por día
> - Archivo separado para errores críticos
> - Esto facilita el debugging y auditoría"

### Health Check

> "El endpoint `/health` permite verificar el estado del sistema:
> - Verificación de conectividad a la base de datos
> - Estado del scheduler de tareas
> - Tiempo de respuesta del servicio
> - Útil para servicios de monitoreo externo"

### Preparación para Despliegue

> "Creamos toda la configuración necesaria para despliegue en la nube:
> - **Dockerfile**: Para containerización con Gunicorn
> - **docker-compose.yml**: Orquestación con persistencia
> - **Procfile**: Para plataformas como Render o Railway
> - **render.yaml**: Blueprint para deploy con un click"

---

## CONCLUSIÓN (2-3 minutos)

### Resumen de Patrones Utilizados

> "A lo largo del proyecto aplicamos varios patrones de diseño:
> - **Repository**: Abstracción del acceso a datos
> - **Service Layer**: Lógica de negocio centralizada
> - **Strategy**: Validadores intercambiables
> - **Proxy**: Integración con servicios externos
> - **Application Factory**: Configuración flexible de Flask"

### Aprendizajes

> "El desarrollo de FitFlow nos permitió:
> - Aplicar conceptos de diseño orientado a objetos en un sistema real
> - Integrar múltiples fuentes de datos
> - Implementar una arquitectura en capas mantenible
> - Preparar una aplicación para despliegue en producción"

### Demostración Final

> "El sistema está completamente funcional y listo para desplegarse en la nube. ¿Tienen alguna pregunta?"

---

## POSIBLES PREGUNTAS Y RESPUESTAS

### ¿Por qué eligieron el patrón Strategy para los validadores?

> "Porque permite agregar nuevos criterios de validación sin modificar el código existente. Si mañana queremos agregar un validador que detecte spam, simplemente creamos una nueva clase que implemente la interfaz y la agregamos al validador compuesto."

### ¿Cómo manejan la concurrencia en las reservas?

> "SQLAlchemy maneja las transacciones de base de datos. Si dos usuarios intentan reservar el último cupo simultáneamente, la base de datos asegura que solo uno tenga éxito."

### ¿Por qué usaron SQLite en lugar de PostgreSQL?

> "SQLite es ideal para desarrollo porque no requiere instalación. La aplicación está preparada para usar PostgreSQL en producción simplemente cambiando la variable de entorno DATABASE_URL."

### ¿Cómo funciona el Agregador de Horarios?

> "El agregador consulta la base de datos local para las clases internas y los proxies para las clases externas. Combina toda la información, la ordena por fecha y hora, y aplica los filtros según el modo de visualización seleccionado."

### ¿Qué pasa si el servicio externo de pagos no está disponible?

> "El Proxy maneja los errores gracefully. Si el servicio no responde, se loguea el error y el sistema continúa funcionando. Los pagos quedan marcados como 'pendiente de verificación' para reintentar después."

---

**Tiempo total estimado: 30-40 minutos**
