"""
Tests para endpoints de autenticación.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


class TestAuthRegister:
    """Tests del endpoint de registro."""
    
    def test_register_new_user(self, clean_storage):
        """Registrar nuevo usuario."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "newplayer",
                "password": "password123",
                "role": "player"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newplayer"
        assert data["role"] == "player"
        assert "id" in data
    
    def test_register_duplicate_username(self, clean_storage):
        """Intentar registrar username duplicado."""
        # Registrar primer usuario
        client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "pass123",
                "role": "player"
            }
        )
        
        # Intentar registrar con mismo username
        response = client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "pass456",
                "role": "player"
            }
        )
        
        assert response.status_code == 409
    
    def test_register_invalid_password(self, clean_storage):
        """Registrar con contraseña inválida."""
        response = client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "123",  # Muy corta
                "role": "player"
            }
        )
        
        assert response.status_code == 422


class TestAuthLogin:
    """Tests del endpoint de login."""
    
    def test_login_success(self, clean_storage):
        """Login exitoso."""
        # Registrar usuario
        client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "password123",
                "role": "player"
            }
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "username": "player1",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "player1"
    
    def test_login_wrong_password(self, clean_storage):
        """Login con contraseña incorrecta."""
        # Registrar usuario
        client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "password123",
                "role": "player"
            }
        )
        
        # Login con contraseña incorrecta
        response = client.post(
            "/api/auth/login",
            json={
                "username": "player1",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_non_existing_user(self, clean_storage):
        """Login con usuario que no existe."""
        response = client.post(
            "/api/auth/login",
            json={
                "username": "nonexistent",
                "password": "password123"
            }
        )
        
        assert response.status_code == 401


class TestAuthMe:
    """Tests del endpoint /me."""
    
    def test_get_current_user(self, clean_storage):
        """Obtener información del usuario actual."""
        # Registrar y hacer login
        client.post(
            "/api/auth/register",
            json={
                "username": "player1",
                "password": "password123",
                "role": "player"
            }
        )
        
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": "player1",
                "password": "password123"
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Obtener info del usuario
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "player1"
        assert data["role"] == "player"
    
    def test_get_current_user_without_token(self, clean_storage):
        """Intentar obtener info sin token."""
        response = client.get("/api/auth/me")
        
        assert response.status_code == 401
