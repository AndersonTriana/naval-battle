"""
Clases Python para almacenamiento de datos en memoria.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid


@dataclass
class User:
    """Clase para almacenar datos de usuario."""
    id: str
    username: str
    hashed_password: str
    role: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ShipTemplate:
    """Clase para almacenar plantillas de barcos."""
    id: str
    name: str
    size: int
    description: Optional[str]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class BaseFleet:
    """Clase para almacenar flotas base."""
    id: str
    name: str
    board_size: int
    ship_template_ids: List[str]
    created_by: str
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ShipSegmentData:
    """Clase para almacenar datos de un segmento de barco."""
    coordinate: str
    coordinate_code: int
    is_hit: bool = False


@dataclass
class ShipInstanceData:
    """Clase para almacenar instancia de barco en el juego."""
    ship_template_id: str
    ship_name: str
    size: int
    segments: List[ShipSegmentData]
    is_sunk: bool = False


@dataclass
class ShotData:
    """Clase para almacenar datos de un disparo."""
    coordinate: str
    coordinate_code: int
    result: str  # "water", "hit", "sunk"
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Game:
    """Clase para almacenar datos de una partida."""
    id: str
    player_id: str
    base_fleet_id: str
    board_size: int
    status: str  # "setup", "in_progress", "finished"
    abb_tree: Any  # Instancia del ABB de coordenadas del jugador
    fleet_tree: Any  # Instancia del árbol N-ario de flota del jugador
    ships: List[ShipInstanceData] = field(default_factory=list)  # Barcos del jugador
    shots: List[ShotData] = field(default_factory=list)  # Disparos del jugador
    occupied_coordinates: Dict[int, str] = field(default_factory=dict)  # code -> ship_id
    
    # IA/Enemigo
    ai_abb_tree: Any = None  # ABB de coordenadas de la IA
    ai_fleet_tree: Any = None  # Árbol N-ario de flota de la IA
    ai_ships: List[ShipInstanceData] = field(default_factory=list)  # Barcos de la IA
    ai_shots: List[ShotData] = field(default_factory=list)  # Disparos de la IA
    ai_occupied_coordinates: Dict[int, str] = field(default_factory=dict)
    ai_last_hits: List[str] = field(default_factory=list)  # Impactos recientes sin hundir
    
    # Control de turnos
    current_turn: str = "player"  # "player" o "ai"
    difficulty: str = "medium"  # "easy", "medium", "hard"
    
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    winner: Optional[str] = None  # "player", "ai", o None
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de la partida."""
        # Estadísticas del jugador (disparos contra la IA)
        player_hits = sum(1 for shot in self.shots if shot.result in ["hit", "sunk"])
        player_misses = sum(1 for shot in self.shots if shot.result == "water")
        
        # Barcos del jugador
        player_ships_sunk = sum(1 for ship in self.ships if ship.is_sunk)
        
        # Barcos de la IA hundidos por el jugador
        ai_ships_sunk = sum(1 for ship in self.ai_ships if ship.is_sunk) if hasattr(self, 'ai_ships') else 0
        print(f"DEBUG get_stats: ai_ships total={len(self.ai_ships) if hasattr(self, 'ai_ships') else 0}, sunk={ai_ships_sunk}")
        
        # Estadísticas de la IA (disparos contra el jugador)
        ai_hits = sum(1 for shot in self.ai_shots if shot.result in ["hit", "sunk"]) if hasattr(self, 'ai_shots') else 0
        ai_misses = sum(1 for shot in self.ai_shots if shot.result == "water") if hasattr(self, 'ai_shots') else 0
        
        # Calcular duración del juego
        if self.finished_at:
            duration = int((self.finished_at - self.created_at).total_seconds())
        else:
            duration = int((datetime.now() - self.created_at).total_seconds())
        
        # Calcular precisión
        accuracy = round((player_hits / len(self.shots) * 100), 2) if len(self.shots) > 0 else 0
        
        return {
            # Disparos del jugador
            "total_shots": len(self.shots),
            "hits": player_hits,
            "misses": player_misses,
            "accuracy": accuracy,
            
            # Barcos del jugador
            "ships_total": len(self.ships),
            "ships_remaining": len(self.ships) - player_ships_sunk,
            "ships_sunk": player_ships_sunk,  # Barcos del jugador hundidos por la IA
            
            # Barcos de la IA
            "enemy_ships_sunk": ai_ships_sunk,  # Barcos de la IA hundidos por el jugador
            
            # Disparos de la IA
            "ai_total_shots": len(self.ai_shots) if hasattr(self, 'ai_shots') else 0,
            "ai_hits": ai_hits,
            "ai_misses": ai_misses,
            
            # Tiempo
            "game_duration_seconds": duration,
            "current_streak": 0  # Placeholder para racha actual
        }
