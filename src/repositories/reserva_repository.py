"""Repositorio para la entidad Reserva"""
from typing import List
from src.repositories.base_repository import BaseRepository
from src.models.reserva import Reserva


class ReservaRepository(BaseRepository[Reserva]):
    """Repositorio para operaciones con Reservas"""
    
    def __init__(self):
        super().__init__(Reserva)
    
    def find_by_socio(self, socio_id: int) -> List[Reserva]:
        """
        Encuentra todas las reservas de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de reservas del socio
        """
        return self.session.query(Reserva).filter_by(socio_id=socio_id).all()
    
    def find_by_clase(self, clase_id: int) -> List[Reserva]:
        """
        Encuentra todas las reservas de una clase.
        
        Args:
            clase_id: ID de la clase
            
        Returns:
            Lista de reservas de la clase
        """
        return self.session.query(Reserva).filter_by(clase_id=clase_id).all()
    
    def get_reservas_activas_clase(self, clase_id: int) -> List[Reserva]:
        """
        Obtiene las reservas activas de una clase.
        
        Args:
            clase_id: ID de la clase
            
        Returns:
            Lista de reservas confirmadas
        """
        return self.session.query(Reserva).filter_by(
            clase_id=clase_id,
            confirmada=True
        ).all()
