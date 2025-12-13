from typing import Dict, Any, Optional
from src.models.socio import Socio
from src.models.plan_membresia import PlanMembresia
from src.repositories.socio_repository import SocioRepository
from src.config.database import db 

class SocioService:
    def __init__(self):
        self.socio_repository = SocioRepository()

    def crear_socio(self, data: Dict[str, Any]) -> Socio:
        """
        Crea un nuevo socio validando reglas de negocio.
        
        Args:
            data: Diccionario con los datos del formulario (nombre, dni, plan_id, etc.)
        """
        
        # 1. VALIDACIONES DE UNICIDAD
        # Verificamos que no exista otro socio con el mismo DNI
        if self.socio_repository.find_by_dni(data.get('dni')):
            raise ValueError("Ya existe un socio registrado con ese DNI.")

        # Verificamos que no exista otro socio con el mismo Email
        if self.socio_repository.find_by_email(data.get('email')):
            raise ValueError("Ya existe un socio registrado con ese Email.")

        # 2. OBTENER EL OBJETO PLAN (Clave para tu lógica de negocio)
        # Tu modelo Socio espera un OBJETO PlanMembresia en el __init__, no un ID.
        # Por eso, buscamos el plan en la base de datos usando el ID que viene del front.
        plan_objeto: Optional[PlanMembresia] = None
        
        # El front puede mandar 'plan_id' o 'plan_membresia_id', ajustalo según tu HTML
        plan_id = data.get('plan_id') or data.get('plan_membresia_id')
        
        if plan_id:
            # Buscamos el plan. Usamos db.session.get(Modelo, id)
            plan_objeto = db.session.get(PlanMembresia, int(plan_id))
            
            if not plan_objeto:
                raise ValueError("El plan de membresía seleccionado no es válido.")

        # 3. INSTANCIAR EL MODELO
        # Al pasarle 'plan_objeto', tu modelo automáticamente setea:
        # rol = SOCIO_REGISTRADO y estado = ACTIVA
        nuevo_socio = Socio(
            nombre=data['nombre'],
            apellido=data['apellido'],
            dni=data['dni'],
            email=data['email'],
            plan_membresia=plan_objeto 
        )

        # 4. PERSISTENCIA
        # Usamos el método create que agregamos al repositorio (o el save del base)
        # Si tu repositorio base usa 'add' o 'save', cambialo aquí.
        return self.socio_repository.create(nuevo_socio)

    def obtener_todos(self):
        """Devuelve todos los socios (útil para tu lista)"""
        return self.socio_repository.find_all() # Asumiendo que BaseRepository tiene find_all