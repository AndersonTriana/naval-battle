"""
Tests para el modo de juego multijugador (2 jugadores).
"""
import pytest
from app.services.game_service import GameService
from app.services.board_service import BoardService
from app.storage.in_memory_store import (
    create_user,
    create_ship_template,
    create_base_fleet,
    get_game,
    games_db,
    users_db,
    ship_templates_db,
    base_fleets_db
)


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
    """Crear flota de prueba con barcos pequeños."""
    # Crear plantillas de barcos
    ship1 = create_ship_template("Lancha", 2, "Barco pequeño", "admin")
    ship2 = create_ship_template("Submarino", 3, "Barco mediano", "admin")
    
    # Crear flota base
    fleet = create_base_fleet(
        "Flota de Prueba",
        5,  # Tablero 5x5
        [ship1.id, ship2.id],
        "admin"
    )
    
    return fleet


class TestMultiplayerGameCreation:
    """Tests de creación de partidas multijugador."""
    
    def test_create_multiplayer_game(self, test_users, test_fleet):
        """Crear una partida multijugador."""
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        
        assert result is not None
        assert result["is_multiplayer"] is True
        assert result["status"] == "waiting_for_player2"
        assert result["player1_id"] == test_users["player1"].id
        assert result["player2_id"] is None
        assert result["current_turn_player_id"] is None
    
    def test_create_vs_ai_game(self, test_users, test_fleet):
        """Crear una partida vs IA (modo clásico)."""
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=False
        )
        
        assert result is not None
        assert result["is_multiplayer"] is False
        assert result["status"] == "setup"
        assert result["player1_id"] == test_users["player1"].id
        assert result["current_turn_player_id"] == test_users["player1"].id


class TestJoinGame:
    """Tests de unirse a una partida."""
    
    def test_join_multiplayer_game(self, test_users, test_fleet):
        """Jugador 2 se une a una partida multijugador."""
        # Crear partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        
        # Jugador 2 se une
        success, message, join_result = GameService.join_game(
            game_id,
            test_users["player2"].id
        )
        
        assert success is True
        assert join_result is not None
        assert join_result["player2_id"] == test_users["player2"].id
        assert join_result["status"] == "player1_setup"
    
    def test_join_non_multiplayer_game(self, test_users, test_fleet):
        """No se puede unir a una partida vs IA."""
        # Crear partida vs IA
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=False
        )
        game_id = result["game_id"]
        
        # Intentar unirse
        success, message, join_result = GameService.join_game(
            game_id,
            test_users["player2"].id
        )
        
        assert success is False
        assert "no es multijugador" in message.lower()
    
    def test_join_own_game(self, test_users, test_fleet):
        """No se puede unir a tu propia partida."""
        # Crear partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        
        # Intentar unirse a propia partida
        success, message, join_result = GameService.join_game(
            game_id,
            test_users["player1"].id
        )
        
        assert success is False
        assert "propia partida" in message.lower()
    
    def test_join_game_not_waiting(self, test_users, test_fleet):
        """No se puede unir a una partida que no está esperando."""
        # Crear partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        
        # Jugador 2 se une
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Crear un tercer usuario
        user3 = create_user("player3", "password789", "player")
        
        # Intentar unirse de nuevo
        success, message, join_result = GameService.join_game(
            game_id,
            user3.id
        )
        
        assert success is False
        assert "esperando" in message.lower()


class TestMultiplayerShipPlacement:
    """Tests de colocación de barcos en modo multijugador."""
    
    def test_player1_place_ship(self, test_users, test_fleet):
        """Jugador 1 coloca un barco."""
        # Crear y unir partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Jugador 1 coloca barco
        success, message, ship = GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        
        assert success is True
        assert ship is not None
        assert ship.size == 2
        
        # Verificar que el barco se agregó
        game = get_game(game_id)
        assert len(game.player1_ships) == 1
        assert len(game.player2_ships) == 0
    
    def test_player2_cannot_place_during_player1_setup(self, test_users, test_fleet):
        """Jugador 2 no puede colocar durante setup de jugador 1."""
        # Crear y unir partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Jugador 2 intenta colocar barco
        success, message, ship = GameService.place_ship(
            game_id,
            test_users["player2"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        
        assert success is False
        assert "turno" in message.lower()
    
    def test_transition_to_player2_setup(self, test_users, test_fleet):
        """Transición a setup de jugador 2 cuando jugador 1 termina."""
        # Crear y unir partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Jugador 1 coloca todos sus barcos
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[1],
            "B1",
            "horizontal"
        )
        
        # Verificar transición de estado
        game = get_game(game_id)
        assert game.status == "player2_setup"
    
    def test_both_players_ready_starts_game(self, test_users, test_fleet):
        """Cuando ambos jugadores terminan setup, el juego inicia."""
        # Crear y unir partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Jugador 1 coloca todos sus barcos
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[1],
            "B1",
            "horizontal"
        )
        
        # Jugador 2 coloca todos sus barcos
        GameService.place_ship(
            game_id,
            test_users["player2"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        GameService.place_ship(
            game_id,
            test_users["player2"].id,
            test_fleet.ship_template_ids[1],
            "B1",
            "horizontal"
        )
        
        # Verificar que el juego inició
        game = get_game(game_id)
        assert game.status == "player1_turn"
        assert game.current_turn_player_id == test_users["player1"].id


class TestMultiplayerGameStats:
    """Tests de estadísticas en modo multijugador."""
    
    def test_get_stats_for_player1(self, test_users, test_fleet):
        """Obtener estadísticas para jugador 1."""
        # Crear y preparar partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Colocar barcos
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[1],
            "B1",
            "horizontal"
        )
        
        # Obtener stats
        game = get_game(game_id)
        stats = game.get_stats(test_users["player1"].id)
        
        assert stats is not None
        assert stats["ships_total"] == 2
        assert stats["total_shots"] == 0
        assert stats["ships_remaining"] == 2
    
    def test_get_stats_for_player2(self, test_users, test_fleet):
        """Obtener estadísticas para jugador 2."""
        # Crear y preparar partida
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=True
        )
        game_id = result["game_id"]
        GameService.join_game(game_id, test_users["player2"].id)
        
        # Jugador 1 coloca todos sus barcos primero
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[1],
            "B1",
            "horizontal"
        )
        
        # Ahora jugador 2 coloca barcos
        GameService.place_ship(
            game_id,
            test_users["player2"].id,
            test_fleet.ship_template_ids[0],
            "C1",
            "horizontal"
        )
        
        # Obtener stats
        game = get_game(game_id)
        stats = game.get_stats(test_users["player2"].id)
        
        assert stats is not None
        assert stats["ships_total"] == 1
        assert stats["total_shots"] == 0


class TestMultiplayerVsAICompatibility:
    """Tests de compatibilidad con modo vs IA."""
    
    def test_vs_ai_still_works(self, test_users, test_fleet):
        """El modo vs IA sigue funcionando después de los cambios."""
        # Crear partida vs IA
        result = GameService.create_new_game(
            test_users["player1"].id,
            test_fleet.id,
            is_multiplayer=False
        )
        game_id = result["game_id"]
        
        # Colocar barcos
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[0],
            "A1",
            "horizontal"
        )
        GameService.place_ship(
            game_id,
            test_users["player1"].id,
            test_fleet.ship_template_ids[1],
            "B1",
            "horizontal"
        )
        
        # Verificar que la IA se inicializó
        game = get_game(game_id)
        assert game.status == "in_progress"
        assert len(game.player2_ships) == 2  # IA colocó sus barcos
        assert game.current_turn_player_id == test_users["player1"].id
