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
    abb_tree: Any  # Instancia del ABB de coordenadas
    fleet_tree: Any  # Instancia del árbol N-ario de flota
    ships: List[ShipInstanceData] = field(default_factory=list)
    shots: List[ShotData] = field(default_factory=list)
    occupied_coordinates: Dict[int, str] = field(default_factory=dict)  # code -> ship_id
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    
    def get_stats(self) -> Dict[str, int]:
        """Obtiene estadísticas de la partida."""
        hits = sum(1 for shot in self.shots if shot.result in ["hit", "sunk"])
        misses = sum(1 for shot in self.shots if shot.result == "water")
        ships_sunk = sum(1 for ship in self.ships if ship.is_sunk)
        
        return {
            "total_shots": len(self.shots),
            "hits": hits,
            "misses": misses,
            "ships_total": len(self.ships),
            "ships_remaining": len(self.ships) - ships_sunk,
            "ships_sunk": ships_sunk
        }
