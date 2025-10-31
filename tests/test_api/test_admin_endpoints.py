"""
Tests para endpoints de administrador.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def get_admin_token():
    """Helper para obtener token de admin."""
    # El admin se crea automáticamente al iniciar
    # Solo necesitamos hacer login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    return None


class TestAdminShipTemplates:
    """Tests de endpoints de plantillas de barcos."""
    
    def test_create_ship_template(self, clean_storage):
        """Crear plantilla de barco."""
        token = get_admin_token()
        
        response = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Portaaviones",
                "size": 5,
                "description": "Barco grande"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Portaaviones"
        assert data["size"] == 5
    
    def test_list_ship_templates(self, clean_storage):
        """Listar plantillas de barcos."""
        token = get_admin_token()
        
        # Crear algunas plantillas
        for i in range(3):
            client.post(
                "/api/admin/ship-templates",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "name": f"Ship{i}",
                    "size": i + 2,
                    "description": f"Ship {i}"
                }
            )
        
        # Listar
        response = client.get(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3
    
    def test_get_ship_template(self, clean_storage):
        """Obtener plantilla específica."""
        token = get_admin_token()
        
        # Crear plantilla
        create_response = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Acorazado",
                "size": 4,
                "description": "Barco mediano"
            }
        )
        
        template_id = create_response.json()["id"]
        
        # Obtener
        response = client.get(
            f"/api/admin/ship-templates/{template_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Acorazado"
    
    def test_update_ship_template(self, clean_storage):
        """Actualizar plantilla de barco."""
        token = get_admin_token()
        
        # Crear plantilla
        create_response = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Crucero",
                "size": 3,
                "description": "Original"
            }
        )
        
        template_id = create_response.json()["id"]
        
        # Actualizar
        response = client.put(
            f"/api/admin/ship-templates/{template_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Crucero Mejorado",
                "size": 4,
                "description": "Actualizado"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Crucero Mejorado"
        assert data["size"] == 4
    
    def test_delete_ship_template(self, clean_storage):
        """Eliminar plantilla de barco."""
        token = get_admin_token()
        
        # Crear plantilla
        create_response = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Submarino",
                "size": 2,
                "description": "Pequeño"
            }
        )
        
        template_id = create_response.json()["id"]
        
        # Eliminar
        response = client.delete(
            f"/api/admin/ship-templates/{template_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 204
        
        # Verificar que no existe
        get_response = client.get(
            f"/api/admin/ship-templates/{template_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert get_response.status_code == 404


class TestAdminBaseFleets:
    """Tests de endpoints de flotas base."""
    
    def test_create_base_fleet(self, clean_storage):
        """Crear flota base."""
        token = get_admin_token()
        
        # Crear plantillas primero
        template1 = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Ship1", "size": 3, "description": "Desc"}
        ).json()
        
        template2 = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Ship2", "size": 2, "description": "Desc"}
        ).json()
        
        # Crear flota
        response = client.post(
            "/api/admin/base-fleets",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Flota Estándar",
                "board_size": 10,
                "ship_template_ids": [template1["id"], template2["id"]]
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Flota Estándar"
        assert data["board_size"] == 10
        assert len(data["ship_template_ids"]) == 2
    
    def test_list_base_fleets(self, clean_storage):
        """Listar flotas base."""
        token = get_admin_token()
        
        # Crear flota
        template = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Ship", "size": 3, "description": "Desc"}
        ).json()
        
        client.post(
            "/api/admin/base-fleets",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Fleet1",
                "board_size": 10,
                "ship_template_ids": [template["id"]]
            }
        )
        
        # Listar
        response = client.get(
            "/api/admin/base-fleets",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1
    
    def test_get_base_fleet(self, clean_storage):
        """Obtener flota base específica."""
        token = get_admin_token()
        
        # Crear flota
        template = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={"name": "Ship", "size": 3, "description": "Desc"}
        ).json()
        
        create_response = client.post(
            "/api/admin/base-fleets",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Fleet Test",
                "board_size": 10,
                "ship_template_ids": [template["id"]]
            }
        )
        
        fleet_id = create_response.json()["id"]
        
        # Obtener
        response = client.get(
            f"/api/admin/base-fleets/{fleet_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Fleet Test"


class TestAdminAuthRequired:
    """Tests de autenticación requerida."""
    
    def test_create_ship_template_without_auth(self, clean_storage):
        """Intentar crear plantilla sin autenticación."""
        response = client.post(
            "/api/admin/ship-templates",
            json={
                "name": "Ship",
                "size": 3,
                "description": "Desc"
            }
        )
        
        assert response.status_code == 401
    
    def test_create_ship_template_as_player(self, clean_storage):
        """Intentar crear plantilla como jugador."""
        # Registrar jugador
        client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "pass123",
                "role": "player"
            }
        )
        
        # Login como jugador
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "player1",
                "password": "pass123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Intentar crear plantilla
        response = client.post(
            "/api/admin/ship-templates",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "name": "Ship",
                "size": 3,
                "description": "Desc"
            }
        )
        
        assert response.status_code == 403
