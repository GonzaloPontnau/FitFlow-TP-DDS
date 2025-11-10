"""Servicio Agregador de Horarios"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time
from enum import Enum
from src.services.clase_service import ClaseService
from src.datasources.proxy.clases_externas_proxy import ClasesExternasProxy
from src.models.clase import Clase
from src.models.clase_externa import ClaseExterna
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ModoVisualizacion(Enum):
    """Modos de visualización del calendario"""
    NORMAL = "normal"  # Solo clases con cupo disponible
    OCUPADO = "ocupado"  # Incluye clases sin cupo


class EventoCalendario:
    """Representa un evento del calendario consolidado"""
    
    def __init__(
        self,
        id: Any,
        titulo: str,
        instructor: str,
        fecha: date,
        hora_inicio: time,
        duracion_minutos: int,
        cupo_maximo: int,
        cupos_disponibles: int,
        tipo: str,  # 'interna' o 'externa'
        descripcion: str = "",
        ubicacion: str = "",
        proveedor: str = "",
        url_inscripcion: str = None
    ):
        self.id = id
        self.titulo = titulo
        self.instructor = instructor
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.duracion_minutos = duracion_minutos
        self.cupo_maximo = cupo_maximo
        self.cupos_disponibles = cupos_disponibles
        self.tipo = tipo
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.proveedor = proveedor
        self.url_inscripcion = url_inscripcion
    
    @property
    def tiene_cupo(self) -> bool:
        """Verifica si hay cupo disponible"""
        return self.cupos_disponibles > 0
    
    @property
    def porcentaje_ocupacion(self) -> float:
        """Retorna el porcentaje de ocupación"""
        if self.cupo_maximo == 0:
            return 0.0
        ocupados = self.cupo_maximo - self.cupos_disponibles
        return (ocupados / self.cupo_maximo) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el evento a diccionario para serialización JSON"""
        return {
            'id': str(self.id),
            'titulo': self.titulo,
            'instructor': self.instructor,
            'fecha': self.fecha.isoformat() if isinstance(self.fecha, date) else str(self.fecha),
            'hora_inicio': self.hora_inicio.strftime('%H:%M') if isinstance(self.hora_inicio, time) else str(self.hora_inicio),
            'duracion_minutos': self.duracion_minutos,
            'cupo_maximo': self.cupo_maximo,
            'cupos_disponibles': self.cupos_disponibles,
            'tiene_cupo': self.tiene_cupo,
            'porcentaje_ocupacion': round(self.porcentaje_ocupacion, 2),
            'tipo': self.tipo,
            'descripcion': self.descripcion,
            'ubicacion': self.ubicacion,
            'proveedor': self.proveedor,
            'url_inscripcion': self.url_inscripcion
        }


class AgregadorHorariosService:
    """
    Servicio que consolida horarios de múltiples fuentes.
    
    Combina:
    - Clases internas (fuente dinámica)
    - Talleres externos (fuentes proxy)
    
    Genera una vista única unificada del calendario.
    """
    
    def __init__(self):
        self.clase_service = ClaseService()
        self.clases_externas_proxy = None
        self._ultimo_update = None
        self._cache_eventos = []
        
    def inicializar_proxies(self) -> None:
        """Inicializa las conexiones con fuentes proxy"""
        try:
            # Configuración del proxy de clases externas
            config_clases_externas = {
                'api_key': 'external_api_key',
                'api_url': 'https://api.talleres-especiales.com',
                'proveedor': 'Talleres Especiales S.A.',
                'timeout': 30
            }
            
            self.clases_externas_proxy = ClasesExternasProxy(config_clases_externas)
            self.clases_externas_proxy.conectar()
            logger.info("Proxies de clases externas inicializados correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar proxies: {str(e)}")
            self.clases_externas_proxy = None
    
    def _convertir_clase_interna(self, clase: Clase) -> EventoCalendario:
        """Convierte una clase interna a EventoCalendario"""
        # Obtener fecha de la clase (para simplificar, usamos fecha actual)
        # En producción, las clases tendrían fechas específicas
        fecha = date.today()
        
        return EventoCalendario(
            id=f"interna_{clase.id}",
            titulo=clase.titulo,
            instructor=clase.entrenador.nombre_completo,
            fecha=fecha,
            hora_inicio=clase.horario.hora_inicio,
            duracion_minutos=clase.horario.duracion_minutos(),
            cupo_maximo=clase.cupo_maximo,
            cupos_disponibles=clase.cupos_disponibles(),
            tipo='interna',
            descripcion=clase.descripcion,
            ubicacion="Gimnasio FitFlow",
            proveedor="FitFlow"
        )
    
    def _convertir_clase_externa(self, clase_ext: ClaseExterna) -> EventoCalendario:
        """Convierte una clase externa a EventoCalendario"""
        return EventoCalendario(
            id=f"externa_{clase_ext.id_externo}",
            titulo=clase_ext.titulo,
            instructor=clase_ext.instructor,
            fecha=clase_ext.fecha.date() if isinstance(clase_ext.fecha, datetime) else clase_ext.fecha,
            hora_inicio=clase_ext.hora_inicio,
            duracion_minutos=clase_ext.duracion_minutos,
            cupo_maximo=clase_ext.cupo_maximo,
            cupos_disponibles=clase_ext.cupos_disponibles,
            tipo='externa',
            descripcion=clase_ext.descripcion,
            ubicacion=clase_ext.ubicacion,
            proveedor=clase_ext.proveedor,
            url_inscripcion=clase_ext.url_inscripcion
        )
    
    def obtener_clases_internas(self, solo_con_cupo: bool = False) -> List[EventoCalendario]:
        """
        Obtiene las clases internas del gimnasio.
        
        Args:
            solo_con_cupo: Si True, solo retorna clases con cupo disponible
            
        Returns:
            Lista de eventos de calendario
        """
        try:
            if solo_con_cupo:
                clases = self.clase_service.listar_clases_con_cupo()
            else:
                clases = self.clase_service.listar_clases_activas()
            
            eventos = [self._convertir_clase_interna(clase) for clase in clases]
            logger.info(f"Obtenidas {len(eventos)} clases internas")
            return eventos
        except Exception as e:
            logger.error(f"Error al obtener clases internas: {str(e)}")
            return []
    
    def obtener_clases_externas(self, solo_con_cupo: bool = False) -> List[EventoCalendario]:
        """
        Obtiene las clases externas de proveedores.
        
        Args:
            solo_con_cupo: Si True, solo retorna clases con cupo disponible
            
        Returns:
            Lista de eventos de calendario
        """
        try:
            if not self.clases_externas_proxy:
                self.inicializar_proxies()
            
            if not self.clases_externas_proxy:
                logger.warning("Proxy de clases externas no disponible")
                return []
            
            clases_externas = self.clases_externas_proxy.obtener_clases_disponibles()
            
            eventos = [self._convertir_clase_externa(clase) for clase in clases_externas]
            
            if solo_con_cupo:
                eventos = [e for e in eventos if e.tiene_cupo]
            
            logger.info(f"Obtenidas {len(eventos)} clases externas")
            return eventos
        except Exception as e:
            logger.error(f"Error al obtener clases externas: {str(e)}")
            return []
    
    def obtener_calendario_consolidado(
        self,
        modo: ModoVisualizacion = ModoVisualizacion.NORMAL,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None
    ) -> List[EventoCalendario]:
        """
        Obtiene el calendario consolidado de todas las fuentes.
        
        Args:
            modo: Modo de visualización (NORMAL o OCUPADO)
            fecha_desde: Fecha inicial del rango (opcional)
            fecha_hasta: Fecha final del rango (opcional)
            
        Returns:
            Lista consolidada de eventos ordenados por fecha y hora
        """
        solo_con_cupo = (modo == ModoVisualizacion.NORMAL)
        
        # Obtener eventos de todas las fuentes
        eventos_internos = self.obtener_clases_internas(solo_con_cupo)
        eventos_externos = self.obtener_clases_externas(solo_con_cupo)
        
        # Consolidar todos los eventos
        todos_eventos = eventos_internos + eventos_externos
        
        # Filtrar por rango de fechas si se especifica
        if fecha_desde or fecha_hasta:
            eventos_filtrados = []
            for evento in todos_eventos:
                if fecha_desde and evento.fecha < fecha_desde:
                    continue
                if fecha_hasta and evento.fecha > fecha_hasta:
                    continue
                eventos_filtrados.append(evento)
            todos_eventos = eventos_filtrados
        
        # Ordenar por fecha y hora
        todos_eventos.sort(key=lambda e: (e.fecha, e.hora_inicio))
        
        logger.info(
            f"Calendario consolidado generado: {len(todos_eventos)} eventos "
            f"(modo: {modo.value}, internos: {len(eventos_internos)}, "
            f"externos: {len(eventos_externos)})"
        )
        
        return todos_eventos
    
    def actualizar_calendario(self) -> None:
        """
        Actualiza el calendario consolidado.
        
        Este método debe ser llamado periódicamente (ej. cada hora)
        para mantener el calendario actualizado.
        """
        logger.info("Actualizando calendario consolidado...")
        self._cache_eventos = self.obtener_calendario_consolidado()
        self._ultimo_update = datetime.now()
        logger.info(f"Calendario actualizado: {len(self._cache_eventos)} eventos en cache")
    
    def obtener_estadisticas_calendario(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del calendario consolidado.
        
        Returns:
            Diccionario con estadísticas
        """
        eventos = self.obtener_calendario_consolidado(modo=ModoVisualizacion.OCUPADO)
        
        total_eventos = len(eventos)
        eventos_internos = sum(1 for e in eventos if e.tipo == 'interna')
        eventos_externos = sum(1 for e in eventos if e.tipo == 'externa')
        eventos_con_cupo = sum(1 for e in eventos if e.tiene_cupo)
        eventos_sin_cupo = total_eventos - eventos_con_cupo
        
        total_cupos = sum(e.cupo_maximo for e in eventos)
        cupos_disponibles = sum(e.cupos_disponibles for e in eventos)
        
        return {
            'total_eventos': total_eventos,
            'eventos_internos': eventos_internos,
            'eventos_externos': eventos_externos,
            'eventos_con_cupo': eventos_con_cupo,
            'eventos_sin_cupo': eventos_sin_cupo,
            'total_cupos': total_cupos,
            'cupos_disponibles': cupos_disponibles,
            'cupos_ocupados': total_cupos - cupos_disponibles,
            'porcentaje_ocupacion_global': round(
                ((total_cupos - cupos_disponibles) / total_cupos * 100) if total_cupos > 0 else 0,
                2
            ),
            'ultimo_update': self._ultimo_update.isoformat() if self._ultimo_update else None
        }
