"""
Tests para el endpoint de partidas disponibles.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage.in_memory_store import (
    create_user,
    create_ship_template,
    create_base_fleet,
    games_db,
    users_db,
    ship_templates_db,
    base_fleets_db
)
from app.services.game_service import GameService


client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_database():
    """Limpiar base de datos antes de cada test."""
    games_db.clear()
    users_db.clear()
    ship_templates_db.clear()
    base_fleets_db.clear()
    yield
    games_db.clear()
    users_db.clear()
    ship_templates_db.clear()
    base_fleets_db.clear()


@pytest.fixture
def test_users():
    """Crear usuarios de prueba."""
    user1 = create_user("player1", "password123", "player")
    user2 = create_user("player2", "password456", "player")
    user3 = create_user("player3", "password789", "player")
    return {"player1": user1, "player2": user2, "player3": user3}


@pytest.fixture
def test_fleet():
    """Crear flota de prueba."""
    ship1 = create_ship_template("Lancha", 2, "Barco pequeño", "admin")
    ship2 = create_ship_template("Submarino", 3, "Barco mediano", "admin")
    
    fleet = create_base_fleet(
        "Flota de Prueba",
        5,
        [ship1.id, ship2.id],
        "admin"
    )
    
    return fleet


@pytest.fixture
def auth_headers(test_users):
    """Obtener headers de autenticación."""
    response1 = client.post(
        "/api/auth/login",
        data={"username": "player1", "password": "password123"}
    )
    token1 = response1.json()["access_token"]
    
    response2 = client.post(
        "/api/auth/login",
        data={"username": "player2", "password": "password456"}
    )
    token2 = response2.json()["access_token"]
    
    response3 = client.post(
        "/api/auth/login",
        data={"username": "player3", "password": "password789"}
    )
    token3 = response3.json()["access_token"]
    
    return {
        "player1": {"Authorization": f"Bearer {token1}"},
        "player2": {"Authorization": f"Bearer {token2}"},
        "player3": {"Authorization": f"Bearer {token3}"}
    }


class TestAvailableGames:
    """Tests del endpoint de partidas disponibles."""
    
    def test_get_available_games_empty(self, test_users, test_fleet, auth_headers):
        """Obtener lista vacía cuando no hay partidas."""
        response = client.get(
            "/api/player/available-multiplayer-games",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["games"] == []
    
    def test_get_available_games_with_waiting_games(self, test_users, test_fleet, auth_headers):
        """Obtener partidas esperando jugador 2."""
        # Player 1 crea partida multijugador
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        assert response.status_code == 201
        
        # Player 2 consulta partidas disponibles
        response = client.get(
            "/api/player/available-multiplayer-games",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["games"]) == 1
        
        game = data["games"][0]
        assert game["player1_id"] == test_users["player1"].id
        assert game["board_size"] == 5
        assert game["base_fleet_name"] == "Flota de Prueba"
        assert game["ship_count"] == 2
    
    def test_own_games_not_shown(self, test_users, test_fleet, auth_headers):
        """Las propias partidas no aparecen en la lista."""
        # Player 1 crea partida
        client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        
        # Player 1 consulta (no debe ver su propia partida)
        response = client.get(
            "/api/player/available-multiplayer-games",
            headers=auth_headers["player1"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
    
    def test_limit_parameter(self, test_users, test_fleet, auth_headers):
        """Verificar que el parámetro limit funciona."""
        # Crear 5 partidas
        for i in range(5):
            client.post(
                "/api/game/create",
                json={
                    "base_fleet_id": test_fleet.id,
                    "is_multiplayer": True
                },
                headers=auth_headers["player1"]
            )
        
        # Consultar con límite de 3
        response = client.get(
            "/api/player/available-multiplayer-games?limit=3",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["games"]) == 3
    
    def test_only_waiting_games_shown(self, test_users, test_fleet, auth_headers):
        """Solo se muestran partidas en estado waiting_for_player2."""
        # Crear partida y que player2 se una
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        game_id = response.json()["id"]
        
        client.post(
            f"/api/game/{game_id}/join",
            headers=auth_headers["player2"]
        )
        
        # Player 3 consulta (no debe ver la partida que ya tiene player2)
        response = client.get(
            "/api/player/available-multiplayer-games",
            headers=auth_headers["player3"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
