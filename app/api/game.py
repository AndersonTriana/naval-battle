"""
Endpoints de juego (Game).
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated, Optional

from app.models.game import (
    GameCreate,
    GameResponse,
    GameDetailResponse,
    ShotRequest,
    ShotResponse,
    ShotHistory,
    JoinGameResponse
)
from app.models.ship import ShipPlacement, ShipInstance
from app.core.dependencies import get_current_user
from app.storage.data_models import User
from app.storage.in_memory_store import get_game, get_base_fleet, get_ship_template, get_user_by_id
from app.services.game_service import GameService


router = APIRouter(prefix="/api/game", tags=["Game"])


@router.post("/create", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_game(
    game_data: GameCreate,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Crear nueva partida.
    
    **Requiere autenticación.**
    
    - **base_fleet_id**: ID de la flota base a utilizar
    
    Proceso:
    1. Genera todas las coordenadas del tablero
    2. Reordena con algoritmo del medio recursivo
    3. Crea ABB balanceado
    4. Crea árbol N-ario para la flota
    5. Estado inicial: "setup"
    """
    result = GameService.create_new_game(
        current_user.id, 
        game_data.base_fleet_id,
        game_data.is_multiplayer
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo crear la partida. Verifica que la flota base existe."
        )
    
    # Obtener información de la flota base
    base_fleet = get_base_fleet(game_data.base_fleet_id)
    
    # Obtener información de los barcos a colocar
    # Importante: si hay barcos duplicados (mismo template_id), cada uno debe aparecer
    ships_to_place = []
    for index, template_id in enumerate(result["ship_template_ids"]):
        template = get_ship_template(template_id)
        if template:
            ships_to_place.append({
                "id": template.id,
                "name": template.name,
                "size": template.size,
                "index": index  # Identificador único para distinguir barcos del mismo tipo
            })
    
    message = "Partida creada. "
    if game_data.is_multiplayer:
        message += "Esperando que se una el jugador 2. Comparte el ID de la partida."
    else:
        message += "Coloca tus barcos para comenzar."
    
    # Obtener nombres de usuario
    player1_user = get_user_by_id(result["player1_id"])
    
    return {
        "id": result["game_id"],
        "player1_id": result["player1_id"],
        "player1_username": player1_user.username if player1_user else "Jugador 1",
        "player2_id": result.get("player2_id"),
        "player2_username": None,
        "current_turn_player_id": result.get("current_turn_player_id"),
        "base_fleet_id": result["base_fleet_id"],
        "board_size": result["board_size"],
        "status": result["status"],
        "is_multiplayer": result["is_multiplayer"],
        "message": message,
        "ships_to_place": ships_to_place,
        "created_at": get_game(result["game_id"]).created_at.isoformat()
    }


@router.post("/{game_id}/join", response_model=dict)
def join_game(
    game_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Unirse a una partida multijugador como jugador 2.
    
    **Requiere autenticación.**
    
    Validaciones:
    - La partida debe existir
    - La partida debe ser multijugador
    - La partida debe estar esperando jugador 2
    - No puedes unirte a tu propia partida
    """
    success, message, result = GameService.join_game(game_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Obtener información de los barcos a colocar
    # Importante: si hay barcos duplicados (mismo template_id), cada uno debe aparecer
    base_fleet = get_base_fleet(result["base_fleet_id"])
    ships_to_place = []
    for index, template_id in enumerate(result["ship_template_ids"]):
        template = get_ship_template(template_id)
        if template:
            ships_to_place.append({
                "id": template.id,
                "name": template.name,
                "size": template.size,
                "index": index  # Identificador único para distinguir barcos del mismo tipo
            })
    
    # Obtener nombres de usuario
    player1_user = get_user_by_id(result["player1_id"])
    player2_user = get_user_by_id(result["player2_id"])
    
    return {
        "message": message,
        "game": {
            "id": result["game_id"],
            "player1_id": result["player1_id"],
            "player1_username": player1_user.username if player1_user else "Jugador 1",
            "player2_id": result["player2_id"],
            "player2_username": player2_user.username if player2_user else "Jugador 2",
            "status": result["status"],
            "board_size": result["board_size"],
            "is_multiplayer": result["is_multiplayer"]
        },
        "ships_to_place": ships_to_place
    }


@router.post("/{game_id}/place-ship", response_model=dict)
def place_ship(
    game_id: str,
    placement: ShipPlacement,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Colocar un barco en el tablero.
    
    **Requiere autenticación.**
    
    - **ship_template_id**: ID de la plantilla de barco
    - **start_coordinate**: Coordenada inicial (ej: "A1")
    - **orientation**: "horizontal" o "vertical"
    
    Validaciones:
    - Coordenada válida para el tablero
    - Barco cabe en el tablero
    - No se superpone con otros barcos
    - Barco pertenece a la flota base
    """
    # Verificar que el juego existe
    game = get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida no encontrada"
        )
    
    # Verificar que el jugador es parte de la partida
    if current_user.id not in [game.player1_id, game.player2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta partida"
        )
    
    success, message, ship_instance = GameService.place_ship(
        game_id=game_id,
        player_id=current_user.id,
        ship_template_id=placement.ship_template_id,
        start_coordinate=placement.start_coordinate,
        orientation=placement.orientation
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    # Calcular barcos restantes por colocar para este jugador
    base_fleet = get_base_fleet(game.base_fleet_id)
    is_player1 = (current_user.id == game.player1_id)
    ships_list = game.player1_ships if is_player1 else game.player2_ships
    ships_remaining = len(base_fleet.ship_template_ids) - len(ships_list)
    
    return {
        "message": "Barco colocado exitosamente",
        "ship": {
            "name": ship_instance.ship_name,
            "coordinates": [seg.coordinate for seg in ship_instance.segments]
        },
        "ships_remaining_to_place": ships_remaining,
        "game_status": game.status
    }


@router.get("/{game_id}/board", response_model=dict)
def get_board_state(
    game_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Obtener estado actual del tablero.
    
    **Requiere autenticación.**
    
    Retorna información completa del tablero incluyendo:
    - Estado de todos los barcos
    - Segmentos y si fueron impactados
    - Estadísticas de disparos
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida no encontrada"
        )
    
    # Verificar que el jugador es parte de la partida
    if current_user.id not in [game.player1_id, game.player2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta partida"
        )
    
    game_detail = GameService.get_game_detail(game_id, current_user.id)
    if not game_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se pudo obtener el estado del juego"
        )
    
    # Determinar qué jugador está consultando
    is_player1 = (current_user.id == game.player1_id)
    stats = game.get_stats(current_user.id)
    
    # Obtener disparos según el jugador
    if is_player1:
        my_shots = game.player1_shots
        enemy_shots = game.player2_shots
    else:
        my_shots = game.player2_shots
        enemy_shots = game.player1_shots
    
    # Formatear disparos
    player_shots = [
        {
            "coordinate": shot.coordinate,
            "result": shot.result,
            "coordinate_code": shot.coordinate_code
        }
        for shot in my_shots
    ]
    
    opponent_shots = [
        {
            "coordinate": shot.coordinate,
            "result": shot.result,
            "coordinate_code": shot.coordinate_code
        }
        for shot in enemy_shots
    ]
    
    # Obtener nombres de usuario
    player1_user = get_user_by_id(game.player1_id)
    player2_user = get_user_by_id(game.player2_id) if game.player2_id else None
    
    return {
        "game_id": game.id,
        "board_size": game.board_size,
        "status": game.status,
        "is_multiplayer": game.is_multiplayer,
        "current_turn_player_id": game.current_turn_player_id,
        "is_my_turn": (game.current_turn_player_id == current_user.id),
        "winner": game.winner,
        "player_ships": game_detail["ships"],
        "player_shots": player_shots,
        "enemy_shots": opponent_shots,
        "total_shots": stats["total_shots"],
        "hits": stats["hits"],
        "misses": stats["misses"],
        "player1_username": player1_user.username if player1_user else "Jugador 1",
        "player2_username": player2_user.username if player2_user else "Esperando..."
    }


@router.post("/{game_id}/shoot", response_model=ShotResponse)
def fire_shot(
    game_id: str,
    shot: ShotRequest,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Realizar un disparo.
    
    **Requiere autenticación.**
    
    - **coordinate**: Coordenada a disparar (ej: "B3")
    
    Validaciones:
    - Juego en estado "in_progress"
    - Coordenada válida
    - No disparar dos veces a la misma coordenada
    
    Proceso:
    1. Convierte coordenada a código
    2. Busca en ABB si hay barco
    3. Actualiza árbol N-ario si hay impacto
    4. Verifica si el barco se hundió
    5. Verifica si todos los barcos se hundieron (fin del juego)
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida no encontrada"
        )
    
    # Verificar que el jugador es parte de la partida
    # En vs IA, player2_id es None, así que solo verificamos player1_id
    valid_players = [game.player1_id]
    if game.player2_id:
        valid_players.append(game.player2_id)
    
    if current_user.id not in valid_players:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta partida"
        )
    
    success, message, result = GameService.fire_shot(game_id, shot.coordinate, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return ShotResponse(
        coordinate=result["coordinate"],
        coordinate_code=result["coordinate_code"],
        result=result["result"],
        ship_hit=result["ship_hit"],
        ship_sunk=result["ship_sunk"],
        game_finished=result.get("game_won", False),
        ai_shot=result.get("ai_shot")  # Incluir disparo de la IA
    )


@router.get("/{game_id}/shots-history", response_model=dict)
def get_shots_history(
    game_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Obtener historial de disparos.
    
    **Requiere autenticación.**
    
    Retorna todos los disparos realizados en la partida con:
    - Coordenada
    - Resultado (water/hit/sunk)
    - Timestamp
    - Barco impactado (si aplica)
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida no encontrada"
        )
    
    # Verificar que el jugador es parte de la partida
    if current_user.id not in [game.player1_id, game.player2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta partida"
        )
    
    # Obtener disparos del jugador actual
    is_player1 = (current_user.id == game.player1_id)
    my_shots = game.player1_shots if is_player1 else game.player2_shots
    
    shots = [
        {
            "coordinate": shot.coordinate,
            "coordinate_code": shot.coordinate_code,
            "result": shot.result,
            "timestamp": shot.timestamp.isoformat()
        }
        for shot in my_shots
    ]
    
    return {
        "total": len(shots),
        "shots": shots
    }


@router.get("/{game_id}/stats", response_model=dict)
def get_game_stats(
    game_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Obtener estadísticas del juego.
    
    **Requiere autenticación.**
    
    Retorna:
    - Total de disparos
    - Impactos y fallos
    - Precisión (%)
    - Barcos hundidos/restantes
    - Duración del juego
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida no encontrada"
        )
    
    # Verificar que el jugador es parte de la partida
    if current_user.id not in [game.player1_id, game.player2_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes acceso a esta partida"
        )
    
    stats = game.get_stats(current_user.id)
    
    # Calcular precisión
    accuracy = 0.0
    if stats["total_shots"] > 0:
        accuracy = (stats["hits"] / stats["total_shots"]) * 100
    
    # Calcular duración del juego
    from datetime import datetime
    duration_minutes = 0
    if game.finished_at:
        duration = game.finished_at - game.created_at
        duration_minutes = int(duration.total_seconds() / 60)
    else:
        duration = datetime.now() - game.created_at
        duration_minutes = int(duration.total_seconds() / 60)
    
    return {
        "game_id": game.id,
        "status": game.status,
        "total_shots": stats["total_shots"],
        "hits": stats["hits"],
        "misses": stats["misses"],
        "accuracy": round(accuracy, 2),
        "ships_total": stats["ships_total"],
        "ships_sunk": stats["ships_sunk"],
        "ships_remaining": stats["ships_remaining"],
        "enemy_ships_sunk": stats["enemy_ships_sunk"],
        "game_duration_minutes": duration_minutes
    }


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Eliminar/abandonar partida.
    
    **Requiere autenticación.**
    
    Solo el jugador dueño puede eliminar su partida.
    """
    game = get_game(game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Partida no encontrada"
        )
    
    # Verificar que el jugador es parte de la partida (solo el creador puede eliminar)
    if current_user.id != game.player1_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo el creador de la partida puede eliminarla"
        )
    
    # Eliminar del storage
    from app.storage.in_memory_store import games_db, player_games
    
    if game_id in games_db:
        del games_db[game_id]
    
    # Eliminar del índice de jugador
    if current_user.id in player_games:
        if game_id in player_games[current_user.id]:
            player_games[current_user.id].remove(game_id)
    
    return None
