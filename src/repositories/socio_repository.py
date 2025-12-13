"""Repositorio para la entidad Socio"""
from typing import List, Optional
from src.repositories.base_repository import BaseRepository
from src.models.socio import Socio


class SocioRepository(BaseRepository[Socio]):
    """Repositorio para operaciones con Socios"""
    
    def __init__(self):
        super().__init__(Socio)
    
    def find_by_dni(self, dni: str) -> Optional[Socio]:
        """
        Busca un socio por su DNI.
        
        Args:
            dni: Documento Nacional de Identidad
            
        Returns:
            El socio si existe, None en caso contrario
        """
        return self.session.query(Socio).filter_by(dni=dni).first()
    
    def find_by_email(self, email: str) -> Optional[Socio]:
        """
        Busca un socio por su email.
        
        Args:
            email: Email del socio
            
        Returns:
            El socio si existe, None en caso contrario
        """
        return self.session.query(Socio).filter_by(email=email).first()
    
    def find_by_plan(self, plan_id: int) -> List[Socio]:
        """
        Encuentra todos los socios con un plan específico.
        
        Args:
            plan_id: ID del plan de membresía
            
        Returns:
            Lista de socios con ese plan
        """
        return self.session.query(Socio).filter_by(plan_membresia_id=plan_id).all()
    
    def get_socios_activos(self) -> List[Socio]:
        """
        Obtiene todos los socios con membresía activa.
        
        Returns:
            Lista de socios activos
        """
        from src.utils.enums import EstadoMembresia
        return self.session.query(Socio).filter_by(
            estado_membresia=EstadoMembresia.ACTIVA
        ).all()

    #metodo para guardar un nuevo socio
    def create(self, socio: Socio) -> Socio:
        """Guarda un nuevo socio en la base de datos"""
        try:
            self.session.add(socio)
            self.session.commit()
            return socio
        except Exception as e:
            self.session.rollback()
            raise e