"""Configuración centralizada de la aplicación"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


@dataclass
class DatabaseConfig:
    """Configuración de base de datos"""
    url: str
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class ProxyConfig:
    """Configuración para servicios proxy"""
    pasarela_pagos_url: str
    pasarela_pagos_api_key: str
    clases_externas_url: str
    clases_externas_api_key: str
    timeout: int = 30


@dataclass
class AppConfig:
    """Configuración general de la aplicación"""
    secret_key: str
    debug: bool
    testing: bool
    log_level: str
    host: str = '0.0.0.0'
    port: int = 5000


class Settings:
    """
    Configuración centralizada del sistema FitFlow.
    
    Singleton que gestiona toda la configuración de la aplicación.
    """
    _instance: Optional['Settings'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._load_config()
    
    def _load_config(self):
        """Carga la configuración desde variables de entorno"""
        # Configuración de la aplicación
        self.app = AppConfig(
            secret_key=os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
            debug=os.getenv('DEBUG', 'False').lower() == 'true',
            testing=os.getenv('TESTING', 'False').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            host=os.getenv('HOST', '0.0.0.0'),
            port=int(os.getenv('PORT', 5000))
        )
        
        # Configuración de base de datos
        # Obtener ruta absoluta para SQLite
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        instance_dir = os.path.join(base_dir, 'src', 'instance')
        # Crear directorio instance si no existe
        os.makedirs(instance_dir, exist_ok=True)
        db_path = os.path.join(instance_dir, 'fitflow.db')
        # Convertir a formato de URL válido para SQLite (barras forward en Windows)
        default_db_url = f'sqlite:///{db_path.replace(os.sep, "/")}'
        
        self.database = DatabaseConfig(
            url=os.getenv('DATABASE_URL', default_db_url),
            echo=os.getenv('DB_ECHO', 'False').lower() == 'true',
            pool_size=int(os.getenv('DB_POOL_SIZE', 5)),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', 10))
        )
        
        # Configuración de servicios proxy
        self.proxy = ProxyConfig(
            pasarela_pagos_url=os.getenv(
                'PASARELA_PAGOS_URL',
                'https://api.pasarela-ficticia.com'
            ),
            pasarela_pagos_api_key=os.getenv('PASARELA_PAGOS_API_KEY', 'test_api_key'),
            clases_externas_url=os.getenv(
                'CLASES_EXTERNAS_URL',
                'https://api.talleres-especiales.com'
            ),
            clases_externas_api_key=os.getenv('CLASES_EXTERNAS_API_KEY', 'test_key'),
            timeout=int(os.getenv('PROXY_TIMEOUT', 30))
        )
    
    @classmethod
    def get_instance(cls) -> 'Settings':
        """Obtiene la instancia única de Settings"""
        return cls()


# Instancia global de configuración
settings = Settings.get_instance()

