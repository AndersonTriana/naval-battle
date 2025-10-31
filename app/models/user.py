"""
Modelos Pydantic para usuarios.
"""
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class UserRole(str, Enum):
    """Roles de usuario en el sistema."""
    ADMIN = "admin"
    PLAYER = "player"


class UserCreate(BaseModel):
    """Modelo para crear un nuevo usuario."""
    username: str = Field(min_length=3, max_length=50, description="Nombre de usuario único")
    password: str = Field(min_length=6, description="Contraseña del usuario")
    role: UserRole = Field(default=UserRole.PLAYER, description="Rol del usuario")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "jugador1",
                    "password": "password123",
                    "role": "player"
                }
            ]
        }
    }


class UserLogin(BaseModel):
    """Modelo para login de usuario."""
    username: str = Field(description="Nombre de usuario")
    password: str = Field(description="Contraseña del usuario")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "username": "admin",
                    "password": "admin123"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Modelo de respuesta con información del usuario."""
    id: str = Field(description="ID único del usuario (UUID)")
    username: str = Field(description="Nombre de usuario")
    role: UserRole = Field(description="Rol del usuario")
    created_at: datetime = Field(description="Fecha de creación")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "username": "jugador1",
                    "role": "player",
                    "created_at": "2024-01-01T12:00:00"
                }
            ]
        }
    }


class TokenResponse(BaseModel):
    """Modelo de respuesta con token de autenticación."""
    access_token: str = Field(description="Token de acceso JWT")
    token_type: str = Field(default="bearer", description="Tipo de token")
    user: UserResponse = Field(description="Información del usuario")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "token_type": "bearer",
                    "user": {
                        "id": "550e8400-e29b-41d4-a716-446655440000",
                        "username": "jugador1",
                        "role": "player",
                        "created_at": "2024-01-01T12:00:00"
                    }
                }
            ]
        }
    }
