"""Repositorio para la entidad PlanMembresia"""
from typing import List
from src.repositories.base_repository import BaseRepository
from src.models.plan_membresia import PlanMembresia


class PlanRepository(BaseRepository[PlanMembresia]):
    """Repositorio para operaciones con Planes de Membresía"""
    
    def __init__(self):
        super().__init__(PlanMembresia)
    
    def get_planes_activos(self) -> List[PlanMembresia]:
        """
        Obtiene todos los planes activos.
        
        Returns:
            Lista de planes activos
        """
        return self.session.query(PlanMembresia).filter_by(activo=True).all()
    
    def find_by_titulo(self, titulo: str) -> PlanMembresia:
        """
        Busca un plan por su título.
        
        Args:
            titulo: Título del plan
            
        Returns:
            El plan si existe, None en caso contrario
        """
        return self.session.query(PlanMembresia).filter_by(titulo=titulo).first()
