"""Modelo de Socio"""
from sqlalchemy import Integer, String, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from src.config.database import db
from src.utils.enums import RolUsuario, EstadoMembresia


class Socio(db.Model):
    """
    Representa un socio del gimnasio.
    
    Un socio puede tener diferentes roles y estados de membresía.
    Puede realizar reservas en las clases incluidas en su plan.
    """
    __tablename__ = 'socios'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido: Mapped[str] = mapped_column(String(100), nullable=False)
    dni: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(
        Enum(RolUsuario),
        default=RolUsuario.VISUALIZADOR
    )
    estado_membresia: Mapped[EstadoMembresia] = mapped_column(
        Enum(EstadoMembresia),
        default=EstadoMembresia.ACTIVA
    )
    
    # Foreign Key
    plan_membresia_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('planes_membresia.id'),
        nullable=True
    )
    
    # Relaciones
    plan_membresia: Mapped[Optional["PlanMembresia"]] = relationship(
        "PlanMembresia",
        back_populates="socios"
    )
    reservas: Mapped[List["Reserva"]] = relationship(
        "Reserva",
        back_populates="socio"
    )
    solicitudes_baja: Mapped[List["SolicitudBaja"]] = relationship(
        "SolicitudBaja",
        back_populates="socio"
    )
    
    def __init__(self, nombre: str, apellido: str, dni: str, email: str,
                 plan_membresia: Optional["PlanMembresia"] = None):
        """
        Inicializa un nuevo Socio.
        
        Args:
            nombre: Nombre del socio
            apellido: Apellido del socio
            dni: Documento Nacional de Identidad
            email: Email de contacto
            plan_membresia: Plan de membresía contratado (opcional)
        """
        self.nombre = nombre
        self.apellido = apellido
        self.dni = dni
        self.email = email
        self.plan_membresia = plan_membresia
        self.rol = RolUsuario.SOCIO_REGISTRADO if plan_membresia else RolUsuario.VISUALIZADOR
        self.estado_membresia = EstadoMembresia.ACTIVA if plan_membresia else EstadoMembresia.SUSPENDIDA
    
    @property
    def nombre_completo(self) -> str:
        """Retorna el nombre completo del socio"""
        return f"{self.nombre} {self.apellido}"
    
    def tiene_plan_activo(self) -> bool:
        """Verifica si el socio tiene un plan de membresía activo"""
        return (self.plan_membresia is not None and 
                self.estado_membresia == EstadoMembresia.ACTIVA)
    
    def puede_acceder_clase(self, clase: "Clase") -> bool:
        """Verifica si el socio puede acceder a una clase específica"""
        if not self.tiene_plan_activo():
            return False
        return clase.esta_incluida_en_plan(self.plan_membresia)
    
    def asignar_plan(self, plan: "PlanMembresia") -> None:
        """Asigna un plan de membresía al socio"""
        self.plan_membresia = plan
        self.rol = RolUsuario.SOCIO_REGISTRADO
        self.estado_membresia = EstadoMembresia.ACTIVA
    
    def suspender_membresia(self) -> None:
        """Suspende la membresía del socio"""
        self.estado_membresia = EstadoMembresia.SUSPENDIDA
    
    def solicitar_baja(self) -> None:
        """Marca el estado como baja solicitada"""
        self.estado_membresia = EstadoMembresia.BAJA_SOLICITADA
    
    def dar_de_baja(self) -> None:
        """Da de baja definitiva al socio"""
        self.estado_membresia = EstadoMembresia.BAJA_DEFINITIVA
        self.plan_membresia = None
    
    def __repr__(self) -> str:
        return (f"<Socio(id={self.id}, nombre='{self.nombre_completo}', "
                f"dni='{self.dni}', estado='{self.estado_membresia.value}')>")
