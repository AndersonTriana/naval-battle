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
    update_game_status,
    join_game_as_player2
)
from app.storage.data_models import ShotData, ShipInstanceData
from app.structures.coordinate_utils import coordinate_to_code, validate_coordinate


class GameService:
    """Servicio para gestión de partidas."""
    
    @staticmethod
    def create_new_game(player1_id: str, base_fleet_id: str, is_multiplayer: bool = False) -> Optional[dict]:
        """
        Crea una nueva partida para un jugador.
        
        Args:
            player1_id: ID del jugador 1
            base_fleet_id: ID de la flota base a utilizar
            is_multiplayer: True para juego de 2 jugadores, False para vs IA
        
        Returns:
            Diccionario con información de la partida o None si hay error
        """
        # Verificar que la flota base existe
        base_fleet = get_base_fleet(base_fleet_id)
        if not base_fleet:
            return None
        
        # Crear ABB balanceado para el tablero del jugador 1
        player1_abb_tree = BoardService.create_balanced_bst(base_fleet.board_size)
        
        # Crear árbol N-ario para la flota del jugador 1
        player1_fleet_tree = ShipService.create_fleet_tree(player1_id)
        
        # Crear la partida
        game = create_game(
            player1_id=player1_id,
            base_fleet_id=base_fleet_id,
            board_size=base_fleet.board_size,
            player1_abb_tree=player1_abb_tree,
            player1_fleet_tree=player1_fleet_tree,
            is_multiplayer=is_multiplayer
        )
        
        return {
            "game_id": game.id,
            "player1_id": game.player1_id,
            "player2_id": game.player2_id,
            "current_turn_player_id": game.current_turn_player_id,
            "base_fleet_id": game.base_fleet_id,
            "board_size": game.board_size,
            "status": game.status,
            "is_multiplayer": game.is_multiplayer,
            "available_ships": len(base_fleet.ship_template_ids),
            "ship_template_ids": base_fleet.ship_template_ids
        }
    
    @staticmethod
    def join_game(game_id: str, player2_id: str) -> tuple[bool, str, Optional[dict]]:
        """
        Permite que un segundo jugador se una a una partida multijugador.
        
        Args:
            game_id: ID de la partida
            player2_id: ID del jugador 2
        
        Returns:
            Tupla (éxito, mensaje, datos_partida)
        """
        game = get_game(game_id)
        if not game:
            return False, "Partida no encontrada", None
        
        if not game.is_multiplayer:
            return False, "Esta partida no es multijugador", None
        
        if game.status != "waiting_for_player2":
            return False, "La partida no está esperando jugadores", None
        
        if game.player1_id == player2_id:
            return False, "No puedes unirte a tu propia partida", None
        
        # Obtener información de la flota
        base_fleet = get_base_fleet(game.base_fleet_id)
        if not base_fleet:
            return False, "Flota base no encontrada", None
        
        # Crear ABB balanceado para el tablero del jugador 2
        player2_abb_tree = BoardService.create_balanced_bst(base_fleet.board_size)
        
        # Crear árbol N-ario para la flota del jugador 2
        player2_fleet_tree = ShipService.create_fleet_tree(player2_id)
        
        # Unir jugador 2 a la partida
        updated_game = join_game_as_player2(
            game_id,
            player2_id,
            player2_abb_tree,
            player2_fleet_tree
        )
        
        if not updated_game:
            return False, "Error al unirse a la partida", None
        
        return True, "Te has unido exitosamente a la partida", {
            "game_id": updated_game.id,
            "player1_id": updated_game.player1_id,
            "player2_id": updated_game.player2_id,
            "current_turn_player_id": updated_game.current_turn_player_id,
            "base_fleet_id": updated_game.base_fleet_id,
            "board_size": updated_game.board_size,
            "status": updated_game.status,
            "is_multiplayer": updated_game.is_multiplayer,
            "available_ships": len(base_fleet.ship_template_ids),
            "ship_template_ids": base_fleet.ship_template_ids
        }
    
    @staticmethod
    def place_ship(
        game_id: str,
        player_id: str,
        ship_template_id: str,
        start_coordinate: str,
        orientation: str
    ) -> tuple[bool, str, Optional[ShipInstanceData]]:
        """
        Coloca un barco en el tablero de una partida.
        
        Args:
            game_id: ID de la partida
            player_id: ID del jugador que coloca el barco
            ship_template_id: ID de la plantilla de barco
            start_coordinate: Coordenada inicial
            orientation: "horizontal" o "vertical"
        
        Returns:
            Tupla (éxito, mensaje, instancia_barco)
        """
        game = get_game(game_id)
        if not game:
            return False, "Partida no encontrada", None
        
        # Determinar qué jugador está colocando
        is_player1 = (player_id == game.player1_id)
        is_player2 = (player_id == game.player2_id)
        
        if not is_player1 and not is_player2:
            return False, "No eres parte de esta partida", None
        
        # Validar estado del juego según el modo
        if game.is_multiplayer:
            # Modo multijugador: ambos jugadores pueden colocar simultáneamente
            valid_setup_states = ["both_players_setup", "waiting_for_player2", "player1_setup", "player2_setup"]
            if game.status not in valid_setup_states:
                return False, "No se pueden colocar barcos en esta fase del juego", None
            
            # Validar que el jugador no haya terminado ya de colocar todos sus barcos
            base_fleet = get_base_fleet(game.base_fleet_id)
            if is_player1 and len(game.player1_ships) >= len(base_fleet.ship_template_ids):
                return False, "Ya has colocado todos tus barcos", None
            if is_player2 and len(game.player2_ships) >= len(base_fleet.ship_template_ids):
                return False, "Ya has colocado todos tus barcos", None
        else:
            # Modo vs IA: solo jugador 1 puede colocar
            if game.status != "setup":
                return False, "Solo se pueden colocar barcos en fase de configuración", None
        
        # Validar que la coordenada es válida para el tablero
        if not validate_coordinate(start_coordinate, game.board_size):
            return False, f"Coordenada {start_coordinate} inválida para tablero {game.board_size}x{game.board_size}", None
        
        # Obtener plantilla del barco
        template = get_ship_template(ship_template_id)
        if not template:
            return False, "Plantilla de barco no encontrada", None
        
        # Seleccionar estructuras según el jugador
        if is_player1:
            fleet_tree = game.player1_fleet_tree
            occupied_coords = game.player1_occupied_coordinates
            ships_list = game.player1_ships
        else:  # is_player2
            fleet_tree = game.player2_fleet_tree
            occupied_coords = game.player2_occupied_coordinates
            ships_list = game.player2_ships
        
        # Validar colocación
        is_valid, message, coordinates = ShipService.validate_ship_placement(
            game.board_size,
            start_coordinate,
            orientation,
            template.size,
            occupied_coords
        )
        
        if not is_valid:
            return False, message, None
        
        # Crear instancia del barco
        ship_instance = ShipService.create_ship_instance(ship_template_id, coordinates, game.board_size)
        if not ship_instance:
            return False, "Error al crear instancia del barco", None
        
        # Agregar barco al árbol N-ario
        ShipService.add_ship_to_fleet(fleet_tree, ship_instance)
        
        # Marcar coordenadas como ocupadas
        for coord in coordinates:
            code = coordinate_to_code(coord, game.board_size)
            occupied_coords[code] = ship_template_id
        
        # Agregar a la lista de barcos del juego
        ships_list.append(ship_instance)
        
        # Verificar si todos los barcos fueron colocados y actualizar estado
        base_fleet = get_base_fleet(game.base_fleet_id)
        
        if game.is_multiplayer:
            # Modo multijugador: verificar si ambos jugadores terminaron de colocar barcos
            player1_ready = len(game.player1_ships) >= len(base_fleet.ship_template_ids)
            player2_ready = game.player2_id and len(game.player2_ships) >= len(base_fleet.ship_template_ids)
            
            # Si ambos jugadores terminaron, iniciar el juego
            if player1_ready and player2_ready:
                game.status = "player1_turn"
                game.current_turn_player_id = game.player1_id
        else:
            # Modo vs IA: inicializar IA cuando jugador 1 termine
            if len(game.player1_ships) == len(base_fleet.ship_template_ids):
                from app.services.ai_service import AIService
                from app.structures.n_ary_tree import NaryTree
                
                # Crear tablero de la IA (player2)
                game.player2_abb_tree = BoardService.create_balanced_bst(game.board_size)
                game.player2_fleet_tree = NaryTree({"type": "fleet", "player": "ai"})
                
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
                        game.player2_ships.append(ai_ship)
                        ShipService.add_ship_to_fleet(game.player2_fleet_tree, ai_ship)
                        
                        # Marcar coordenadas como ocupadas
                        for coord in placement["coordinates"]:
                            code = coordinate_to_code(coord, game.board_size)
                            game.player2_occupied_coordinates[code] = placement["template_id"]
                
                game.status = "in_progress"
                game.current_turn_player_id = game.player1_id
        
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
    def fire_shot(game_id: str, coordinate: str, player_id: str = None) -> tuple[bool, str, Optional[dict]]:
        """
        Realiza un disparo (vs IA o multijugador).
        
        Args:
            game_id: ID de la partida
            coordinate: Coordenada a disparar
            player_id: ID del jugador que dispara (requerido para multijugador)
        
        Returns:
            Tupla (éxito, mensaje, resultado_disparo)
        """
        game = get_game(game_id)
        if not game:
            return False, "Partida no encontrada", None
        
        # Validar que el juego esté en progreso
        valid_playing_states = ["in_progress", "player1_turn", "player2_turn"]
        if game.status not in valid_playing_states:
            return False, "La partida no está en progreso", None
        
        # Variable para rastrear si es player1 (usada en multijugador)
        is_player1 = False
        
        # Modo multijugador
        if game.is_multiplayer:
            if not player_id:
                return False, "ID de jugador requerido", None
            
            # Validar turno
            if game.current_turn_player_id != player_id:
                return False, "No es tu turno", None
            
            # Determinar quién dispara y a quién
            is_player1 = (player_id == game.player1_id)
            target_abb_tree = game.player2_abb_tree if is_player1 else game.player1_abb_tree
            target_fleet_tree = game.player2_fleet_tree if is_player1 else game.player1_fleet_tree
            target_ships = game.player2_ships if is_player1 else game.player1_ships
            shooter_shots = game.player1_shots if is_player1 else game.player2_shots
            
        else:
            # Modo vs IA: usa player2_* para la IA
            # Verificar que los atributos de IA existan
            if not game.player2_abb_tree:
                return False, "El juego no está correctamente inicializado. Coloca todos tus barcos primero.", None
            
            target_abb_tree = game.player2_abb_tree
            target_fleet_tree = game.player2_fleet_tree
            target_ships = game.player2_ships
            shooter_shots = game.player1_shots
        
        # Validar coordenada
        if not validate_coordinate(coordinate, game.board_size):
            return False, f"Coordenada {coordinate} inválida", None
        
        coordinate_code = coordinate_to_code(coordinate, game.board_size)
        
        # Verificar si ya fue disparada
        if BoardService.is_coordinate_shot(target_abb_tree, coordinate, game.board_size):
            return False, "Esta coordenada ya fue disparada", None
        
        # Marcar como disparada en el ABB del objetivo
        BoardService.mark_coordinate_as_shot(target_abb_tree, coordinate, game.board_size)
        
        # Verificar si hay un barco en esa coordenada
        ship_node = ShipService.find_ship_by_coordinate(target_fleet_tree, coordinate_code)
        
        result = "water"
        ship_hit_name = None
        ship_sunk = False
        game_finished = False
        
        if ship_node:
            # Impacto en barco
            segment_found, is_sunk = ShipService.hit_ship_segment(
                target_fleet_tree,
                ship_node,
                coordinate_code
            )
            
            if segment_found:
                result = "sunk" if is_sunk else "hit"
                ship_hit_name = ship_node.data.get("ship_name")
                ship_sunk = is_sunk
                
                # Actualizar estado del barco en la lista
                # Buscar el barco por coordenada en lugar de solo por template_id
                # para manejar correctamente múltiples barcos del mismo tipo
                for ship in target_ships:
                    # Verificar si este barco contiene la coordenada impactada
                    ship_has_coordinate = any(seg.coordinate_code == coordinate_code for seg in ship.segments)
                    if ship_has_coordinate:
                        # Marcar segmento como impactado
                        for segment in ship.segments:
                            if segment.coordinate_code == coordinate_code:
                                segment.is_hit = True
                        
                        # Verificar si todos los segmentos están impactados
                        all_segments_hit = all(seg.is_hit for seg in ship.segments)
                        
                        # Si todos los segmentos están impactados, el barco está hundido
                        if all_segments_hit:
                            ship.is_sunk = True
                            print(f"🔴 DEBUG: Barco {ship.ship_name} marcado como hundido. is_sunk={ship.is_sunk}")
                            print(f"🔴 DEBUG: target_ships es player1_ships={target_ships is game.player1_ships}, player2_ships={target_ships is game.player2_ships}")
                            print(f"🔴 DEBUG: ID del barco en memoria: {id(ship)}")
                        break
                
                # Verificar si todos los barcos fueron hundidos
                fleet_status = ShipService.get_fleet_status(target_fleet_tree)
                if fleet_status["all_ships_sunk"]:
                    if game.is_multiplayer:
                        # Determinar ganador
                        game.status = "player1_won" if is_player1 else "player2_won"
                        game.winner = game.player1_id if is_player1 else game.player2_id
                    else:
                        game.status = "finished"
                        game.winner = "player"
                    game.finished_at = datetime.now()
                    game_finished = True
        
        # Registrar disparo
        shot = ShotData(
            coordinate=coordinate,
            coordinate_code=coordinate_code,
            result=result,
            timestamp=datetime.now()
        )
        shooter_shots.append(shot)
        
        # Cambiar turno
        ai_shot_result = None
        if not game_finished:
            if game.is_multiplayer:
                # Cambiar turno al otro jugador
                if is_player1:
                    game.status = "player2_turn"
                    game.current_turn_player_id = game.player2_id
                else:
                    game.status = "player1_turn"
                    game.current_turn_player_id = game.player1_id
            else:
                # Modo vs IA
                game.current_turn = "ai"
                ai_shot_result = GameService._ai_turn(game)
                game.current_turn = "player"
        
        shot_result = {
            "coordinate": coordinate,
            "coordinate_code": coordinate_code,
            "result": result,
            "ship_hit": ship_hit_name,
            "ship_sunk": ship_sunk,
            "game_won": game_finished,
            "ai_shot": ai_shot_result  # Solo para vs IA
        }
        
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
            [{"coordinate": s.coordinate, "result": s.result} for s in game.player2_shots],
            game.player2_last_hits,
            game.difficulty
        )
        
        coordinate_code = coordinate_to_code(ai_coordinate, game.board_size)
        
        # Marcar como disparada en el ABB del jugador
        BoardService.mark_coordinate_as_shot(game.player1_abb_tree, ai_coordinate, game.board_size)
        
        # Verificar si hay un barco del jugador en esa coordenada
        ship_node = ShipService.find_ship_by_coordinate(game.player1_fleet_tree, coordinate_code)
        
        result = "water"
        ship_hit_name = None
        ship_sunk = False
        
        if ship_node:
            # Impacto en barco del jugador
            segment_found, is_sunk = ShipService.hit_ship_segment(
                game.player1_fleet_tree,
                ship_node,
                coordinate_code
            )
            
            if segment_found:
                result = "sunk" if is_sunk else "hit"
                ship_hit_name = ship_node.data.get("ship_name")
                ship_sunk = is_sunk
                
                # Actualizar estado del barco del jugador
                for ship in game.player1_ships:
                    if ship.ship_template_id == ship_node.data.get("ship_template_id"):
                        for segment in ship.segments:
                            if segment.coordinate_code == coordinate_code:
                                segment.is_hit = True
                        if is_sunk:
                            ship.is_sunk = True
                            # Remover de last_hits si se hundió
                            game.player2_last_hits = []
                        break
                
                # Si fue impacto pero no hundido, agregar a last_hits
                if result == "hit":
                    game.player2_last_hits.append(ai_coordinate)
                
                # Verificar si todos los barcos del jugador fueron hundidos
                fleet_status = ShipService.get_fleet_status(game.player1_fleet_tree)
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
        game.player2_shots.append(ai_shot)
        
        return {
            "coordinate": ai_coordinate,
            "result": result,
            "ship_hit": ship_hit_name,
            "ship_sunk": ship_sunk
        }
    
    @staticmethod
    def get_game_detail(game_id: str, player_id: str = None) -> Optional[dict]:
        """
        Obtiene los detalles completos de una partida.
        
        Args:
            game_id: ID de la partida
            player_id: ID del jugador (requerido para multijugador)
        
        Returns:
            Diccionario con detalles de la partida o None
        """
        game = get_game(game_id)
        if not game:
            return None
        
        # Determinar qué jugador está consultando (para multijugador)
        if game.is_multiplayer:
            if not player_id:
                return None
            
            is_player1 = (player_id == game.player1_id)
            stats = game.get_stats(player_id)
            
            # Obtener barcos del jugador
            fleet_tree = game.player1_fleet_tree if is_player1 else game.player2_fleet_tree
            ships_list = ShipService.get_ships_list(fleet_tree)
            
            # Obtener disparos del jugador
            shots = game.player1_shots if is_player1 else game.player2_shots
        else:
            # Modo vs IA: mostrar barcos del jugador (player1)
            stats = game.get_stats()
            ships_list = ShipService.get_ships_list(game.player1_fleet_tree) if game.player1_fleet_tree else []
            shots = game.player1_shots
        
        # Convertir disparos a formato de respuesta
        shot_history = [
            {
                "coordinate": shot.coordinate,
                "coordinate_code": shot.coordinate_code,
                "result": shot.result,
                "timestamp": shot.timestamp.isoformat()
            }
            for shot in shots
        ]
        
        return {
            "game": {
                "id": game.id,
                "player1_id": game.player1_id if game.is_multiplayer else getattr(game, 'player_id', game.player1_id),
                "player2_id": game.player2_id if game.is_multiplayer else None,
                "base_fleet_id": game.base_fleet_id,
                "board_size": game.board_size,
                "status": game.status,
                "is_multiplayer": game.is_multiplayer,
                "winner": game.winner,
                "total_shots": stats["total_shots"],
                "hits": stats["hits"],
                "misses": stats["misses"],
                "ships_total": stats["ships_total"],
                "ships_remaining": stats["ships_remaining"],
                "ships_sunk": stats["ships_sunk"],
                "enemy_ships_sunk": stats["enemy_ships_sunk"],
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
