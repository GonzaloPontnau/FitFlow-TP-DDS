"""Repositorio para la entidad Clase"""
from typing import List
from src.repositories.base_repository import BaseRepository
from src.models.clase import Clase
from src.utils.enums import DiaSemana


class ClaseRepository(BaseRepository[Clase]):
    """Repositorio para operaciones con Clases"""
    
    def __init__(self):
        super().__init__(Clase)
    
    def get_clases_activas(self) -> List[Clase]:
        """
        Obtiene todas las clases activas.
        
        Returns:
            Lista de clases activas
        """
        return self.session.query(Clase).filter_by(activa=True).all()
    
    def find_by_plan(self, plan_id: int) -> List[Clase]:
        """
        Encuentra todas las clases de un plan específico.
        
        Args:
            plan_id: ID del plan de membresía
            
        Returns:
            Lista de clases del plan
        """
        from src.models.plan_membresia import PlanMembresia
        
        plan = self.session.get(PlanMembresia, plan_id)
        if plan:
            return [clase for clase in plan.clases if clase.activa]
        return []
    
    def find_by_dia(self, dia: DiaSemana) -> List[Clase]:
        """
        Encuentra todas las clases de un día específico.
        
        Args:
            dia: Día de la semana
            
        Returns:
            Lista de clases en ese día
        """
        from src.models.horario import Horario
        
        return (self.session.query(Clase)
                .join(Horario)
                .filter(Horario.dia_semana == dia)
                .filter(Clase.activa == True)
                .all())
    
    def find_con_cupo_disponible(self) -> List[Clase]:
        """
        Encuentra todas las clases con cupo disponible.
        
        Returns:
            Lista de clases con cupo
        """
        clases_activas = self.get_clases_activas()
        return [clase for clase in clases_activas if clase.tiene_cupo_disponible()]
