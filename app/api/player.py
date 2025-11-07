"""
Endpoints de jugador.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated, Optional

from app.models.game import (
    GameCreate,
    GameResponse,
    GameDetailResponse,
    GameListResponse,
    ShotRequest,
    ShotResponse
)
from app.models.ship import ShipInstance, ShipPlacement
from app.models.board import BaseFleetResponse
from app.core.dependencies import get_current_user
from app.storage.data_models import User
from app.storage.in_memory_store import (
    get_base_fleet,
    get_all_base_fleets,
    get_player_games,
    games_db,
    get_user_by_id,
    get_ship_template
)
from app.services.game_service import GameService


router = APIRouter(prefix="/api/player", tags=["Jugador"])


# ==================== BASE FLEETS (READ ONLY) ====================

@router.get("/available-fleets", response_model=List[BaseFleetResponse])
def list_available_fleets(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Ver flotas base disponibles para jugar.
    
    **Requiere autenticación.**
    """
    fleets = get_all_base_fleets()
    
    result = []
    for f in fleets:
        # Obtener detalles de los barcos
        ships = []
        for template_id in f.ship_template_ids:
            template = get_ship_template(template_id)
            if template:
                ships.append({
                    "id": template.id,
                    "name": template.name,
                    "size": template.size
                })
        
        fleet_response = BaseFleetResponse(
            id=f.id,
            name=f.name,
            board_size=f.board_size,
            ship_template_ids=f.ship_template_ids,
            ship_count=len(f.ship_template_ids),
            created_by=f.created_by,
            created_at=f.created_at
        )
        # Agregar ships como atributo adicional
        fleet_dict = fleet_response.model_dump()
        fleet_dict['ships'] = ships
        result.append(fleet_dict)
    
    return result


@router.get("/base-fleets/{fleet_id}", response_model=BaseFleetResponse)
def get_fleet_details(
    fleet_id: str,
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Obtiene detalles de una flota base específica.
    
    **Requiere autenticación.**
    """
    fleet = get_base_fleet(fleet_id)
    if not fleet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flota base no encontrada"
        )
    
    return BaseFleetResponse(
        id=fleet.id,
        name=fleet.name,
        board_size=fleet.board_size,
        ship_template_ids=fleet.ship_template_ids,
        ship_count=len(fleet.ship_template_ids),
        created_by=fleet.created_by,
        created_at=fleet.created_at
    )


# ==================== MY GAMES ====================

@router.get("/my-games", response_model=GameListResponse)
def list_my_games(
    current_user: Annotated[User, Depends(get_current_user)],
    status: Optional[str] = None
):
    """
    Listar partidas del jugador.
    
    **Requiere autenticación.**
    
    Retorna todas las partidas del jugador actual con su estado.
    
    Args:
        status: Filtrar por estado (opcional): 'in_progress', 'finished', 'setup'
    """
    games = get_player_games(current_user.id)
    
    # Filtrar por estado si se proporciona
    if status:
        games = [g for g in games if g.status == status]
    
    games_response = []
    for game in games:
        stats = game.get_stats(current_user.id)
        games_response.append(
            GameResponse(
                id=game.id,
                player1_id=game.player1_id,
                player2_id=game.player2_id,
                current_turn_player_id=game.current_turn_player_id,
                base_fleet_id=game.base_fleet_id,
                board_size=game.board_size,
                status=game.status,
                is_multiplayer=game.is_multiplayer,
                total_shots=stats["total_shots"],
                hits=stats["hits"],
                misses=stats["misses"],
                ships_total=stats["ships_total"],
                ships_remaining=stats["ships_remaining"],
                ships_sunk=stats["ships_sunk"],
                created_at=game.created_at,
                finished_at=game.finished_at
            )
        )
    
    return GameListResponse(
        total=len(games_response),
        games=games_response
    )


@router.get("/available-multiplayer-games", response_model=dict)
def list_available_multiplayer_games(
    current_user: Annotated[User, Depends(get_current_user)],
    limit: int = 8
):
    """
    Listar partidas multijugador disponibles para unirse.
    
    **Requiere autenticación.**
    
    Retorna partidas que están esperando un segundo jugador.
    
    Args:
        limit: Número máximo de partidas a retornar (default: 8)
    """
    # Filtrar partidas multijugador esperando jugador 2
    available_games = []
    
    for game_id, game in games_db.items():
        # Solo partidas multijugador esperando jugador 2
        if (game.is_multiplayer and 
            game.status == "waiting_for_player2" and 
            game.player1_id != current_user.id):  # No mostrar propias partidas
            
            # Obtener info de la flota
            fleet = get_base_fleet(game.base_fleet_id)
            
            # Obtener nombre del jugador 1
            player1 = get_user_by_id(game.player1_id)
            player1_username = player1.username if player1 else "Desconocido"
            
            available_games.append({
                "id": game.id,
                "player1_id": game.player1_id,
                "player1_username": player1_username,
                "board_size": game.board_size,
                "base_fleet_name": fleet.name if fleet else "Desconocida",
                "ship_count": len(fleet.ship_template_ids) if fleet else 0,
                "created_at": game.created_at.isoformat(),
                "time_waiting": (game.created_at).isoformat()  # Para calcular tiempo en frontend
            })
            
            # Limitar resultados
            if len(available_games) >= limit:
                break
    
    # Ordenar por más recientes primero
    available_games.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "total": len(available_games),
        "games": available_games
    }
