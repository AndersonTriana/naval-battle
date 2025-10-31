"""
Modelos Pydantic para tableros y flotas base.
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class BaseFleetCreate(BaseModel):
    """Modelo para crear una flota base."""
    name: str = Field(min_length=1, max_length=100, description="Nombre de la flota base")
    board_size: int = Field(ge=5, le=20, description="Tamaño del tablero (NxN)")
    ship_template_ids: List[str] = Field(description="IDs de las plantillas de barcos incluidas")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Flota Clásica",
                    "board_size": 10,
                    "ship_template_ids": [
                        "550e8400-e29b-41d4-a716-446655440001",
                        "550e8400-e29b-41d4-a716-446655440002"
                    ]
                }
            ]
        }
    }


class BaseFleetUpdate(BaseModel):
    """Modelo para actualizar una flota base."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nombre de la flota")
    board_size: Optional[int] = Field(None, ge=5, le=20, description="Tamaño del tablero")
    ship_template_ids: Optional[List[str]] = Field(None, description="IDs de plantillas de barcos")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Flota Clásica Actualizada",
                    "board_size": 12
                }
            ]
        }
    }


class BaseFleetResponse(BaseModel):
    """Modelo de respuesta con información de una flota base."""
    id: str = Field(description="ID único de la flota base (UUID)")
    name: str = Field(description="Nombre de la flota base")
    board_size: int = Field(description="Tamaño del tablero")
    ship_template_ids: List[str] = Field(description="IDs de plantillas de barcos")
    ship_count: int = Field(description="Número de barcos en la flota")
    created_by: str = Field(description="ID del usuario que creó la flota")
    created_at: datetime = Field(description="Fecha de creación")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440010",
                    "name": "Flota Clásica",
                    "board_size": 10,
                    "ship_template_ids": [
                        "550e8400-e29b-41d4-a716-446655440001",
                        "550e8400-e29b-41d4-a716-446655440002"
                    ],
                    "ship_count": 2,
                    "created_by": "550e8400-e29b-41d4-a716-446655440000",
                    "created_at": "2024-01-01T12:00:00"
                }
            ]
        }
    }


class BoardCell(BaseModel):
    """Modelo para una celda del tablero."""
    coordinate: str = Field(description="Coordenada en formato A1")
    coordinate_code: int = Field(description="Código numérico de la coordenada")
    has_ship: bool = Field(default=False, description="Indica si hay un barco")
    is_shot: bool = Field(default=False, description="Indica si fue disparada")
    is_hit: bool = Field(default=False, description="Indica si fue un impacto")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "coordinate": "A1",
                    "coordinate_code": 11,
                    "has_ship": True,
                    "is_shot": True,
                    "is_hit": True
                }
            ]
        }
    }


class BoardView(BaseModel):
    """Modelo para visualizar el estado del tablero."""
    board_size: int = Field(description="Tamaño del tablero")
    total_cells: int = Field(description="Total de celdas")
    shots_fired: int = Field(description="Disparos realizados")
    hits: int = Field(description="Impactos")
    misses: int = Field(description="Fallos")
    cells: List[BoardCell] = Field(description="Estado de las celdas")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "board_size": 10,
                    "total_cells": 100,
                    "shots_fired": 5,
                    "hits": 2,
                    "misses": 3,
                    "cells": []
                }
            ]
        }
    }
