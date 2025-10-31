"""
Configuración de la aplicación.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación."""
    
    # Configuración del servidor
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    
    # Configuración de logging
    log_level: str = "INFO"
    
    # Configuración de seguridad
    secret_key: str = "your-secret-key-change-this-in-production-123456789"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 horas
    
    # Configuración de la aplicación
    project_name: str = "Batalla Naval API"
    version: str = "1.0.0"
    description: str = "API REST para juego de Batalla Naval con ABB y Árbol N-ario"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Instancia global de configuración
settings = Settings()
