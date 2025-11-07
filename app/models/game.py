"""
Modelos Pydantic para partidas y acciones de juego.
"""
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import List, Optional
from app.models.ship import ShipInstance


class GameStatus(str, Enum):
    """Estados posibles de una partida."""
    WAITING_FOR_PLAYER2 = "waiting_for_player2"  # Esperando que se una el jugador 2
    BOTH_PLAYERS_SETUP = "both_players_setup"  # Ambos jugadores colocando barcos simultáneamente
    PLAYER1_TURN = "player1_turn"  # Turno del jugador 1
    PLAYER2_TURN = "player2_turn"  # Turno del jugador 2
    FINISHED = "finished"  # Juego terminado
    PLAYER1_WON = "player1_won"  # Jugador 1 ganó
    PLAYER2_WON = "player2_won"  # Jugador 2 ganó
    
    # Estados legacy para compatibilidad con vs IA
    SETUP = "setup"  # Colocando barcos (vs IA)
    IN_PROGRESS = "in_progress"  # Jugando (vs IA)
    PLAYER1_SETUP = "player1_setup"  # Legacy - ahora usa BOTH_PLAYERS_SETUP
    PLAYER2_SETUP = "player2_setup"  # Legacy - ahora usa BOTH_PLAYERS_SETUP


class GameCreate(BaseModel):
    """Modelo para crear una nueva partida."""
    base_fleet_id: str = Field(description="ID de la flota base a utilizar")
    is_multiplayer: bool = Field(default=False, description="True para juego de 2 jugadores, False para vs IA")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "base_fleet_id": "550e8400-e29b-41d4-a716-446655440010",
                    "is_multiplayer": True
                }
            ]
        }
    }


class ShotRequest(BaseModel):
    """Modelo para realizar un disparo."""
    coordinate: str = Field(description="Coordenada a disparar (ej: B3)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "coordinate": "B3"
                }
            ]
        }
    }


class ShotResult(str, Enum):
    """Resultados posibles de un disparo."""
    WATER = "water"
    HIT = "hit"
    SUNK = "sunk"


class ShotResponse(BaseModel):
    """Modelo de respuesta de un disparo."""
    coordinate: str = Field(description="Coordenada disparada")
    coordinate_code: int = Field(description="Código de la coordenada")
    result: ShotResult = Field(description="Resultado del disparo")
    ship_hit: Optional[str] = Field(None, description="Nombre del barco impactado")
    ship_sunk: bool = Field(default=False, description="Indica si el barco fue hundido")
    game_finished: bool = Field(default=False, description="Indica si el juego terminó")
    ai_shot: Optional[dict] = Field(None, description="Disparo de la IA (si aplica)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "coordinate": "B3",
                    "coordinate_code": 23,
                    "result": "hit",
                    "ship_hit": "Portaaviones",
                    "ship_sunk": False,
                    "game_finished": False
                }
            ]
        }
    }


class ShotHistory(BaseModel):
    """Modelo para el historial de disparos."""
    coordinate: str = Field(description="Coordenada disparada")
    coordinate_code: int = Field(description="Código de la coordenada")
    result: ShotResult = Field(description="Resultado del disparo")
    timestamp: datetime = Field(description="Momento del disparo")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "coordinate": "B3",
                    "coordinate_code": 23,
                    "result": "hit",
                    "timestamp": "2024-01-01T12:30:00"
                }
            ]
        }
    }


class GameResponse(BaseModel):
    """Modelo de respuesta con información de una partida."""
    id: str = Field(description="ID único de la partida (UUID)")
    player1_id: str = Field(description="ID del jugador 1")
    player2_id: Optional[str] = Field(None, description="ID del jugador 2 (None si es vs IA o esperando jugador)")
    current_turn_player_id: Optional[str] = Field(None, description="ID del jugador en turno actual")
    base_fleet_id: str = Field(description="ID de la flota base utilizada")
    board_size: int = Field(description="Tamaño del tablero")
    status: GameStatus = Field(description="Estado actual de la partida")
    is_multiplayer: bool = Field(description="Indica si es partida multijugador")
    total_shots: int = Field(description="Total de disparos realizados")
    hits: int = Field(description="Número de impactos")
    misses: int = Field(description="Número de fallos")
    ships_total: int = Field(description="Total de barcos en la flota")
    ships_remaining: int = Field(description="Barcos restantes")
    ships_sunk: int = Field(description="Barcos hundidos")
    created_at: datetime = Field(description="Fecha de creación")
    finished_at: Optional[datetime] = Field(None, description="Fecha de finalización")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440020",
                    "player_id": "550e8400-e29b-41d4-a716-446655440000",
                    "base_fleet_id": "550e8400-e29b-41d4-a716-446655440010",
                    "board_size": 10,
                    "status": "in_progress",
                    "total_shots": 15,
                    "hits": 5,
                    "misses": 10,
                    "ships_total": 5,
                    "ships_remaining": 3,
                    "ships_sunk": 2,
                    "created_at": "2024-01-01T12:00:00",
                    "finished_at": None
                }
            ]
        }
    }


class GameDetailResponse(BaseModel):
    """Modelo de respuesta detallada de una partida."""
    game: GameResponse = Field(description="Información básica de la partida")
    ships: List[ShipInstance] = Field(description="Estado de los barcos")
    shot_history: List[ShotHistory] = Field(description="Historial de disparos")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "game": {
                        "id": "550e8400-e29b-41d4-a716-446655440020",
                        "player_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "in_progress"
                    },
                    "ships": [],
                    "shot_history": []
                }
            ]
        }
    }


class GameListResponse(BaseModel):
    """Modelo de respuesta para lista de partidas."""
    total: int = Field(description="Total de partidas")
    games: List[GameResponse] = Field(description="Lista de partidas")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total": 2,
                    "games": []
                }
            ]
        }
    }


class JoinGameResponse(BaseModel):
    """Modelo de respuesta al unirse a una partida."""
    game: GameResponse = Field(description="Información de la partida")
    message: str = Field(description="Mensaje de confirmación")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "game": {
                        "id": "550e8400-e29b-41d4-a716-446655440020",
                        "player1_id": "550e8400-e29b-41d4-a716-446655440000",
                        "player2_id": "550e8400-e29b-41d4-a716-446655440001",
                        "status": "player1_setup",
                        "is_multiplayer": True
                    },
                    "message": "Te has unido exitosamente a la partida"
                }
            ]
        }
    }
