"""
Configuración de fixtures compartidos para pytest.
"""
import pytest
from typing import Generator, Dict, List
from datetime import datetime
import uuid

from app.structures.coordinate_utils import generate_coordinate_codes
from app.storage.data_models import User, ShipTemplate, BaseFleet
import app.storage.in_memory_store as store


@pytest.fixture
def sample_coordinates_5x5() -> List[int]:
    """Fixture: coordenadas para tablero 5x5."""
    return generate_coordinate_codes(5)


@pytest.fixture
def sample_coordinates_10x10() -> List[int]:
    """Fixture: coordenadas para tablero 10x10."""
    return generate_coordinate_codes(10)


@pytest.fixture
def sample_ship_template() -> Dict:
    """Fixture: plantilla de barco de ejemplo."""
    return {
        "id": str(uuid.uuid4()),
        "name": "Portaaviones",
        "size": 5,
        "description": "El barco más grande",
        "created_by": "test-user-id",
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_ship_templates() -> List[Dict]:
    """Fixture: múltiples plantillas de barcos."""
    return [
        {
            "id": str(uuid.uuid4()),
            "name": "Portaaviones",
            "size": 5,
            "description": "Barco grande"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Acorazado",
            "size": 4,
            "description": "Barco mediano"
        },
        {
            "id": str(uuid.uuid4()),
            "name": "Crucero",
            "size": 3,
            "description": "Barco pequeño"
        }
    ]


@pytest.fixture
def sample_base_fleet(sample_ship_templates) -> Dict:
    """Fixture: flota base de ejemplo."""
    ship_ids = [ship["id"] for ship in sample_ship_templates]
    return {
        "id": str(uuid.uuid4()),
        "name": "Flota Clásica",
        "board_size": 10,
        "ship_template_ids": ship_ids,
        "created_by": "test-user-id",
        "created_at": datetime.now()
    }


@pytest.fixture
def sample_user() -> Dict:
    """Fixture: usuario de ejemplo."""
    return {
        "id": str(uuid.uuid4()),
        "username": "testplayer",
        "password": "testpass123",
        "role": "player"
    }


@pytest.fixture
def sample_admin() -> Dict:
    """Fixture: administrador de ejemplo."""
    return {
        "id": str(uuid.uuid4()),
        "username": "testadmin",
        "password": "adminpass123",
        "role": "admin"
    }


@pytest.fixture
def clean_storage() -> Generator:
    """
    Fixture: limpiar almacenamiento en memoria antes y después de cada test.
    
    Guarda el estado actual, limpia los diccionarios, ejecuta el test,
    y luego restaura el estado original.
    """
    # Guardar estado actual
    users_backup = store.users_db.copy()
    ship_templates_backup = store.ship_templates_db.copy()
    base_fleets_backup = store.base_fleets_db.copy()
    games_backup = store.games_db.copy()
    username_to_user_id_backup = store.username_to_user_id.copy()
    player_games_backup = store.player_games.copy()
    
    # Limpiar diccionarios
    store.users_db.clear()
    store.ship_templates_db.clear()
    store.base_fleets_db.clear()
    store.games_db.clear()
    store.username_to_user_id.clear()
    store.player_games.clear()
    
    yield
    
    # Restaurar estado original
    store.users_db.clear()
    store.users_db.update(users_backup)
    store.ship_templates_db.clear()
    store.ship_templates_db.update(ship_templates_backup)
    store.base_fleets_db.clear()
    store.base_fleets_db.update(base_fleets_backup)
    store.games_db.clear()
    store.games_db.update(games_backup)
    store.username_to_user_id.clear()
    store.username_to_user_id.update(username_to_user_id_backup)
    store.player_games.clear()
    store.player_games.update(player_games_backup)


@pytest.fixture
def balanced_coordinates_array() -> List[int]:
    """Fixture: array de coordenadas ordenado para inserción balanceada."""
    # Array pequeño para tests: [11, 12, 13, 14, 15, 16, 17]
    return [11, 12, 13, 14, 15, 16, 17]


@pytest.fixture
def sample_game_data(sample_base_fleet, sample_user) -> Dict:
    """Fixture: datos de juego de ejemplo."""
    return {
        "id": str(uuid.uuid4()),
        "player_id": sample_user["id"],
        "base_fleet_id": sample_base_fleet["id"],
        "board_size": 10,
        "status": "setup"
    }
