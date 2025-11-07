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
    player1_id: str  # Renombrado de player_id
    base_fleet_id: str
    board_size: int
    status: str  # "waiting_for_player2", "player1_setup", "player2_setup", "player1_turn", "player2_turn", "finished"
    is_multiplayer: bool = False  # True para 2 jugadores, False para vs IA
    
    # Jugador 1
    player1_abb_tree: Any = None  # ABB de coordenadas del jugador 1
    player1_fleet_tree: Any = None  # Árbol N-ario de flota del jugador 1
    player1_ships: List[ShipInstanceData] = field(default_factory=list)  # Barcos del jugador 1
    player1_shots: List[ShotData] = field(default_factory=list)  # Disparos del jugador 1
    player1_occupied_coordinates: Dict[int, str] = field(default_factory=dict)  # code -> ship_id
    
    # Jugador 2 / IA
    player2_id: Optional[str] = None  # ID del jugador 2 (None si es IA)
    player2_abb_tree: Any = None  # ABB de coordenadas del jugador 2/IA
    player2_fleet_tree: Any = None  # Árbol N-ario de flota del jugador 2/IA
    player2_ships: List[ShipInstanceData] = field(default_factory=list)  # Barcos del jugador 2/IA
    player2_shots: List[ShotData] = field(default_factory=list)  # Disparos del jugador 2/IA
    player2_occupied_coordinates: Dict[int, str] = field(default_factory=dict)
    player2_last_hits: List[str] = field(default_factory=list)  # Impactos recientes (para IA)
    
    # Control de turnos
    current_turn_player_id: Optional[str] = None  # ID del jugador actual
    difficulty: str = "medium"  # "easy", "medium", "hard" (solo para IA)
    
    created_at: datetime = field(default_factory=datetime.now)
    finished_at: Optional[datetime] = None
    winner: Optional[str] = None  # ID del jugador ganador, o None
    
    def get_stats(self, player_id: Optional[str] = None) -> Dict[str, int]:
        """
        Obtiene estadísticas de la partida.
        
        Args:
            player_id: ID del jugador para el cual obtener stats (None = jugador 1)
        """
        # Determinar qué jugador
        if player_id is None or player_id == self.player1_id:
            my_shots = self.player1_shots
            my_ships = self.player1_ships
            enemy_ships = self.player2_ships
            enemy_shots = self.player2_shots
        else:
            my_shots = self.player2_shots
            my_ships = self.player2_ships
            enemy_ships = self.player1_ships
            enemy_shots = self.player1_shots
        
        # Estadísticas de mis disparos
        player_hits = sum(1 for shot in my_shots if shot.result in ["hit", "sunk"])
        player_misses = sum(1 for shot in my_shots if shot.result == "water")
        
        # Mis barcos
        player_ships_sunk = sum(1 for ship in my_ships if ship.is_sunk)
        
        # Barcos enemigos hundidos
        enemy_ships_sunk = sum(1 for ship in enemy_ships if ship.is_sunk)
        
        # Estadísticas de disparos enemigos
        enemy_hits = sum(1 for shot in enemy_shots if shot.result in ["hit", "sunk"])
        enemy_misses = sum(1 for shot in enemy_shots if shot.result == "water")
        
        # Calcular duración del juego
        if self.finished_at:
            duration = int((self.finished_at - self.created_at).total_seconds())
        else:
            duration = int((datetime.now() - self.created_at).total_seconds())
        
        # Calcular precisión
        accuracy = round((player_hits / len(my_shots) * 100), 2) if len(my_shots) > 0 else 0
        
        return {
            # Mis disparos
            "total_shots": len(my_shots),
            "hits": player_hits,
            "misses": player_misses,
            "accuracy": accuracy,
            
            # Mis barcos
            "ships_total": len(my_ships),
            "ships_remaining": len(my_ships) - player_ships_sunk,
            "ships_sunk": player_ships_sunk,
            
            # Barcos enemigos
            "enemy_ships_sunk": enemy_ships_sunk,
            
            # Disparos enemigos
            "enemy_total_shots": len(enemy_shots),
            "enemy_hits": enemy_hits,
            "enemy_misses": enemy_misses,
            
            # Tiempo
            "game_duration_seconds": duration,
            "current_streak": 0
        }
