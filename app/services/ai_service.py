"""
Servicio de Inteligencia Artificial para el juego de Batalla Naval.
Implementa estrategias de colocación de barcos y disparo.
"""
import random
from typing import List, Tuple, Optional
from app.structures.coordinate_utils import (
    coordinate_to_code,
    code_to_coordinate,
    validate_coordinate,
    get_adjacent_coordinates
)


class AIService:
    """Servicio de IA para el juego."""
    
    @staticmethod
    def place_ships_randomly(
        ship_templates: List[dict],
        board_size: int,
        occupied_coordinates: set = None
    ) -> List[dict]:
        """
        Coloca barcos aleatoriamente en el tablero.
        
        Args:
            ship_templates: Lista de plantillas de barcos a colocar
            board_size: Tamaño del tablero
            occupied_coordinates: Coordenadas ya ocupadas (opcional)
        
        Returns:
            Lista de barcos colocados con formato:
            [{"template_id": "...", "start": "A1", "orientation": "horizontal"}, ...]
        """
        if occupied_coordinates is None:
            occupied_coordinates = set()
        
        placed_ships = []
        
        for template in ship_templates:
            ship_id = template.get("id")
            ship_size = template.get("size", 3)
            max_attempts = 100
            placed = False
            
            for _ in range(max_attempts):
                # Elegir orientación aleatoria
                orientation = random.choice(["horizontal", "vertical"])
                
                # Elegir coordenada inicial aleatoria
                if orientation == "horizontal":
                    max_row = board_size
                    max_col = board_size - ship_size + 1
                else:
                    max_row = board_size - ship_size + 1
                    max_col = board_size
                
                row = random.randint(1, max_row)
                col = random.randint(1, max_col)
                
                # Convertir a coordenada
                letter = chr(ord('A') + row - 1)
                start_coord = f"{letter}{col}"
                
                # Validar que no se superponga
                try:
                    coords = get_adjacent_coordinates(start_coord, board_size, orientation, ship_size)
                    
                    # Verificar si alguna coordenada está ocupada
                    coords_codes = {coordinate_to_code(c, board_size) for c in coords}
                    if not coords_codes.intersection(occupied_coordinates):
                        # Colocar barco
                        placed_ships.append({
                            "template_id": ship_id,
                            "start": start_coord,
                            "orientation": orientation,
                            "coordinates": coords
                        })
                        
                        # Marcar coordenadas como ocupadas
                        occupied_coordinates.update(coords_codes)
                        placed = True
                        break
                        
                except ValueError:
                    # Coordenada inválida, intentar de nuevo
                    continue
            
            if not placed:
                raise Exception(f"No se pudo colocar el barco {ship_id} después de {max_attempts} intentos")
        
        return placed_ships
    
    @staticmethod
    def get_next_shot(
        board_size: int,
        shots_history: List[dict],
        last_hits: List[str] = None,
        difficulty: str = "medium"
    ) -> str:
        """
        Determina la siguiente coordenada a disparar según la estrategia de la IA.
        
        Args:
            board_size: Tamaño del tablero
            shots_history: Historial de disparos [{"coordinate": "A1", "result": "water"}, ...]
            last_hits: Lista de impactos recientes sin hundir
            difficulty: Nivel de dificultad ("easy", "medium", "hard")
        
        Returns:
            Coordenada a disparar (ej: "B5")
        """
        # Crear set de coordenadas ya disparadas
        shot_coords = {shot["coordinate"] for shot in shots_history}
        
        # Estrategia según dificultad
        if difficulty == "hard" and last_hits:
            # Modo cazador: hay impactos sin hundir
            coord = AIService._hunt_mode(board_size, shot_coords, last_hits)
            if coord:
                return coord
        
        elif difficulty == "medium" and last_hits:
            # 70% probabilidad de modo cazador
            if random.random() < 0.7:
                coord = AIService._hunt_mode(board_size, shot_coords, last_hits)
                if coord:
                    return coord
        
        # Modo búsqueda: disparo aleatorio o en patrón
        if difficulty == "hard":
            # Patrón de tablero de ajedrez para ser más eficiente
            coord = AIService._checkerboard_pattern(board_size, shot_coords)
            if coord:
                return coord
        
        # Disparo completamente aleatorio
        return AIService._random_shot(board_size, shot_coords)
    
    @staticmethod
    def _hunt_mode(board_size: int, shot_coords: set, last_hits: List[str]) -> Optional[str]:
        """
        Modo cazador: dispara alrededor de impactos recientes.
        
        Args:
            board_size: Tamaño del tablero
            shot_coords: Coordenadas ya disparadas
            last_hits: Lista de impactos recientes
        
        Returns:
            Coordenada a disparar o None
        """
        # Obtener el último impacto
        last_hit = last_hits[-1]
        
        # Intentar disparar en las 4 direcciones (arriba, abajo, izquierda, derecha)
        directions = [
            (0, 1),   # Derecha
            (0, -1),  # Izquierda
            (1, 0),   # Abajo
            (-1, 0)   # Arriba
        ]
        
        # Convertir coordenada a índices
        letter = last_hit[0]
        number = int(last_hit[1:])
        row = ord(letter) - ord('A') + 1
        col = number
        
        # Barajar direcciones para variar
        random.shuffle(directions)
        
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            
            # Validar que esté dentro del tablero
            if 1 <= new_row <= board_size and 1 <= new_col <= board_size:
                new_letter = chr(ord('A') + new_row - 1)
                new_coord = f"{new_letter}{new_col}"
                
                if new_coord not in shot_coords:
                    return new_coord
        
        return None
    
    @staticmethod
    def _checkerboard_pattern(board_size: int, shot_coords: set) -> Optional[str]:
        """
        Dispara en patrón de tablero de ajedrez (más eficiente).
        
        Args:
            board_size: Tamaño del tablero
            shot_coords: Coordenadas ya disparadas
        
        Returns:
            Coordenada a disparar o None
        """
        candidates = []
        
        for row in range(1, board_size + 1):
            for col in range(1, board_size + 1):
                # Patrón de ajedrez: suma de fila+columna es par
                if (row + col) % 2 == 0:
                    letter = chr(ord('A') + row - 1)
                    coord = f"{letter}{col}"
                    
                    if coord not in shot_coords:
                        candidates.append(coord)
        
        return random.choice(candidates) if candidates else None
    
    @staticmethod
    def _random_shot(board_size: int, shot_coords: set) -> str:
        """
        Disparo completamente aleatorio.
        
        Args:
            board_size: Tamaño del tablero
            shot_coords: Coordenadas ya disparadas
        
        Returns:
            Coordenada a disparar
        """
        max_attempts = board_size * board_size
        
        for _ in range(max_attempts):
            row = random.randint(1, board_size)
            col = random.randint(1, board_size)
            
            letter = chr(ord('A') + row - 1)
            coord = f"{letter}{col}"
            
            if coord not in shot_coords:
                return coord
        
        # Si llegamos aquí, el tablero está lleno (no debería pasar)
        raise Exception("No hay coordenadas disponibles para disparar")
