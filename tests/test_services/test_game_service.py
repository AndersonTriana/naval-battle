"""
Tests para GameService.
"""
import pytest
from app.services.game_service import GameService
from app.storage.in_memory_store import (
    create_ship_template,
    create_base_fleet,
    create_user
)


class TestGameServiceValidations:
    """Tests de validaciones de GameService."""
    
    def test_validate_fleet_fits_board_valid(self):
        """Validar que flota cabe en tablero."""
        # Tablero 10x10 = 100 celdas, máximo 20 celdas
        ship_sizes = [5, 4, 3, 3, 2]  # Total: 17 celdas
        
        is_valid, msg = GameService.validate_fleet_fits_board(10, ship_sizes)
        
        assert is_valid is True
        assert msg == ""
    
    def test_validate_fleet_too_large(self):
        """Validar que flota muy grande no cabe."""
        # Tablero 10x10 = 100 celdas, máximo 20 celdas
        ship_sizes = [10, 10, 10]  # Total: 30 celdas (>20)
        
        is_valid, msg = GameService.validate_fleet_fits_board(10, ship_sizes)
        
        assert is_valid is False
        assert "máximo permitido" in msg
    
    def test_validate_fleet_edge_case(self):
        """Validar caso límite (exactamente 20%)."""
        # Tablero 10x10 = 100 celdas, máximo 20 celdas
        ship_sizes = [5, 5, 5, 5]  # Total: 20 celdas (exacto)
        
        is_valid, msg = GameService.validate_fleet_fits_board(10, ship_sizes)
        
        assert is_valid is True


class TestGameServiceCreateGame:
    """Tests de creación de juegos."""
    
    def test_create_new_game(self, clean_storage):
        """Crear nueva partida."""
        # Crear usuario
        user = create_user("player1", "pass123", "player")
        
        # Crear plantillas de barcos
        template1 = create_ship_template("Ship1", 3, "Desc", user.id)
        template2 = create_ship_template("Ship2", 2, "Desc", user.id)
        
        # Crear flota base
        fleet = create_base_fleet(
            "Fleet1",
            10,
            [template1.id, template2.id],
            user.id
        )
        
        # Crear juego
        result = GameService.create_new_game(user.id, fleet.id)
        
        assert result is not None
        assert "game_id" in result
        assert result["player_id"] == user.id
        assert result["status"] == "setup"
        assert result["board_size"] == 10


class TestGameServiceGetGameDetail:
    """Tests de obtener detalles del juego."""
    
    def test_get_game_detail_non_existing(self):
        """Obtener detalles de juego que no existe."""
        result = GameService.get_game_detail("non-existing-id")
        
        assert result is None
