"""
Tests de integración para endpoints de modo multijugador.
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
    return {"player1": user1, "player2": user2}


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
    """Obtener headers de autenticación para ambos jugadores."""
    # Login player1
    response1 = client.post(
        "/api/auth/login",
        data={"username": "player1", "password": "password123"}
    )
    token1 = response1.json()["access_token"]
    
    # Login player2
    response2 = client.post(
        "/api/auth/login",
        data={"username": "player2", "password": "password456"}
    )
    token2 = response2.json()["access_token"]
    
    return {
        "player1": {"Authorization": f"Bearer {token1}"},
        "player2": {"Authorization": f"Bearer {token2}"}
    }


class TestMultiplayerGameFlow:
    """Tests del flujo completo de una partida multijugador."""
    
    def test_complete_multiplayer_game_flow(self, test_users, test_fleet, auth_headers):
        """Flujo completo: crear, unirse, colocar barcos."""
        # 1. Jugador 1 crea partida multijugador
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_multiplayer"] is True
        assert data["status"] == "waiting_for_player2"
        assert "Esperando que se una el jugador 2" in data["message"]
        
        game_id = data["id"]
        
        # 2. Jugador 2 se une a la partida
        response = client.post(
            f"/api/game/{game_id}/join",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["game"]["status"] == "player1_setup"
        assert data["game"]["player2_id"] == test_users["player2"].id
        
        # 3. Jugador 1 coloca sus barcos
        response = client.post(
            f"/api/game/{game_id}/place-ship",
            json={
                "ship_template_id": test_fleet.ship_template_ids[0],
                "start_coordinate": "A1",
                "orientation": "horizontal"
            },
            headers=auth_headers["player1"]
        )
        assert response.status_code == 200
        assert response.json()["ships_remaining_to_place"] == 1
        
        response = client.post(
            f"/api/game/{game_id}/place-ship",
            json={
                "ship_template_id": test_fleet.ship_template_ids[1],
                "start_coordinate": "B1",
                "orientation": "horizontal"
            },
            headers=auth_headers["player1"]
        )
        assert response.status_code == 200
        assert response.json()["ships_remaining_to_place"] == 0
        assert response.json()["game_status"] == "player2_setup"
        
        # 4. Jugador 2 coloca sus barcos
        response = client.post(
            f"/api/game/{game_id}/place-ship",
            json={
                "ship_template_id": test_fleet.ship_template_ids[0],
                "start_coordinate": "C1",
                "orientation": "horizontal"
            },
            headers=auth_headers["player2"]
        )
        assert response.status_code == 200
        
        response = client.post(
            f"/api/game/{game_id}/place-ship",
            json={
                "ship_template_id": test_fleet.ship_template_ids[1],
                "start_coordinate": "D1",
                "orientation": "horizontal"
            },
            headers=auth_headers["player2"]
        )
        assert response.status_code == 200
        assert response.json()["game_status"] == "player1_turn"
        
        # 5. Verificar estado del tablero para jugador 1
        response = client.get(
            f"/api/game/{game_id}/board",
            headers=auth_headers["player1"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_multiplayer"] is True
        assert data["is_my_turn"] is True
        assert data["current_turn_player_id"] == test_users["player1"].id
        
        # 6. Verificar estado del tablero para jugador 2
        response = client.get(
            f"/api/game/{game_id}/board",
            headers=auth_headers["player2"]
        )
        assert response.status_code == 200
        data = response.json()
        assert data["is_my_turn"] is False
    
    def test_create_vs_ai_game(self, test_users, test_fleet, auth_headers):
        """Crear partida vs IA (modo clásico)."""
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": False
            },
            headers=auth_headers["player1"]
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["is_multiplayer"] is False
        assert data["status"] == "setup"
        assert "Coloca tus barcos" in data["message"]
    
    def test_join_non_existent_game(self, test_users, test_fleet, auth_headers):
        """Intentar unirse a una partida que no existe."""
        response = client.post(
            "/api/game/fake-game-id/join",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 400
        assert "no encontrada" in response.json()["detail"].lower()
    
    def test_join_own_game(self, test_users, test_fleet, auth_headers):
        """Intentar unirse a tu propia partida."""
        # Crear partida
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        game_id = response.json()["id"]
        
        # Intentar unirse a propia partida
        response = client.post(
            f"/api/game/{game_id}/join",
            headers=auth_headers["player1"]
        )
        
        assert response.status_code == 400
        assert "propia partida" in response.json()["detail"].lower()
    
    def test_player2_cannot_place_during_player1_setup(self, test_users, test_fleet, auth_headers):
        """Jugador 2 no puede colocar barcos durante setup de jugador 1."""
        # Crear y unir partida
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
        
        # Jugador 2 intenta colocar barco
        response = client.post(
            f"/api/game/{game_id}/place-ship",
            json={
                "ship_template_id": test_fleet.ship_template_ids[0],
                "start_coordinate": "A1",
                "orientation": "horizontal"
            },
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 400
        assert "turno" in response.json()["detail"].lower()
    
    def test_get_stats_for_each_player(self, test_users, test_fleet, auth_headers):
        """Obtener estadísticas individuales para cada jugador."""
        # Crear y preparar partida completa
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        game_id = response.json()["id"]
        
        client.post(f"/api/game/{game_id}/join", headers=auth_headers["player2"])
        
        # Colocar barcos de ambos jugadores
        for coord in ["A1", "B1"]:
            idx = 0 if coord == "A1" else 1
            client.post(
                f"/api/game/{game_id}/place-ship",
                json={
                    "ship_template_id": test_fleet.ship_template_ids[idx],
                    "start_coordinate": coord,
                    "orientation": "horizontal"
                },
                headers=auth_headers["player1"]
            )
        
        for coord in ["C1", "D1"]:
            idx = 0 if coord == "C1" else 1
            client.post(
                f"/api/game/{game_id}/place-ship",
                json={
                    "ship_template_id": test_fleet.ship_template_ids[idx],
                    "start_coordinate": coord,
                    "orientation": "horizontal"
                },
                headers=auth_headers["player2"]
            )
        
        # Obtener stats de jugador 1
        response = client.get(
            f"/api/game/{game_id}/stats",
            headers=auth_headers["player1"]
        )
        assert response.status_code == 200
        stats1 = response.json()
        assert stats1["ships_total"] == 2
        
        # Obtener stats de jugador 2
        response = client.get(
            f"/api/game/{game_id}/stats",
            headers=auth_headers["player2"]
        )
        assert response.status_code == 200
        stats2 = response.json()
        assert stats2["ships_total"] == 2
    
    def test_unauthorized_access_to_game(self, test_users, test_fleet, auth_headers):
        """Usuario no autorizado no puede acceder a la partida."""
        # Crear partida
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": False
            },
            headers=auth_headers["player1"]
        )
        game_id = response.json()["id"]
        
        # Jugador 2 intenta acceder al tablero de jugador 1
        response = client.get(
            f"/api/game/{game_id}/board",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 403
        assert "acceso" in response.json()["detail"].lower()


class TestMultiplayerGameDeletion:
    """Tests de eliminación de partidas multijugador."""
    
    def test_only_creator_can_delete(self, test_users, test_fleet, auth_headers):
        """Solo el creador puede eliminar la partida."""
        # Crear y unir partida
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": test_fleet.id,
                "is_multiplayer": True
            },
            headers=auth_headers["player1"]
        )
        game_id = response.json()["id"]
        
        client.post(f"/api/game/{game_id}/join", headers=auth_headers["player2"])
        
        # Jugador 2 intenta eliminar
        response = client.delete(
            f"/api/game/{game_id}",
            headers=auth_headers["player2"]
        )
        
        assert response.status_code == 403
        assert "creador" in response.json()["detail"].lower()
        
        # Jugador 1 elimina exitosamente
        response = client.delete(
            f"/api/game/{game_id}",
            headers=auth_headers["player1"]
        )
        
        assert response.status_code == 204
