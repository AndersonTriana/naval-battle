"""
Servicio para gestión de partidas.
"""
from typing import Optional, List
from datetime import datetime

from app.services.board_service import BoardService
from app.services.ship_service import ShipService
from app.storage.in_memory_store import (
    create_game,
    get_game,
    get_base_fleet,
    get_ship_template,
    update_game_status
)
from app.storage.data_models import ShotData, ShipInstanceData
from app.structures.coordinate_utils import coordinate_to_code, validate_coordinate


class GameService:
    """Servicio para gestión de partidas."""
    
    @staticmethod
    def create_new_game(player_id: str, base_fleet_id: str) -> Optional[dict]:
        """
        Crea una nueva partida para un jugador.
        
        Args:
            player_id: ID del jugador
            base_fleet_id: ID de la flota base a utilizar
        
        Returns:
            Diccionario con información de la partida o None si hay error
        """
        # Verificar que la flota base existe
        base_fleet = get_base_fleet(base_fleet_id)
        if not base_fleet:
            return None
        
        # Crear ABB balanceado para el tablero
        abb_tree = BoardService.create_balanced_bst(base_fleet.board_size)
        
        # Crear árbol N-ario para la flota
        fleet_tree = ShipService.create_fleet_tree(player_id)
        
        # Crear la partida
        game = create_game(
            player_id=player_id,
            base_fleet_id=base_fleet_id,
            board_size=base_fleet.board_size,
            abb_tree=abb_tree,
            fleet_tree=fleet_tree
        )
        
        return {
            "game_id": game.id,
            "player_id": game.player_id,
            "base_fleet_id": game.base_fleet_id,
            "board_size": game.board_size,
            "status": game.status,
            "available_ships": len(base_fleet.ship_template_ids),
            "ship_template_ids": base_fleet.ship_template_ids
        }
    
    @staticmethod
    def place_ship(
        game_id: str,
        ship_template_id: str,
        start_coordinate: str,
        orientation: str
    ) -> tuple[bool, str, Optional[ShipInstanceData]]:
        """
        Coloca un barco en el tablero de una partida.
        
        Args:
            game_id: ID de la partida
            ship_template_id: ID de la plantilla de barco
            start_coordinate: Coordenada inicial
            orientation: "horizontal" o "vertical"
        
        Returns:
            Tupla (éxito, mensaje, instancia_barco)
        """
        game = get_game(game_id)
        if not game:
            return False, "Partida no encontrada", None
        
        if game.status != "setup":
            return False, "Solo se pueden colocar barcos en fase de configuración", None
        
        # Validar que la coordenada es válida para el tablero
        if not validate_coordinate(start_coordinate, game.board_size):
            return False, f"Coordenada {start_coordinate} inválida para tablero {game.board_size}x{game.board_size}", None
        
        # Obtener plantilla del barco
        template = get_ship_template(ship_template_id)
        if not template:
            return False, "Plantilla de barco no encontrada", None
        
        # Validar colocación
        is_valid, message, coordinates = ShipService.validate_ship_placement(
            game.board_size,
            start_coordinate,
            orientation,
            template.size,
            game.occupied_coordinates
        )
        
        if not is_valid:
            return False, message, None
        
        # Crear instancia del barco
        ship_instance = ShipService.create_ship_instance(ship_template_id, coordinates, game.board_size)
        if not ship_instance:
            return False, "Error al crear instancia del barco", None
        
        # Agregar barco al árbol N-ario
        ShipService.add_ship_to_fleet(game.fleet_tree, ship_instance)
        
        # Marcar coordenadas como ocupadas
        for coord in coordinates:
            code = coordinate_to_code(coord, game.board_size)
            game.occupied_coordinates[code] = ship_template_id
        
        # Agregar a la lista de barcos del juego
        game.ships.append(ship_instance)
        
        # Verificar si todos los barcos fueron colocados
        # Si es así, iniciar automáticamente el juego e inicializar la IA
        base_fleet = get_base_fleet(game.base_fleet_id)
        if len(game.ships) == len(base_fleet.ship_template_ids):
            # Inicializar IA
            from app.services.ai_service import AIService
            from app.services.board_service import BoardService
            from app.structures.n_ary_tree import NaryTree
            
            # Crear tablero de la IA
            game.ai_abb_tree = BoardService.create_balanced_bst(game.board_size)
            game.ai_fleet_tree = NaryTree({"type": "fleet", "player": "ai"})
            
            # Obtener plantillas de barcos
            ship_templates = []
            for ship_template_id in base_fleet.ship_template_ids:
                template = get_ship_template(ship_template_id)
                if template:
                    ship_templates.append({
                        "id": ship_template_id,
                        "size": template.size,
                        "name": template.name
                    })
            
            # Colocar barcos de la IA aleatoriamente
            ai_placements = AIService.place_ships_randomly(
                ship_templates,
                game.board_size,
                set()
            )
            
            # Crear instancias de barcos de la IA
            for placement in ai_placements:
                ai_ship = ShipService.create_ship_instance(
                    placement["template_id"],
                    placement["coordinates"],
                    game.board_size
                )
                if ai_ship:
                    game.ai_ships.append(ai_ship)
                    ShipService.add_ship_to_fleet(game.ai_fleet_tree, ai_ship)
                    
                    # Marcar coordenadas como ocupadas
                    for coord in placement["coordinates"]:
                        code = coordinate_to_code(coord, game.board_size)
                        game.ai_occupied_coordinates[code] = placement["template_id"]
            
            game.status = "in_progress"
            game.current_turn = "player"
        
        return True, "Barco colocado exitosamente", ship_instance
    
    @staticmethod
    def start_game(game_id: str) -> tuple[bool, str]:
        """
        Inicia una partida (cambia de setup a in_progress).
        
        Args:
            game_id: ID de la partida
        
        Returns:
            Tupla (éxito, mensaje)
        """
        game = get_game(game_id)
        if not game:
            return False, "Partida no encontrada"
        
        if game.status != "setup":
            return False, "La partida ya fue iniciada"
        
        if len(game.ships) == 0:
            return False, "Debes colocar al menos un barco antes de iniciar"
        
        update_game_status(game_id, "in_progress")
        return True, "Partida iniciada exitosamente"
    
    @staticmethod
    def fire_shot(game_id: str, coordinate: str) -> tuple[bool, str, Optional[dict]]:
        """
        Realiza un disparo del jugador contra la IA.
        
        Args:
            game_id: ID de la partida
            coordinate: Coordenada a disparar
        
        Returns:
            Tupla (éxito, mensaje, resultado_disparo)
        """
        game = get_game(game_id)
        if not game:
            return False, "Partida no encontrada", None
        
        if game.status != "in_progress":
            return False, "La partida no está en progreso", None
        
        if game.current_turn != "player":
            return False, "No es tu turno", None
        
        # Validar coordenada
        if not validate_coordinate(coordinate, game.board_size):
            return False, f"Coordenada {coordinate} inválida", None
        
        coordinate_code = coordinate_to_code(coordinate, game.board_size)
        
        # Verificar si ya fue disparada (en el tablero de la IA)
        if BoardService.is_coordinate_shot(game.ai_abb_tree, coordinate, game.board_size):
            return False, "Esta coordenada ya fue disparada", None
        
        # Marcar como disparada en el ABB de la IA
        BoardService.mark_coordinate_as_shot(game.ai_abb_tree, coordinate, game.board_size)
        
        # Verificar si hay un barco de la IA en esa coordenada
        ship_node = ShipService.find_ship_by_coordinate(game.ai_fleet_tree, coordinate_code)
        
        result = "water"
        ship_hit_name = None
        ship_sunk = False
        game_finished = False
        
        if ship_node:
            # Impacto en barco de la IA
            segment_found, is_sunk = ShipService.hit_ship_segment(
                game.ai_fleet_tree,
                ship_node,
                coordinate_code
            )
            
            if segment_found:
                result = "sunk" if is_sunk else "hit"
                ship_hit_name = ship_node.data.get("ship_name")
                ship_sunk = is_sunk
                
                # Actualizar estado del barco de la IA en la lista
                ship_template_id = ship_node.data.get("ship_template_id")
                for ship in game.ai_ships:
                    if ship.ship_template_id == ship_template_id:
                        # Marcar segmento como impactado
                        for segment in ship.segments:
                            if segment.coordinate_code == coordinate_code:
                                segment.is_hit = True
                        
                        # Verificar si todos los segmentos están impactados
                        all_segments_hit = all(seg.is_hit for seg in ship.segments)
                        
                        # Si todos los segmentos están impactados, el barco está hundido
                        if all_segments_hit:
                            ship.is_sunk = True
                            print(f"DEBUG: Barco IA hundido: {ship.ship_name} (template_id: {ship_template_id})")
                        break
                
                # Verificar si todos los barcos de la IA fueron hundidos
                fleet_status = ShipService.get_fleet_status(game.ai_fleet_tree)
                if fleet_status["all_ships_sunk"]:
                    game.status = "finished"
                    game.winner = "player"
                    game.finished_at = datetime.now()
                    game_finished = True
        
        # Registrar disparo del jugador
        shot = ShotData(
            coordinate=coordinate,
            coordinate_code=coordinate_code,
            result=result,
            timestamp=datetime.now()
        )
        game.shots.append(shot)
        
        # Cambiar turno a la IA si el juego no terminó
        if not game_finished:
            game.current_turn = "ai"
            
            # Turno de la IA
            ai_shot_result = GameService._ai_turn(game)
        else:
            ai_shot_result = None
        
        shot_result = {
            "coordinate": coordinate,
            "coordinate_code": coordinate_code,
            "result": result,
            "ship_hit": ship_hit_name,
            "ship_sunk": ship_sunk,
            "game_won": game_finished,
            "ai_shot": ai_shot_result  # Incluir disparo de la IA
        }
        
        # Volver turno al jugador
        if not game_finished:
            game.current_turn = "player"
        
        return True, "Disparo realizado", shot_result
    
    @staticmethod
    def _ai_turn(game: 'Game') -> Optional[dict]:
        """
        Ejecuta el turno de la IA.
        
        Args:
            game: Instancia del juego
        
        Returns:
            Resultado del disparo de la IA o None si hay error
        """
        from app.services.ai_service import AIService
        
        # Obtener siguiente coordenada a disparar
        ai_coordinate = AIService.get_next_shot(
            game.board_size,
            [{"coordinate": s.coordinate, "result": s.result} for s in game.ai_shots],
            game.ai_last_hits,
            game.difficulty
        )
        
        coordinate_code = coordinate_to_code(ai_coordinate, game.board_size)
        
        # Marcar como disparada en el ABB del jugador
        BoardService.mark_coordinate_as_shot(game.abb_tree, ai_coordinate, game.board_size)
        
        # Verificar si hay un barco del jugador en esa coordenada
        ship_node = ShipService.find_ship_by_coordinate(game.fleet_tree, coordinate_code)
        
        result = "water"
        ship_hit_name = None
        ship_sunk = False
        
        if ship_node:
            # Impacto en barco del jugador
            segment_found, is_sunk = ShipService.hit_ship_segment(
                game.fleet_tree,
                ship_node,
                coordinate_code
            )
            
            if segment_found:
                result = "sunk" if is_sunk else "hit"
                ship_hit_name = ship_node.data.get("ship_name")
                ship_sunk = is_sunk
                
                # Actualizar estado del barco del jugador
                for ship in game.ships:
                    if ship.ship_template_id == ship_node.data.get("ship_template_id"):
                        for segment in ship.segments:
                            if segment.coordinate_code == coordinate_code:
                                segment.is_hit = True
                        if is_sunk:
                            ship.is_sunk = True
                            # Remover de last_hits si se hundió
                            game.ai_last_hits = []
                        break
                
                # Si fue impacto pero no hundido, agregar a last_hits
                if result == "hit":
                    game.ai_last_hits.append(ai_coordinate)
                
                # Verificar si todos los barcos del jugador fueron hundidos
                fleet_status = ShipService.get_fleet_status(game.fleet_tree)
                if fleet_status["all_ships_sunk"]:
                    game.status = "finished"
                    game.winner = "ai"
                    game.finished_at = datetime.now()
        
        # Registrar disparo de la IA
        ai_shot = ShotData(
            coordinate=ai_coordinate,
            coordinate_code=coordinate_code,
            result=result,
            timestamp=datetime.now()
        )
        game.ai_shots.append(ai_shot)
        
        return {
            "coordinate": ai_coordinate,
            "result": result,
            "ship_hit": ship_hit_name,
            "ship_sunk": ship_sunk
        }
    
    @staticmethod
    def get_game_detail(game_id: str) -> Optional[dict]:
        """
        Obtiene los detalles completos de una partida.
        
        Args:
            game_id: ID de la partida
        
        Returns:
            Diccionario con detalles de la partida o None
        """
        game = get_game(game_id)
        if not game:
            return None
        
        stats = game.get_stats()
        
        # Obtener lista de barcos desde el árbol N-ario
        ships_list = ShipService.get_ships_list(game.fleet_tree)
        
        # Convertir disparos a formato de respuesta
        shot_history = [
            {
                "coordinate": shot.coordinate,
                "coordinate_code": shot.coordinate_code,
                "result": shot.result,
                "timestamp": shot.timestamp.isoformat()
            }
            for shot in game.shots
        ]
        
        return {
            "game": {
                "id": game.id,
                "player_id": game.player_id,
                "base_fleet_id": game.base_fleet_id,
                "board_size": game.board_size,
                "status": game.status,
                "total_shots": stats["total_shots"],
                "hits": stats["hits"],
                "misses": stats["misses"],
                "ships_total": stats["ships_total"],
                "ships_remaining": stats["ships_remaining"],
                "ships_sunk": stats["ships_sunk"],
                "created_at": game.created_at.isoformat(),
                "finished_at": game.finished_at.isoformat() if game.finished_at else None
            },
            "ships": ships_list,
            "shot_history": shot_history
        }
    
    @staticmethod
    def check_game_finished(fleet_tree) -> bool:
        """
        Verifica si todos los barcos de la flota están hundidos.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
        
        Returns:
            True si todos los barcos están hundidos
        
        Proceso:
            - Recorrer todos los barcos en el árbol
            - Para cada barco, verificar si todos sus segmentos is_hit=True
            - Si algún barco tiene segmentos intactos, retornar False
        """
        fleet_status = ShipService.get_fleet_status(fleet_tree)
        return fleet_status["all_ships_sunk"]
    
    @staticmethod
    def validate_shot(game, coordinate: str) -> tuple[bool, str]:
        """
        Valida que un disparo sea permitido.
        
        Args:
            game: Instancia del juego
            coordinate: Coordenada del disparo
        
        Returns:
            (es_valido, mensaje_error)
        
        Validaciones:
            1. Juego debe estar en status "in_progress"
            2. Coordenada debe ser válida para el tablero
            3. Coordenada no debe haber sido disparada antes
        """
        from app.structures.coordinate_utils import validate_coordinate
        from app.services.board_service import BoardService
        
        # Validar estado del juego
        if game.status != "in_progress":
            return False, "El juego no está en progreso"
        
        # Validar formato de coordenada
        if not validate_coordinate(coordinate, game.board_size):
            return False, f"Coordenada '{coordinate}' inválida para tablero {game.board_size}x{game.board_size}"
        
        # Verificar que no haya sido disparada antes
        if BoardService.is_coordinate_shot(game.abb_tree, coordinate):
            return False, f"La coordenada '{coordinate}' ya fue disparada"
        
        return True, ""
    
    @staticmethod
    def validate_fleet_fits_board(board_size: int, ship_sizes: list[int]) -> tuple[bool, str]:
        """
        Valida que los barcos de la flota puedan caber en el tablero.
        
        Regla: La suma de tamaños de barcos no debe exceder el 20% del tablero
        
        Args:
            board_size: Tamaño del tablero
            ship_sizes: Lista de tamaños de barcos
        
        Returns:
            (es_valido, mensaje_error)
        
        Ejemplo:
            Tablero 10x10 = 100 celdas
            Máximo permitido = 20 celdas
            Flota: [5, 4, 3, 3, 2] = 17 celdas ✅
            Flota: [5, 5, 5, 5, 5] = 25 celdas ❌
        """
        total_cells = board_size * board_size
        max_allowed = int(total_cells * 0.20)
        total_ship_cells = sum(ship_sizes)
        
        if total_ship_cells > max_allowed:
            return False, f"Los barcos ocupan {total_ship_cells} celdas, máximo permitido: {max_allowed} (20% del tablero)"
        
        return True, ""
