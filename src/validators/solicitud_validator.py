"""Validador de solicitudes de baja"""
from src.utils.enums import LONGITUD_MINIMA_SOLICITUD_BAJA


class ValidadorDeSolicitudes:
    """
    Interfaz para validar solicitudes de baja.
    
    Implementa el patrón Strategy para permitir diferentes
    estrategias de validación.
    """
    
    def es_valida(self, texto: str) -> bool:
        """
        Valida si un texto de solicitud cumple los requisitos.
        
        Args:
            texto: Texto de la justificación
            
        Returns:
            True si es válida, False en caso contrario
        """
        raise NotImplementedError("Debe implementarse en una subclase")


class ValidadorLongitudMinima(ValidadorDeSolicitudes):
    """Validador que verifica la longitud mínima del texto"""
    
    def es_valida(self, texto: str) -> bool:
        """
        Valida que el texto tenga la longitud mínima requerida.
        
        Args:
            texto: Texto a validar
            
        Returns:
            True si cumple con la longitud mínima
        """
        if not texto:
            return False
        return len(texto.strip()) >= LONGITUD_MINIMA_SOLICITUD_BAJA


class ValidadorPalabrasVacias(ValidadorDeSolicitudes):
    """Validador que verifica que el texto no sea solo espacios"""
    
    def es_valida(self, texto: str) -> bool:
        """
        Valida que el texto contenga caracteres significativos.
        
        Args:
            texto: Texto a validar
            
        Returns:
            True si contiene texto significativo
        """
        if not texto:
            return False
        return len(texto.strip()) > 0 and not texto.isspace()


class ValidadorCompuesto(ValidadorDeSolicitudes):
    """
    Validador que combina múltiples validadores.
    
    Todos los validadores deben aprobar para que sea válida.
    """
    
    def __init__(self):
        self.validadores = [
            ValidadorLongitudMinima(),
            ValidadorPalabrasVacias()
        ]
    
    def es_valida(self, texto: str) -> bool:
        """
        Ejecuta todos los validadores.
        
        Args:
            texto: Texto a validar
            
        Returns:
            True si todos los validadores aprueban
        """
        return all(validador.es_valida(texto) for validador in self.validadores)
    
    def agregar_validador(self, validador: ValidadorDeSolicitudes) -> None:
        """
        Agrega un nuevo validador a la cadena.
        
        Args:
            validador: Validador a agregar
        """
        self.validadores.append(validador)
