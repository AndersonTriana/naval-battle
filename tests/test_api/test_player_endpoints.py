"""
Tests para endpoints de jugador.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def get_player_token(clean_storage):
    """Helper para obtener token de jugador."""
    # Registrar y hacer login
    client.post(
        "/api/auth/register",
        json={
            "username": "player1",
            "password": "pass123",
            "role": "player"
        }
    )
    
    response = client.post(
        "/api/auth/login",
        json={
            "username": "player1",
            "password": "pass123"
        }
    )
    return response.json()["access_token"]


def get_admin_token():
    """Helper para obtener token de admin."""
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


class TestPlayerAvailableFleets:
    """Tests de flotas disponibles."""
    
    def test_list_available_fleets(self, clean_storage):
        """Listar flotas disponibles."""
        player_token = get_player_token(clean_storage)
        admin_token = get_admin_token()
        
        # Crear flota como admin
        template = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"name": "Ship", "size": 3, "description": "Desc"}
        ).json()
        
        client.post(
            "/api/admin/base-fleets",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                "name": "Fleet1",
                "board_size": 10,
                "ship_template_ids": [template["id"]]
            }
        )
        
        # Listar como jugador
        response = client.get(
            "/api/player/available-fleets",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_available_fleets_without_auth(self, clean_storage):
        """Intentar listar flotas sin autenticación."""
        response = client.get("/api/player/available-fleets")
        
        assert response.status_code == 401


class TestPlayerMyGames:
    """Tests de mis partidas."""
    
    def test_list_my_games_empty(self, clean_storage):
        """Listar partidas cuando no hay ninguna."""
        player_token = get_player_token(clean_storage)
        
        response = client.get(
            "/api/player/my-games",
            headers={"Authorization": f"Bearer {player_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert len(data["games"]) == 0
    
    def test_my_games_without_auth(self, clean_storage):
        """Intentar listar partidas sin autenticación."""
        response = client.get("/api/player/my-games")
        
        assert response.status_code == 401
