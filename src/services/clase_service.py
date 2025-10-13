"""Servicio de gestión de Clases"""
from typing import List, Optional
from src.repositories.clase_repository import ClaseRepository
from src.models.clase import Clase
from src.models.entrenador import Entrenador
from src.models.horario import Horario
from src.utils.enums import DiaSemana


class ClaseService:
    """Servicio para operaciones de negocio relacionadas con Clases"""
    
    def __init__(self):
        self.clase_repo = ClaseRepository()
    
    def crear_clase(self, titulo: str, descripcion: str, cupo_maximo: int,
                   entrenador: Entrenador, horario: Horario) -> Clase:
        """
        Crea una nueva clase.
        
        Args:
            titulo: Nombre de la clase
            descripcion: Descripción de la actividad
            cupo_maximo: Cantidad máxima de participantes
            entrenador: Entrenador que dicta la clase
            horario: Horario de la clase
            
        Returns:
            La clase creada
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if cupo_maximo <= 0:
            raise ValueError("El cupo máximo debe ser mayor a 0")
        
        if len(titulo.strip()) < 3:
            raise ValueError("El título debe tener al menos 3 caracteres")
        
        nueva_clase = Clase(
            titulo=titulo,
            descripcion=descripcion,
            cupo_maximo=cupo_maximo,
            entrenador=entrenador,
            horario=horario
        )
        
        return self.clase_repo.create(nueva_clase)
    
    def obtener_clase(self, clase_id: int) -> Optional[Clase]:
        """Obtiene una clase por su ID"""
        return self.clase_repo.get_by_id(clase_id)
    
    def listar_clases_activas(self) -> List[Clase]:
        """Lista todas las clases activas"""
        return self.clase_repo.get_clases_activas()
    
    def listar_clases_por_plan(self, plan_id: int) -> List[Clase]:
        """
        Lista todas las clases de un plan específico.
        
        Args:
            plan_id: ID del plan de membresía
            
        Returns:
            Lista de clases del plan
        """
        return self.clase_repo.find_by_plan(plan_id)
    
    def listar_clases_por_dia(self, dia: DiaSemana) -> List[Clase]:
        """
        Lista todas las clases de un día específico.
        
        Args:
            dia: Día de la semana
            
        Returns:
            Lista de clases en ese día
        """
        return self.clase_repo.find_by_dia(dia)
    
    def listar_clases_con_cupo(self) -> List[Clase]:
        """Lista todas las clases que tienen cupo disponible"""
        return self.clase_repo.find_con_cupo_disponible()
    
    def filtrar_clases(self, plan_id: int = None, dia: DiaSemana = None,
                      solo_con_cupo: bool = False) -> List[Clase]:
        """
        Filtra clases según criterios múltiples.
        
        Args:
            plan_id: ID del plan (opcional)
            dia: Día de la semana (opcional)
            solo_con_cupo: Si True, solo muestra clases con cupo disponible
            
        Returns:
            Lista de clases filtradas
        """
        # Partir de todas las clases activas
        clases = self.clase_repo.get_clases_activas()
        
        # Filtrar por plan
        if plan_id:
            clases = [c for c in clases if any(p.id == plan_id for p in c.planes)]
        
        # Filtrar por día
        if dia:
            clases = [c for c in clases if c.horario.dia_semana == dia]
        
        # Filtrar por cupo disponible
        if solo_con_cupo:
            clases = [c for c in clases if c.tiene_cupo_disponible()]
        
        return clases
    
    def desactivar_clase(self, clase_id: int) -> None:
        """
        Desactiva una clase.
        
        Args:
            clase_id: ID de la clase a desactivar
            
        Raises:
            ValueError: Si la clase no existe
        """
        clase = self.clase_repo.get_by_id(clase_id)
        if not clase:
            raise ValueError(f"Clase con ID {clase_id} no existe")
        
        clase.desactivar()
        self.clase_repo.update(clase)
