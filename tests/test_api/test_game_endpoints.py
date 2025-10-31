"""
Tests para endpoints de juego.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def setup_game_environment(clean_storage):
    """Helper para configurar entorno de juego."""
    # Registrar jugador
    client.post(
        "/api/auth/register",
        json={
            "username": "player1",
            "password": "pass123",
            "role": "player"
        }
    )
    
    # Login jugador
    player_response = client.post(
        "/api/auth/login",
        json={
            "username": "player1",
            "password": "pass123"
        }
    )
    player_token = player_response.json()["access_token"]
    
    # Login admin
    admin_response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    admin_token = admin_response.json()["access_token"]
    
    # Crear plantillas de barcos
    template1 = client.post(
        "/api/admin/ship-templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Ship1", "size": 3, "description": "Desc"}
    ).json()
    
    template2 = client.post(
        "/api/admin/ship-templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Ship2", "size": 2, "description": "Desc"}
    ).json()
    
    # Crear flota base
    fleet = client.post(
        "/api/admin/base-fleets",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Test Fleet",
            "board_size": 10,
            "ship_template_ids": [template1["id"], template2["id"]]
        }
    ).json()
    
    return {
        "player_token": player_token,
        "admin_token": admin_token,
        "fleet_id": fleet["id"],
        "template_ids": [template1["id"], template2["id"]]
    }


class TestGameCreate:
    """Tests de creación de juego."""
    
    def test_create_game(self, clean_storage):
        """Crear nueva partida."""
        env = setup_game_environment(clean_storage)
        
        response = client.post(
            "/api/game/create",
            headers={"Authorization": f"Bearer {env['player_token']}"},
            json={
                "base_fleet_id": env["fleet_id"]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "setup"
        assert data["board_size"] == 10
        assert "ships_to_place" in data
    
    def test_create_game_without_auth(self, clean_storage):
        """Intentar crear juego sin autenticación."""
        response = client.post(
            "/api/game/create",
            json={
                "base_fleet_id": "some-id"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_game_invalid_fleet(self, clean_storage):
        """Intentar crear juego con flota inválida."""
        env = setup_game_environment(clean_storage)
        
        response = client.post(
            "/api/game/create",
            headers={"Authorization": f"Bearer {env['player_token']}"},
            json={
                "base_fleet_id": "non-existing-fleet"
            }
        )
        
        assert response.status_code == 400


class TestGameBoard:
    """Tests de tablero de juego."""
    
    def test_get_board_state(self, clean_storage):
        """Obtener estado del tablero."""
        env = setup_game_environment(clean_storage)
        
        # Crear juego
        create_response = client.post(
            "/api/game/create",
            headers={"Authorization": f"Bearer {env['player_token']}"},
            json={
                "base_fleet_id": env["fleet_id"]
            }
        )
        
        game_id = create_response.json()["id"]
        
        # Obtener tablero
        response = client.get(
            f"/api/game/{game_id}/board",
            headers={"Authorization": f"Bearer {env['player_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert "board_size" in data
        assert "status" in data
    
    def test_get_board_without_auth(self, clean_storage):
        """Intentar obtener tablero sin autenticación."""
        response = client.get("/api/game/some-id/board")
        
        assert response.status_code == 401


class TestGameStats:
    """Tests de estadísticas de juego."""
    
    def test_get_game_stats(self, clean_storage):
        """Obtener estadísticas del juego."""
        env = setup_game_environment(clean_storage)
        
        # Crear juego
        create_response = client.post(
            "/api/game/create",
            headers={"Authorization": f"Bearer {env['player_token']}"},
            json={
                "base_fleet_id": env["fleet_id"]
            }
        )
        
        game_id = create_response.json()["id"]
        
        # Obtener estadísticas
        response = client.get(
            f"/api/game/{game_id}/stats",
            headers={"Authorization": f"Bearer {env['player_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "game_id" in data
        assert "status" in data
        assert "total_shots" in data
        assert "hits" in data
        assert "misses" in data
        assert "accuracy" in data


class TestGameShotsHistory:
    """Tests de historial de disparos."""
    
    def test_get_shots_history_empty(self, clean_storage):
        """Obtener historial vacío."""
        env = setup_game_environment(clean_storage)
        
        # Crear juego
        create_response = client.post(
            "/api/game/create",
            headers={"Authorization": f"Bearer {env['player_token']}"},
            json={
                "base_fleet_id": env["fleet_id"]
            }
        )
        
        game_id = create_response.json()["id"]
        
        # Obtener historial
        response = client.get(
            f"/api/game/{game_id}/shots-history",
            headers={"Authorization": f"Bearer {env['player_token']}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["shots"]) == 0


class TestGameDelete:
    """Tests de eliminación de juego."""
    
    def test_delete_game(self, clean_storage):
        """Eliminar partida."""
        env = setup_game_environment(clean_storage)
        
        # Crear juego
        create_response = client.post(
            "/api/game/create",
            headers={"Authorization": f"Bearer {env['player_token']}"},
            json={
                "base_fleet_id": env["fleet_id"]
            }
        )
        
        game_id = create_response.json()["id"]
        
        # Eliminar
        response = client.delete(
            f"/api/game/{game_id}",
            headers={"Authorization": f"Bearer {env['player_token']}"}
        )
        
        assert response.status_code == 204
    
    def test_delete_non_existing_game(self, clean_storage):
        """Intentar eliminar juego que no existe."""
        env = setup_game_environment(clean_storage)
        
        response = client.delete(
            "/api/game/non-existing-id",
            headers={"Authorization": f"Bearer {env['player_token']}"}
        )
        
        assert response.status_code == 404
