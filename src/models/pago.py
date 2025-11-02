"""Modelo de Pago"""
from sqlalchemy import Integer, Float, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, UTC
from src.config.database import db
from enum import Enum as PyEnum


class EstadoPago(PyEnum):
    """Estados posibles de un pago"""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"
    PROCESANDO = "procesando"
    REEMBOLSADO = "reembolsado"


class Pago(db.Model):
    """
    Representa un pago de membresía.
    
    Un pago se asocia a un socio y a su plan de membresía,
    registrando el estado del pago verificado con la pasarela externa.
    """
    __tablename__ = 'pagos'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    monto: Mapped[float] = mapped_column(Float, nullable=False)
    fecha_pago: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC)
    )
    estado: Mapped[EstadoPago] = mapped_column(
        Enum(EstadoPago),
        default=EstadoPago.PENDIENTE
    )
    referencia_externa: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
        unique=True
    )
    fecha_verificacion: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True
    )
    mes_periodo: Mapped[int] = mapped_column(Integer, nullable=False)
    anio_periodo: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Foreign Key
    socio_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('socios.id'),
        nullable=False
    )
    
    # Relaciones
    socio: Mapped["Socio"] = relationship(
        "Socio",
        back_populates="pagos"
    )
    
    def __init__(self, socio: "Socio", monto: float, mes_periodo: int, 
                 anio_periodo: int, referencia_externa: str = None):
        """
        Inicializa un nuevo Pago.
        
        Args:
            socio: Socio que realiza el pago
            monto: Monto del pago
            mes_periodo: Mes del período que se está pagando (1-12)
            anio_periodo: Año del período que se está pagando
            referencia_externa: ID de transacción en la pasarela externa
        """
        self.socio = socio
        self.monto = monto
        self.mes_periodo = mes_periodo
        self.anio_periodo = anio_periodo
        self.referencia_externa = referencia_externa
        self.fecha_pago = datetime.now(UTC)
        self.estado = EstadoPago.PENDIENTE
    
    def actualizar_estado(self, nuevo_estado: EstadoPago) -> None:
        """
        Actualiza el estado del pago.
        
        Args:
            nuevo_estado: Nuevo estado del pago
        """
        self.estado = nuevo_estado
        self.fecha_verificacion = datetime.now(UTC)
    
    def esta_aprobado(self) -> bool:
        """Verifica si el pago está aprobado"""
        return self.estado == EstadoPago.APROBADO
    
    def esta_pendiente(self) -> bool:
        """Verifica si el pago está pendiente"""
        return self.estado == EstadoPago.PENDIENTE
    
    def __repr__(self) -> str:
        return (f"<Pago(id={self.id}, socio_id={self.socio_id}, "
                f"monto={self.monto}, estado='{self.estado.value}', "
                f"periodo={self.mes_periodo}/{self.anio_periodo})>")

