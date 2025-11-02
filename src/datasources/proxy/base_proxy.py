"""Clase base para fuentes proxy"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseProxy(ABC):
    """
    Clase base abstracta para todas las fuentes proxy.
    
    Define la interfaz común que deben implementar todas las
    fuentes de datos externas.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa el proxy con configuración opcional.
        
        Args:
            config: Diccionario con configuración específica del proxy
        """
        self.config = config or {}
    
    @abstractmethod
    def conectar(self) -> bool:
        """
        Establece conexión con el servicio externo.
        
        Returns:
            True si la conexión fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def verificar_disponibilidad(self) -> bool:
        """
        Verifica si el servicio externo está disponible.
        
        Returns:
            True si el servicio está disponible, False en caso contrario
        """
        pass
    
    def desconectar(self) -> None:
        """
        Cierra la conexión con el servicio externo.
        
        Implementación por defecto que puede ser sobrescrita.
        """
        pass

