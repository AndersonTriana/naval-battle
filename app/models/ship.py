"""
Modelos Pydantic para barcos y plantillas de barcos.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class ShipTemplateCreate(BaseModel):
    """Modelo para crear una plantilla de barco."""
    name: str = Field(min_length=1, max_length=50, description="Nombre del tipo de barco")
    size: int = Field(ge=1, le=10, description="Tamaño del barco (número de celdas)")
    description: Optional[str] = Field(None, max_length=200, description="Descripción opcional del barco")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Portaaviones",
                    "size": 5,
                    "description": "El barco más grande de la flota"
                }
            ]
        }
    }


class ShipTemplateUpdate(BaseModel):
    """Modelo para actualizar una plantilla de barco."""
    name: Optional[str] = Field(None, min_length=1, max_length=50, description="Nombre del tipo de barco")
    size: Optional[int] = Field(None, ge=1, le=10, description="Tamaño del barco")
    description: Optional[str] = Field(None, max_length=200, description="Descripción del barco")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Portaaviones Mejorado",
                    "size": 6,
                    "description": "Versión mejorada del portaaviones"
                }
            ]
        }
    }


class ShipTemplateResponse(BaseModel):
    """Modelo de respuesta con información de una plantilla de barco."""
    id: str = Field(description="ID único de la plantilla (UUID)")
    name: str = Field(description="Nombre del tipo de barco")
    size: int = Field(description="Tamaño del barco")
    description: Optional[str] = Field(description="Descripción del barco")
    created_by: str = Field(description="ID del usuario que creó la plantilla")
    created_at: datetime = Field(description="Fecha de creación")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "name": "Portaaviones",
                    "size": 5,
                    "description": "El barco más grande de la flota",
                    "created_by": "550e8400-e29b-41d4-a716-446655440000",
                    "created_at": "2024-01-01T12:00:00"
                }
            ]
        }
    }


class ShipSegment(BaseModel):
    """Modelo para un segmento de barco en el tablero."""
    coordinate: str = Field(description="Coordenada en formato A1, B3, etc.")
    coordinate_code: int = Field(description="Código numérico de la coordenada")
    is_hit: bool = Field(default=False, description="Indica si este segmento fue impactado")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "coordinate": "A1",
                    "coordinate_code": 11,
                    "is_hit": False
                }
            ]
        }
    }


class ShipInstance(BaseModel):
    """Modelo para una instancia de barco colocado en el tablero."""
    ship_template_id: str = Field(description="ID de la plantilla de barco")
    ship_name: str = Field(description="Nombre del barco")
    size: int = Field(description="Tamaño del barco")
    segments: List[ShipSegment] = Field(description="Segmentos del barco")
    is_sunk: bool = Field(default=False, description="Indica si el barco está hundido")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ship_template_id": "550e8400-e29b-41d4-a716-446655440001",
                    "ship_name": "Portaaviones",
                    "size": 5,
                    "segments": [
                        {"coordinate": "A1", "coordinate_code": 11, "is_hit": False},
                        {"coordinate": "A2", "coordinate_code": 12, "is_hit": True}
                    ],
                    "is_sunk": False
                }
            ]
        }
    }


class ShipPlacement(BaseModel):
    """Modelo para colocar un barco en el tablero."""
    ship_template_id: str = Field(description="ID de la plantilla de barco a colocar")
    start_coordinate: str = Field(description="Coordenada inicial (ej: A1)")
    orientation: str = Field(pattern="^(horizontal|vertical)$", description="Orientación del barco")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "ship_template_id": "550e8400-e29b-41d4-a716-446655440001",
                    "start_coordinate": "A1",
                    "orientation": "horizontal"
                }
            ]
        }
    }
