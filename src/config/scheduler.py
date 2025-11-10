"""Configuración de tareas asincrónicas programadas"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class TaskScheduler:
    """Programador de tareas asincrónicas del sistema"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._jobs = {}
    
    def iniciar(self):
        """Inicia el programador de tareas"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler de tareas iniciado")
    
    def detener(self):
        """Detiene el programador de tareas"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler de tareas detenido")
    
    def agregar_tarea_nocturna(self, func, hora: int = 2, minuto: int = 0, job_id: str = None):
        """
        Agrega una tarea para ejecutarse diariamente en horario nocturno.
        
        Args:
            func: Función a ejecutar
            hora: Hora de ejecución (0-23, default: 2am)
            minuto: Minuto de ejecución (default: 0)
            job_id: Identificador único del job
        """
        trigger = CronTrigger(hour=hora, minute=minuto)
        job = self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            max_instances=1
        )
        self._jobs[job_id] = job
        logger.info(f"Tarea nocturna programada: {job_id} a las {hora:02d}:{minuto:02d}")
        return job
    
    def agregar_tarea_horaria(self, func, minuto: int = 0, job_id: str = None):
        """
        Agrega una tarea para ejecutarse cada hora.
        
        Args:
            func: Función a ejecutar
            minuto: Minuto de la hora en que ejecutar (default: 0)
            job_id: Identificador único del job
        """
        trigger = CronTrigger(minute=minuto)
        job = self.scheduler.add_job(
            func=func,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            max_instances=1
        )
        self._jobs[job_id] = job
        logger.info(f"Tarea horaria programada: {job_id} en el minuto {minuto}")
        return job
    
    def agregar_tarea_intervalo(self, func, minutos: int, job_id: str = None):
        """
        Agrega una tarea para ejecutarse cada N minutos.
        
        Args:
            func: Función a ejecutar
            minutos: Intervalo en minutos
            job_id: Identificador único del job
        """
        job = self.scheduler.add_job(
            func=func,
            trigger='interval',
            minutes=minutos,
            id=job_id,
            replace_existing=True,
            max_instances=1
        )
        self._jobs[job_id] = job
        logger.info(f"Tarea con intervalo programada: {job_id} cada {minutos} minutos")
        return job
    
    def ejecutar_ahora(self, job_id: str):
        """Ejecuta inmediatamente una tarea programada"""
        job = self._jobs.get(job_id)
        if job:
            job.modify(next_run_time=datetime.now())
            logger.info(f"Tarea {job_id} ejecutándose inmediatamente")
        else:
            logger.warning(f"Tarea {job_id} no encontrada")
    
    def listar_tareas(self):
        """Lista todas las tareas programadas"""
        jobs = self.scheduler.get_jobs()
        return [{
            'id': job.id,
            'name': job.name,
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger)
        } for job in jobs]


# Instancia global del scheduler
scheduler = TaskScheduler()


def configurar_tareas_programadas(app):
    """
    Configura todas las tareas programadas del sistema.
    
    Args:
        app: Aplicación Flask
    """
    from src.services.lista_espera_service import ListaEsperaService
    from src.services.agregador_horarios_service import AgregadorHorariosService
    
    # Crear servicios con contexto de aplicación
    def procesar_lista_espera_nocturna():
        """Procesa liberaciones de cupos desde lista de espera (tarea nocturna)"""
        with app.app_context():
            try:
                logger.info("Iniciando procesamiento nocturno de lista de espera...")
                service = ListaEsperaService()
                notificaciones = service.procesar_liberaciones_cupos()
                logger.info(
                    f"Procesamiento nocturno completado: {notificaciones} notificaciones"
                )
            except Exception as e:
                logger.error(f"Error en procesamiento nocturno de lista de espera: {e}")
    
    def actualizar_calendario_horario():
        """Actualiza el calendario consolidado (tarea horaria)"""
        with app.app_context():
            try:
                logger.info("Actualizando calendario consolidado...")
                service = AgregadorHorariosService()
                service.actualizar_calendario()
                logger.info("Calendario consolidado actualizado")
            except Exception as e:
                logger.error(f"Error actualizando calendario: {e}")
    
    # Programar tareas
    # Procesamiento de lista de espera: 2:00 AM todos los días
    scheduler.agregar_tarea_nocturna(
        func=procesar_lista_espera_nocturna,
        hora=2,
        minuto=0,
        job_id='procesar_lista_espera'
    )
    
    # Actualización de calendario: cada hora en punto
    scheduler.agregar_tarea_horaria(
        func=actualizar_calendario_horario,
        minuto=0,
        job_id='actualizar_calendario'
    )
    
    # Iniciar scheduler
    scheduler.iniciar()
    
    logger.info("Tareas asincrónicas programadas correctamente")
    
    return scheduler
