"""Data Transfer Objects (DTOs) para transferencia de datos"""
from dataclasses import dataclass
from typing import Optional, Generic, TypeVar, Any
from datetime import datetime

T = TypeVar('T')


@dataclass
class OperationResult(Generic[T]):
    """
    Resultado estándar de operaciones de servicio.
    
    Encapsula el resultado de una operación, incluyendo éxito/fallo,
    datos y mensajes.
    """
    success: bool
    data: Optional[T] = None
    message: str = ""
    errors: list = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @classmethod
    def ok(cls, data: T = None, message: str = "Operación exitosa") -> 'OperationResult[T]':
        """Crea un resultado exitoso"""
        return cls(success=True, data=data, message=message)
    
    @classmethod
    def fail(cls, message: str, errors: list = None) -> 'OperationResult[T]':
        """Crea un resultado fallido"""
        return cls(success=False, message=message, errors=errors or [])
    
    def to_dict(self) -> dict:
        """Convierte el resultado a diccionario"""
        return {
            'success': self.success,
            'data': self.data,
            'message': self.message,
            'errors': self.errors
        }


@dataclass
class SocioDTO:
    """DTO para información de Socio"""
    id: int
    nombre: str
    apellido: str
    dni: str
    email: str
    rol: str
    estado_membresia: str
    plan_membresia_id: Optional[int] = None
    plan_membresia_nombre: Optional[str] = None
    
    @property
    def nombre_completo(self) -> str:
        return f"{self.nombre} {self.apellido}"


@dataclass
class ClaseDTO:
    """DTO para información de Clase"""
    id: int
    titulo: str
    descripcion: str
    cupo_maximo: int
    cupos_disponibles: int
    activa: bool
    entrenador_nombre: str
    dia_semana: str
    hora_inicio: str
    duracion_minutos: int


@dataclass
class ReservaDTO:
    """DTO para información de Reserva"""
    id: int
    socio_id: int
    socio_nombre: str
    clase_id: int
    clase_titulo: str
    fecha_reserva: datetime
    confirmada: bool
    fecha_cancelacion: Optional[datetime] = None


@dataclass
class PagoDTO:
    """DTO para información de Pago"""
    id: int
    socio_id: int
    socio_nombre: str
    monto: float
    estado: str
    fecha_pago: datetime
    mes_periodo: int
    anio_periodo: int
    referencia_externa: Optional[str] = None
    fecha_verificacion: Optional[datetime] = None


@dataclass
class ClaseExternaDTO:
    """DTO para información de Clases Externas"""
    id_externo: str
    titulo: str
    descripcion: str
    instructor: str
    fecha: datetime
    hora_inicio: str
    hora_fin: str
    duracion_minutos: int
    cupo_maximo: int
    cupos_disponibles: int
    precio: float
    ubicacion: str
    proveedor: str


@dataclass
class PaginationInfo:
    """Información de paginación para listas"""
    page: int
    page_size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class PaginatedResult(Generic[T]):
    """Resultado paginado de una consulta"""
    items: list[T]
    pagination: PaginationInfo

