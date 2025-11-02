"""Configuración del sistema de logging"""
import logging
import sys
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Formatter con colores para la consola"""
    
    # Códigos ANSI para colores
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Verde
        'WARNING': '\033[33m',    # Amarillo
        'ERROR': '\033[31m',      # Rojo
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Agregar color al nivel de log
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logging(log_level: str = 'INFO', log_dir: str = 'logs'):
    """
    Configura el sistema de logging de la aplicación.
    
    Args:
        log_level: Nivel de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directorio donde guardar los archivos de log
    """
    # Crear directorio de logs si no existe
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Formato de los logs
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Limpiar handlers existentes
    root_logger.handlers.clear()
    
    # Handler para consola con colores
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_formatter = ColoredFormatter(log_format, datefmt=date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Handler para archivo general
    file_handler = logging.FileHandler(
        log_path / f"fitflow_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(log_format, datefmt=date_format)
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Handler para errores (archivo separado)
    error_handler = logging.FileHandler(
        log_path / f"fitflow_errors_{datetime.now().strftime('%Y%m%d')}.log",
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_handler)
    
    # Silenciar logs de bibliotecas externas ruidosas
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    
    logging.info("Sistema de logging configurado correctamente")


def get_logger(name: str) -> logging.Logger:
    """
    Obtiene un logger con el nombre especificado.
    
    Args:
        name: Nombre del logger (usualmente __name__)
        
    Returns:
        Logger configurado
    """
    return logging.getLogger(name)

