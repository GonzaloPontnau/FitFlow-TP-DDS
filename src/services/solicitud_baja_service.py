"""Servicio de gestión de Solicitudes de Baja"""
from typing import List
from src.repositories.solicitud_baja_repository import SolicitudBajaRepository
from src.repositories.socio_repository import SocioRepository
from src.models.solicitud_baja import SolicitudBaja
from src.utils.enums import LONGITUD_MINIMA_SOLICITUD_BAJA


class SolicitudBajaService:
    """Servicio para operaciones de negocio relacionadas con Solicitudes de Baja"""
    
    def __init__(self):
        self.solicitud_repo = SolicitudBajaRepository()
        self.socio_repo = SocioRepository()
    
    def crear_solicitud(self, socio_id: int, justificacion: str) -> SolicitudBaja:
        """
        Crea una nueva solicitud de baja.
        
        Args:
            socio_id: ID del socio que solicita la baja
            justificacion: Texto justificando la solicitud
            
        Returns:
            La solicitud creada
            
        Raises:
            ValueError: Si el socio no existe, ya tiene una solicitud pendiente,
                       o la justificación no es válida
        """
        # Verificar que el socio existe
        socio = self.socio_repo.get_by_id(socio_id)
        if not socio:
            raise ValueError(f"Socio con ID {socio_id} no existe")
        
        # Verificar que no tenga una solicitud pendiente
        if self.solicitud_repo.tiene_solicitud_pendiente(socio_id):
            raise ValueError("El socio ya tiene una solicitud de baja pendiente")
        
        # Validar justificación
        if len(justificacion.strip()) < LONGITUD_MINIMA_SOLICITUD_BAJA:
            raise ValueError(
                f"La justificación debe tener al menos "
                f"{LONGITUD_MINIMA_SOLICITUD_BAJA} caracteres"
            )
        
        # Crear la solicitud
        nueva_solicitud = SolicitudBaja(
            socio=socio,
            justificacion=justificacion
        )
        
        # Actualizar estado del socio
        socio.solicitar_baja()
        self.socio_repo.update(socio)
        
        return self.solicitud_repo.create(nueva_solicitud)
    
    def listar_solicitudes_pendientes(self) -> List[SolicitudBaja]:
        """Lista todas las solicitudes pendientes de aprobación"""
        return self.solicitud_repo.get_pendientes()
    
    def obtener_solicitud(self, solicitud_id: int) -> SolicitudBaja:
        """
        Obtiene una solicitud por su ID.
        
        Args:
            solicitud_id: ID de la solicitud
            
        Returns:
            La solicitud encontrada
            
        Raises:
            ValueError: Si la solicitud no existe
        """
        solicitud = self.solicitud_repo.get_by_id(solicitud_id)
        if not solicitud:
            raise ValueError(f"Solicitud con ID {solicitud_id} no existe")
        return solicitud
    
    def aprobar_solicitud(self, solicitud_id: int, 
                         comentario_admin: str = None) -> SolicitudBaja:
        """
        Aprueba una solicitud de baja.
        
        Args:
            solicitud_id: ID de la solicitud
            comentario_admin: Comentario opcional del administrador
            
        Returns:
            La solicitud aprobada
            
        Raises:
            ValueError: Si la solicitud no existe o no está pendiente
        """
        solicitud = self.obtener_solicitud(solicitud_id)
        
        if not solicitud.esta_pendiente():
            raise ValueError("Solo se pueden aprobar solicitudes pendientes")
        
        solicitud.aprobar(comentario_admin)
        return self.solicitud_repo.update(solicitud)
    
    def rechazar_solicitud(self, solicitud_id: int, 
                          comentario_admin: str) -> SolicitudBaja:
        """
        Rechaza una solicitud de baja.
        
        Args:
            solicitud_id: ID de la solicitud
            comentario_admin: Motivo del rechazo
            
        Returns:
            La solicitud rechazada
            
        Raises:
            ValueError: Si la solicitud no existe, no está pendiente,
                       o no se proporciona comentario
        """
        if not comentario_admin or len(comentario_admin.strip()) < 10:
            raise ValueError("El comentario del administrador es obligatorio")
        
        solicitud = self.obtener_solicitud(solicitud_id)
        
        if not solicitud.esta_pendiente():
            raise ValueError("Solo se pueden rechazar solicitudes pendientes")
        
        # Reactivar al socio
        socio = solicitud.socio
        from src.utils.enums import EstadoMembresia
        socio.estado_membresia = EstadoMembresia.ACTIVA
        self.socio_repo.update(socio)
        
        solicitud.rechazar(comentario_admin)
        return self.solicitud_repo.update(solicitud)
    
    def obtener_solicitudes_socio(self, socio_id: int) -> List[SolicitudBaja]:
        """
        Obtiene todas las solicitudes de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de solicitudes del socio
        """
        return self.solicitud_repo.find_by_socio(socio_id)
