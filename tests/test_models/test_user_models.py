"""
Tests para modelos Pydantic de usuarios.
Valida la validación de datos de usuarios.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models.user import (
    UserRole,
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse
)


class TestUserRole:
    """Tests del enum UserRole."""
    
    def test_user_role_admin(self):
        """Verificar que rol admin existe."""
        assert UserRole.ADMIN == "admin"
    
    def test_user_role_player(self):
        """Verificar que rol player existe."""
        assert UserRole.PLAYER == "player"
    
    def test_user_role_values(self):
        """Verificar todos los valores del enum."""
        roles = [role.value for role in UserRole]
        assert "admin" in roles
        assert "player" in roles
        assert len(roles) == 2


class TestUserCreate:
    """Tests del modelo UserCreate."""
    
    def test_user_create_valid(self):
        """Crear usuario con datos válidos."""
        user = UserCreate(
            username="player1",
            password="123456",
            role=UserRole.PLAYER
        )
        assert user.username == "player1"
        assert user.password == "123456"
        assert user.role == UserRole.PLAYER
    
    def test_user_create_default_role(self):
        """Verificar que el rol por defecto es player."""
        user = UserCreate(username="player1", password="123456")
        assert user.role == UserRole.PLAYER
    
    def test_user_create_admin_role(self):
        """Crear usuario con rol admin."""
        user = UserCreate(
            username="admin1",
            password="admin123",
            role=UserRole.ADMIN
        )
        assert user.role == UserRole.ADMIN


class TestUserCreateValidation:
    """Tests de validación del modelo UserCreate."""
    
    def test_user_create_invalid_username_too_short(self):
        """Validar que username muy corto falla."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="ab", password="123456")
        
        errors = exc_info.value.errors()
        assert any("username" in str(error) for error in errors)
    
    def test_user_create_invalid_username_too_long(self):
        """Validar que username muy largo falla."""
        long_username = "a" * 51
        with pytest.raises(ValidationError):
            UserCreate(username=long_username, password="123456")
    
    def test_user_create_invalid_password_too_short(self):
        """Validar que password muy corto falla."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(username="player1", password="12345")
        
        errors = exc_info.value.errors()
        assert any("password" in str(error) for error in errors)
    
    def test_user_create_valid_minimum_length(self):
        """Verificar longitudes mínimas válidas."""
        user = UserCreate(username="abc", password="123456")
        assert user.username == "abc"
        assert user.password == "123456"
    
    def test_user_create_valid_maximum_length(self):
        """Verificar longitudes máximas válidas."""
        username = "a" * 50
        user = UserCreate(username=username, password="123456")
        assert len(user.username) == 50


class TestUserLogin:
    """Tests del modelo UserLogin."""
    
    def test_user_login_valid(self):
        """Crear modelo de login válido."""
        login = UserLogin(username="player1", password="123456")
        assert login.username == "player1"
        assert login.password == "123456"
    
    def test_user_login_required_fields(self):
        """Verificar que todos los campos son requeridos."""
        with pytest.raises(ValidationError):
            UserLogin(username="player1")
        
        with pytest.raises(ValidationError):
            UserLogin(password="123456")


class TestUserResponse:
    """Tests del modelo UserResponse."""
    
    def test_user_response_valid(self):
        """Crear respuesta de usuario válida."""
        user = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            username="player1",
            role=UserRole.PLAYER,
            created_at=datetime.now()
        )
        assert user.id == "550e8400-e29b-41d4-a716-446655440000"
        assert user.username == "player1"
        assert user.role == UserRole.PLAYER
        assert isinstance(user.created_at, datetime)
    
    def test_user_response_required_fields(self):
        """Verificar que todos los campos son requeridos."""
        with pytest.raises(ValidationError):
            UserResponse(
                username="player1",
                role=UserRole.PLAYER,
                created_at=datetime.now()
            )


class TestTokenResponse:
    """Tests del modelo TokenResponse."""
    
    def test_token_response_valid(self):
        """Crear respuesta de token válida."""
        user = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            username="player1",
            role=UserRole.PLAYER,
            created_at=datetime.now()
        )
        
        token = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            token_type="bearer",
            user=user
        )
        
        assert token.access_token.startswith("eyJ")
        assert token.token_type == "bearer"
        assert token.user.username == "player1"
    
    def test_token_response_default_token_type(self):
        """Verificar que token_type tiene valor por defecto."""
        user = UserResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            username="player1",
            role=UserRole.PLAYER,
            created_at=datetime.now()
        )
        
        token = TokenResponse(
            access_token="token123",
            user=user
        )
        
        assert token.token_type == "bearer"
