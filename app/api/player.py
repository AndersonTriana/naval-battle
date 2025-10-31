"""
Endpoints de jugador.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated

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
    get_player_games
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
    
    return [
        BaseFleetResponse(
            id=f.id,
            name=f.name,
            board_size=f.board_size,
            ship_template_ids=f.ship_template_ids,
            ship_count=len(f.ship_template_ids),
            created_by=f.created_by,
            created_at=f.created_at
        )
        for f in fleets
    ]


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
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Listar partidas del jugador.
    
    **Requiere autenticación.**
    
    Retorna todas las partidas del jugador actual con su estado.
    """
    games = get_player_games(current_user.id)
    
    games_response = []
    for game in games:
        stats = game.get_stats()
        games_response.append(
            GameResponse(
                id=game.id,
                player_id=game.player_id,
                base_fleet_id=game.base_fleet_id,
                board_size=game.board_size,
                status=game.status,
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
