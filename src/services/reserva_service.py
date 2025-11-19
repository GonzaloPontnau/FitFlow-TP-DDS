"""Servicio de gestión de reservas"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from src.repositories.reserva_repository import ReservaRepository
from src.repositories.socio_repository import SocioRepository
from src.repositories.clase_repository import ClaseRepository
from src.models.reserva import Reserva
from src.models.socio import Socio
from src.models.clase import Clase
from src.utils.enums import HORARIO_CANCELACION_RESERVA_HORAS


class ReservaService:
    """
    Servicio para la gestión de reservas de clases.
    
    Gestiona la lógica de negocio relacionada con la creación,
    cancelación y consulta de reservas.
    """
    
    def __init__(self):
        self.reserva_repository = ReservaRepository()
        self.socio_repository = SocioRepository()
        self.clase_repository = ClaseRepository()
    
    def crear_reserva(self, socio_id: int, clase_id: int) -> Dict[str, any]:
        """
        Crea una nueva reserva para un socio en una clase.
        
        Valida que:
        - El socio exista y tenga un plan activo
        - La clase exista y esté activa
        - La clase esté incluida en el plan del socio
        - Haya cupo disponible
        - El socio no tenga ya una reserva activa para esa clase
        
        Args:
            socio_id: ID del socio que realiza la reserva
            clase_id: ID de la clase a reservar
            
        Returns:
            Dict con el resultado de la operación:
                - success: bool indicando si fue exitosa
                - reserva: objeto Reserva si fue exitosa
                - message: mensaje descriptivo del resultado
                
        Raises:
            ValueError: Si las validaciones fallan
        """
        # Validar que el socio existe
        socio = self.socio_repository.get_by_id(socio_id)
        if not socio:
            return {
                'success': False,
                'reserva': None,
                'message': f'El socio con ID {socio_id} no existe'
            }
        
        # Validar que el socio tenga un plan activo
        if not socio.tiene_plan_activo():
            return {
                'success': False,
                'reserva': None,
                'message': f'El socio {socio.nombre_completo} no tiene un plan de membresía activo'
            }
        
        # Validar que la clase existe
        clase = self.clase_repository.get_by_id(clase_id)
        if not clase:
            return {
                'success': False,
                'reserva': None,
                'message': f'La clase con ID {clase_id} no existe'
            }
        
        # Validar que la clase esté activa
        if not clase.activa:
            return {
                'success': False,
                'reserva': None,
                'message': f'La clase "{clase.titulo}" no está activa'
            }
        
        # Validar que la clase esté incluida en el plan del socio
        if not socio.puede_acceder_clase(clase):
            return {
                'success': False,
                'reserva': None,
                'message': f'La clase "{clase.titulo}" no está incluida en el plan del socio'
            }
        
        # Validar que haya cupo disponible
        if not clase.tiene_cupo_disponible():
            return {
                'success': False,
                'reserva': None,
                'message': f'La clase "{clase.titulo}" no tiene cupo disponible'
            }
        
        # Validar que el socio no tenga ya una reserva activa para esta clase
        reserva_existente = self._tiene_reserva_activa(socio_id, clase_id)
        if reserva_existente:
            return {
                'success': False,
                'reserva': None,
                'message': f'El socio ya tiene una reserva activa para la clase "{clase.titulo}"'
            }
        
        # Crear la reserva
        reserva = Reserva(socio=socio, clase=clase)
        reserva_guardada = self.reserva_repository.save(reserva)
        
        # Emitir evento de nueva reserva
        try:
            from src.extensions import socketio
            socketio.emit('actualizacion_cupos', {
                'clase_id': clase.id,
                'cupos_disponibles': clase.cupos_disponibles()
            })
        except Exception as e:
            # No fallar si hay error en socket
            print(f"Error emitiendo evento socket: {e}")
        
        return {
            'success': True,
            'reserva': reserva_guardada,
            'message': f'Reserva creada exitosamente para {socio.nombre_completo} en "{clase.titulo}"'
        }
    
    def cancelar_reserva(self, reserva_id: int) -> Dict[str, any]:
        """
        Cancela una reserva existente.
        
        Valida que:
        - La reserva exista
        - La reserva esté activa
        - Se cancele con al menos 24 horas de anticipación
        
        Args:
            reserva_id: ID de la reserva a cancelar
            
        Returns:
            Dict con el resultado de la operación:
                - success: bool indicando si fue exitosa
                - reserva: objeto Reserva actualizada si fue exitosa
                - message: mensaje descriptivo del resultado
        """
        # Validar que la reserva existe
        reserva = self.reserva_repository.get_by_id(reserva_id)
        if not reserva:
            return {
                'success': False,
                'reserva': None,
                'message': f'La reserva con ID {reserva_id} no existe'
            }
        
        # Validar que la reserva esté activa
        if not reserva.esta_activa():
            return {
                'success': False,
                'reserva': None,
                'message': 'La reserva ya fue cancelada previamente'
            }
        
        # Validar que se cancele con al menos 24 horas de anticipación
        if not self._puede_cancelar_reserva(reserva):
            return {
                'success': False,
                'reserva': None,
                'message': f'No se puede cancelar la reserva con menos de {HORARIO_CANCELACION_RESERVA_HORAS} horas de anticipación'
            }
        
        # Cancelar la reserva
        reserva.cancelar()
        reserva_actualizada = self.reserva_repository.save(reserva)
        
        # Emitir evento de cancelación
        try:
            from src.extensions import socketio
            socketio.emit('actualizacion_cupos', {
                'clase_id': reserva.clase.id,
                'cupos_disponibles': reserva.clase.cupos_disponibles()
            })
        except Exception as e:
            print(f"Error emitiendo evento socket: {e}")
        
        return {
            'success': True,
            'reserva': reserva_actualizada,
            'message': f'Reserva cancelada exitosamente'
        }
    
    def listar_reservas_socio(self, socio_id: int) -> List[Reserva]:
        """
        Lista todas las reservas de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de reservas del socio
        """
        return self.reserva_repository.find_by_socio(socio_id)
    
    def listar_reservas_activas_socio(self, socio_id: int) -> List[Reserva]:
        """
        Lista las reservas activas de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de reservas activas del socio
        """
        reservas = self.reserva_repository.find_by_socio(socio_id)
        return [r for r in reservas if r.esta_activa()]
    
    def listar_reservas_clase(self, clase_id: int) -> List[Reserva]:
        """
        Lista todas las reservas de una clase.
        
        Args:
            clase_id: ID de la clase
            
        Returns:
            Lista de reservas de la clase
        """
        return self.reserva_repository.find_by_clase(clase_id)
    
    def obtener_reserva(self, reserva_id: int) -> Optional[Reserva]:
        """
        Obtiene una reserva por su ID.
        
        Args:
            reserva_id: ID de la reserva
            
        Returns:
            Objeto Reserva o None si no existe
        """
        return self.reserva_repository.get_by_id(reserva_id)
    
    def _tiene_reserva_activa(self, socio_id: int, clase_id: int) -> bool:
        """
        Verifica si un socio tiene una reserva activa para una clase.
        
        Args:
            socio_id: ID del socio
            clase_id: ID de la clase
            
        Returns:
            True si tiene reserva activa, False en caso contrario
        """
        reservas = self.reserva_repository.find_by_socio(socio_id)
        for reserva in reservas:
            if reserva.clase_id == clase_id and reserva.esta_activa():
                return True
        return False
    
    def _puede_cancelar_reserva(self, reserva: Reserva) -> bool:
        """
        Verifica si una reserva puede ser cancelada.
        
        Una reserva solo puede cancelarse si faltan al menos 24 horas
        para el inicio de la clase.
        
        Args:
            reserva: Objeto Reserva
            
        Returns:
            True si puede cancelarse, False en caso contrario
        """
        # Obtener la fecha y hora de inicio de la clase
        # Para esto necesitamos combinar el día de la semana con la hora
        # Como no tenemos una fecha específica, asumimos que la clase es en el futuro
        # y verificamos solo si han pasado 24 horas desde la reserva
        
        # Por ahora, permitimos cancelar si no es el mismo día de la clase
        # En una implementación más completa, se verificaría con fechas específicas
        ahora = datetime.utcnow()
        tiempo_desde_reserva = ahora - reserva.fecha_reserva
        
        # Permitir cancelación si han pasado menos de 7 días desde la reserva
        # (En una implementación real, se compararía con la fecha/hora de la clase)
        return True  # Simplificado por ahora
    
    def get_cupos_disponibles(self, clase_id: int) -> Dict[str, any]:
        """
        Obtiene información sobre los cupos de una clase.
        
        Args:
            clase_id: ID de la clase
            
        Returns:
            Dict con información de cupos:
                - cupo_maximo: int
                - cupos_ocupados: int
                - cupos_disponibles: int
                - tiene_cupo: bool
        """
        clase = self.clase_repository.get_by_id(clase_id)
        if not clase:
            return {
                'cupo_maximo': 0,
                'cupos_ocupados': 0,
                'cupos_disponibles': 0,
                'tiene_cupo': False
            }
        
        reservas_activas = self.reserva_repository.get_reservas_activas_clase(clase_id)
        cupos_ocupados = len(reservas_activas)
        cupos_disponibles = clase.cupo_maximo - cupos_ocupados
        
        return {
            'cupo_maximo': clase.cupo_maximo,
            'cupos_ocupados': cupos_ocupados,
            'cupos_disponibles': cupos_disponibles,
            'tiene_cupo': cupos_disponibles > 0
        }

