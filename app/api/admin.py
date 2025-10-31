"""
Endpoints de administrador.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Annotated

from app.models.ship import ShipTemplateCreate, ShipTemplateUpdate, ShipTemplateResponse
from app.models.board import BaseFleetCreate, BaseFleetUpdate, BaseFleetResponse
from app.core.dependencies import get_current_admin
from app.storage.data_models import User
from app.storage.in_memory_store import (
    create_ship_template,
    get_ship_template,
    get_all_ship_templates,
    update_ship_template,
    delete_ship_template,
    create_base_fleet,
    get_base_fleet,
    get_all_base_fleets,
    update_base_fleet,
    delete_base_fleet
)


router = APIRouter(prefix="/api/admin", tags=["Administrador"])


# ==================== SHIP TEMPLATES ====================

@router.post("/ship-templates", response_model=ShipTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_ship_template_endpoint(
    template_data: ShipTemplateCreate,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Crea una nueva plantilla de barco.
    
    **Requiere rol de administrador.**
    
    - **name**: Nombre del tipo de barco
    - **size**: Tamaño del barco (1-10 celdas)
    - **description**: Descripción opcional
    """
    template = create_ship_template(
        name=template_data.name,
        size=template_data.size,
        description=template_data.description,
        created_by=current_admin.id
    )
    
    return ShipTemplateResponse(
        id=template.id,
        name=template.name,
        size=template.size,
        description=template.description,
        created_by=template.created_by,
        created_at=template.created_at
    )


@router.get("/ship-templates", response_model=List[ShipTemplateResponse])
def list_ship_templates(
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Lista todas las plantillas de barcos.
    
    **Requiere rol de administrador.**
    """
    templates = get_all_ship_templates()
    
    return [
        ShipTemplateResponse(
            id=t.id,
            name=t.name,
            size=t.size,
            description=t.description,
            created_by=t.created_by,
            created_at=t.created_at
        )
        for t in templates
    ]


@router.get("/ship-templates/{template_id}", response_model=ShipTemplateResponse)
def get_ship_template_endpoint(
    template_id: str,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Obtiene una plantilla de barco por su ID.
    
    **Requiere rol de administrador.**
    """
    template = get_ship_template(template_id)
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla de barco no encontrada"
        )
    
    return ShipTemplateResponse(
        id=template.id,
        name=template.name,
        size=template.size,
        description=template.description,
        created_by=template.created_by,
        created_at=template.created_at
    )


@router.put("/ship-templates/{template_id}", response_model=ShipTemplateResponse)
def update_ship_template_endpoint(
    template_id: str,
    update_data: ShipTemplateUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Actualiza una plantilla de barco.
    
    **Requiere rol de administrador.**
    """
    template = update_ship_template(
        template_id=template_id,
        name=update_data.name,
        size=update_data.size,
        description=update_data.description
    )
    
    if not template:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla de barco no encontrada"
        )
    
    return ShipTemplateResponse(
        id=template.id,
        name=template.name,
        size=template.size,
        description=template.description,
        created_by=template.created_by,
        created_at=template.created_at
    )


@router.delete("/ship-templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ship_template_endpoint(
    template_id: str,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Elimina una plantilla de barco.
    
    **Requiere rol de administrador.**
    """
    deleted = delete_ship_template(template_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plantilla de barco no encontrada"
        )
    
    return None


# ==================== BASE FLEETS ====================

@router.post("/base-fleets", response_model=BaseFleetResponse, status_code=status.HTTP_201_CREATED)
def create_base_fleet_endpoint(
    fleet_data: BaseFleetCreate,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Crea una nueva flota base.
    
    **Requiere rol de administrador.**
    
    - **name**: Nombre de la flota
    - **board_size**: Tamaño del tablero (5-20)
    - **ship_template_ids**: IDs de las plantillas de barcos incluidas
    """
    # Verificar que todas las plantillas existen
    for template_id in fleet_data.ship_template_ids:
        if not get_ship_template(template_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Plantilla de barco {template_id} no encontrada"
            )
    
    fleet = create_base_fleet(
        name=fleet_data.name,
        board_size=fleet_data.board_size,
        ship_template_ids=fleet_data.ship_template_ids,
        created_by=current_admin.id
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


@router.get("/base-fleets", response_model=List[BaseFleetResponse])
def list_base_fleets(
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Lista todas las flotas base.
    
    **Requiere rol de administrador.**
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
def get_base_fleet_endpoint(
    fleet_id: str,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Obtiene una flota base por su ID.
    
    **Requiere rol de administrador.**
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


@router.put("/base-fleets/{fleet_id}", response_model=BaseFleetResponse)
def update_base_fleet_endpoint(
    fleet_id: str,
    update_data: BaseFleetUpdate,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Actualiza una flota base.
    
    **Requiere rol de administrador.**
    """
    # Verificar plantillas si se actualizan
    if update_data.ship_template_ids:
        for template_id in update_data.ship_template_ids:
            if not get_ship_template(template_id):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Plantilla de barco {template_id} no encontrada"
                )
    
    fleet = update_base_fleet(
        fleet_id=fleet_id,
        name=update_data.name,
        board_size=update_data.board_size,
        ship_template_ids=update_data.ship_template_ids
    )
    
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


@router.delete("/base-fleets/{fleet_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_base_fleet_endpoint(
    fleet_id: str,
    current_admin: Annotated[User, Depends(get_current_admin)]
):
    """
    Elimina una flota base.
    
    **Requiere rol de administrador.**
    """
    deleted = delete_base_fleet(fleet_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flota base no encontrada"
        )
    
    return None
