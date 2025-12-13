"""Repositorio para la entidad SolicitudBaja"""
from typing import List
from src.repositories.base_repository import BaseRepository
from src.models.solicitud_baja import SolicitudBaja
from src.utils.enums import EstadoSolicitudBaja


class SolicitudBajaRepository(BaseRepository[SolicitudBaja]):
    """Repositorio para operaciones con Solicitudes de Baja"""
    
    def __init__(self):
        super().__init__(SolicitudBaja)
    
    def get_pendientes(self) -> List[SolicitudBaja]:
        """
        Obtiene todas las solicitudes pendientes.
        
        Returns:
            Lista de solicitudes pendientes
        """
        print(">>> DEBUG REPO: Querying ALL requests (debug mode)...")
        # DEBUG: Traer todas para ver qué está pasando
        res = self.session.query(SolicitudBaja).all()
        print(f">>> DEBUG REPO: Found {len(res)} TOTAL requests.")
        for r in res:
             print(f"   -> Req {r.id}: Socio {r.socio_id}, Estado {r.estado} (Type: {type(r.estado)})")
        
        # Restaurar filtro en memoria si es necesario, o devolver todo para ver en frontend
        # return [r for r in res if r.estado == EstadoSolicitudBaja.PENDIENTE]
        return res
    
    def find_by_socio(self, socio_id: int) -> List[SolicitudBaja]:
        """
        Encuentra todas las solicitudes de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de solicitudes del socio
        """
        return self.session.query(SolicitudBaja).filter_by(
            socio_id=socio_id
        ).all()
    
    def tiene_solicitud_pendiente(self, socio_id: int) -> bool:
        """
        Verifica si un socio tiene una solicitud pendiente.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            True si tiene solicitud pendiente, False en caso contrario
        """
        return self.session.query(SolicitudBaja).filter_by(
            socio_id=socio_id,
            estado=EstadoSolicitudBaja.PENDIENTE
        ).first() is not None
