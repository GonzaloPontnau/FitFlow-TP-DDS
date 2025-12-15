"""Servicio de gestión de Planes de Membresía"""
from typing import List, Optional
from src.repositories.plan_repository import PlanRepository
from src.models.plan_membresia import PlanMembresia
from src.models.clase import Clase


class PlanService:
    """Servicio para operaciones de negocio relacionadas con Planes de Membresía"""
    
    def __init__(self):
        self.plan_repo = PlanRepository()
    
    def crear_plan(self, titulo: str, descripcion: str, precio: float, nivel: int = 1) -> PlanMembresia:
        """
        Crea un nuevo plan de membresía.
        
        Args:
            titulo: Nombre del plan
            descripcion: Descripción del plan
            precio: Precio mensual
            nivel: Nivel jerárquico del plan (1=Básico, 2=Premium, 3=Elite)
            
        Returns:
            El plan creado
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if precio <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        
        if len(titulo.strip()) < 3:
            raise ValueError("El título debe tener al menos 3 caracteres")
        
        if nivel not in [1, 2, 3]:
            raise ValueError("El nivel debe ser 1, 2 o 3")
        
        # Verificar que no exista un plan con el mismo título
        plan_existente = self.plan_repo.find_by_titulo(titulo)
        if plan_existente:
            raise ValueError(f"Ya existe un plan con el título '{titulo}'")
        
        nuevo_plan = PlanMembresia(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            nivel=nivel
        )
        
        return self.plan_repo.create(nuevo_plan)
    
    def obtener_plan(self, plan_id: int) -> Optional[PlanMembresia]:
        """Obtiene un plan por su ID"""
        return self.plan_repo.get_by_id(plan_id)
    
    def listar_planes_activos(self) -> List[PlanMembresia]:
        """Lista todos los planes activos"""
        return self.plan_repo.get_planes_activos()
    
    def actualizar_plan(self, plan_id: int, titulo: str = None,
                       descripcion: str = None, precio: float = None) -> PlanMembresia:
        """
        Actualiza los datos de un plan.
        
        Args:
            plan_id: ID del plan a actualizar
            titulo: Nuevo título (opcional)
            descripcion: Nueva descripción (opcional)
            precio: Nuevo precio (opcional)
            
        Returns:
            El plan actualizado
            
        Raises:
            ValueError: Si el plan no existe o los datos son inválidos
        """
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan con ID {plan_id} no existe")
        
        if titulo:
            plan.titulo = titulo
        if descripcion:
            plan.descripcion = descripcion
        if precio is not None:
            if precio <= 0:
                raise ValueError("El precio debe ser mayor a 0")
            plan.precio = precio
        
        return self.plan_repo.update(plan)
    
    def desactivar_plan(self, plan_id: int) -> None:
        """
        Desactiva un plan (no se podrá asignar a nuevos socios).
        
        Args:
            plan_id: ID del plan a desactivar
            
        Raises:
            ValueError: Si el plan no existe
        """
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan con ID {plan_id} no existe")
        
        plan.desactivar()
        self.plan_repo.update(plan)
    
    def agregar_clase_a_plan(self, plan_id: int, clase: Clase) -> None:
        """
        Agrega una clase a un plan.
        
        Args:
            plan_id: ID del plan
            clase: Clase a agregar
            
        Raises:
            ValueError: Si el plan no existe
        """
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan con ID {plan_id} no existe")
        
        plan.agregar_clase(clase)
        self.plan_repo.update(plan)
    
    def quitar_clase_de_plan(self, plan_id: int, clase: Clase) -> None:
        """
        Quita una clase de un plan.
        
        Args:
            plan_id: ID del plan
            clase: Clase a quitar
            
        Raises:
            ValueError: Si el plan no existe
        """
        plan = self.plan_repo.get_by_id(plan_id)
        if not plan:
            raise ValueError(f"Plan con ID {plan_id} no existe")
        
        plan.quitar_clase(clase)
        self.plan_repo.update(plan)
