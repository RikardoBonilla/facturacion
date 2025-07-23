"""
Configuración de la aplicación
Usando Pydantic Settings para manejo de variables de entorno
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Configuración de la aplicación usando variables de entorno"""
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Sistema de Facturación Electrónica Colombia"
    
    # Seguridad
    SECRET_KEY: str = Field(..., description="Clave secreta para JWT")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Base de datos
    DATABASE_URL: str = Field(..., description="URL de conexión a PostgreSQL")
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["*"]  # En producción, especificar dominios exactos
    
    # Debug
    DEBUG: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # DIAN (Facturación Electrónica)
    DIAN_AMBIENTE: str = "PRUEBAS"  # PRUEBAS o PRODUCCION
    DIAN_WSDL_URL: str = ""
    DIAN_CERTIFICADO_PATH: str = ""
    DIAN_CERTIFICADO_PASSWORD: str = ""
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instancia global de configuración
settings = Settings()