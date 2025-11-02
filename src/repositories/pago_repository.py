"""Repositorio para la entidad Pago"""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.pago import Pago, EstadoPago


class PagoRepository(BaseRepository[Pago]):
    """Repositorio para operaciones con Pagos"""
    
    def __init__(self):
        super().__init__(Pago)
    
    def find_by_socio(self, socio_id: int) -> List[Pago]:
        """
        Encuentra todos los pagos de un socio.
        
        Args:
            socio_id: ID del socio
            
        Returns:
            Lista de pagos del socio
        """
        return self.session.query(Pago).filter_by(socio_id=socio_id).all()
    
    def find_by_referencia_externa(self, referencia: str) -> Optional[Pago]:
        """
        Encuentra un pago por su referencia externa.
        
        Args:
            referencia: Referencia externa del pago
            
        Returns:
            Objeto Pago o None si no existe
        """
        return self.session.query(Pago).filter_by(
            referencia_externa=referencia
        ).first()
    
    def find_pagos_pendientes(self) -> List[Pago]:
        """
        Obtiene todos los pagos pendientes de verificación.
        
        Returns:
            Lista de pagos en estado PENDIENTE o PROCESANDO
        """
        return self.session.query(Pago).filter(
            Pago.estado.in_([EstadoPago.PENDIENTE, EstadoPago.PROCESANDO])
        ).all()
    
    def find_by_periodo(self, mes: int, anio: int) -> List[Pago]:
        """
        Encuentra pagos por período.
        
        Args:
            mes: Mes del período (1-12)
            anio: Año del período
            
        Returns:
            Lista de pagos del período
        """
        return self.session.query(Pago).filter_by(
            mes_periodo=mes,
            anio_periodo=anio
        ).all()
    
    def find_pagos_socio_periodo(self, socio_id: int, mes: int, 
                                  anio: int) -> Optional[Pago]:
        """
        Encuentra el pago de un socio para un período específico.
        
        Args:
            socio_id: ID del socio
            mes: Mes del período
            anio: Año del período
            
        Returns:
            Objeto Pago o None si no existe
        """
        return self.session.query(Pago).filter_by(
            socio_id=socio_id,
            mes_periodo=mes,
            anio_periodo=anio
        ).first()

