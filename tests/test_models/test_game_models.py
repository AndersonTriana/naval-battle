"""
Tests para modelos Pydantic de juego.
Valida la validación de datos de partidas y acciones de juego.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models.game import (
    GameStatus,
    GameCreate,
    ShotRequest,
    ShotResult,
    ShotResponse,
    ShotHistory,
    GameResponse,
    GameDetailResponse,
    GameListResponse
)
from app.models.ship import ShipInstance, ShipSegment


class TestGameStatus:
    """Tests del enum GameStatus."""
    
    def test_game_status_setup(self):
        """Verificar que estado setup existe."""
        assert GameStatus.SETUP == "setup"
    
    def test_game_status_in_progress(self):
        """Verificar que estado in_progress existe."""
        assert GameStatus.IN_PROGRESS == "in_progress"
    
    def test_game_status_finished(self):
        """Verificar que estado finished existe."""
        assert GameStatus.FINISHED == "finished"
    
    def test_game_status_all_values(self):
        """Verificar todos los valores del enum."""
        statuses = [status.value for status in GameStatus]
        assert "setup" in statuses
        assert "in_progress" in statuses
        assert "finished" in statuses
        assert len(statuses) == 3


class TestShotResult:
    """Tests del enum ShotResult."""
    
    def test_shot_result_water(self):
        """Verificar resultado water."""
        assert ShotResult.WATER == "water"
    
    def test_shot_result_hit(self):
        """Verificar resultado hit."""
        assert ShotResult.HIT == "hit"
    
    def test_shot_result_sunk(self):
        """Verificar resultado sunk."""
        assert ShotResult.SUNK == "sunk"
    
    def test_shot_result_all_values(self):
        """Verificar todos los valores del enum."""
        results = [result.value for result in ShotResult]
        assert "water" in results
        assert "hit" in results
        assert "sunk" in results
        assert len(results) == 3


class TestGameCreate:
    """Tests del modelo GameCreate."""
    
    def test_game_create_valid(self):
        """Crear juego con base_fleet_id válido."""
        game = GameCreate(base_fleet_id="fleet-id-123")
        assert game.base_fleet_id == "fleet-id-123"
    
    def test_game_create_required_field(self):
        """Verificar que base_fleet_id es requerido."""
        with pytest.raises(ValidationError):
            GameCreate()


class TestShotRequest:
    """Tests del modelo ShotRequest."""
    
    def test_shot_request_model(self):
        """Validar modelo de disparo."""
        shot = ShotRequest(coordinate="B3")
        assert shot.coordinate == "B3"
    
    def test_shot_request_required_field(self):
        """Verificar que coordinate es requerido."""
        with pytest.raises(ValidationError):
            ShotRequest()
    
    def test_shot_request_various_coordinates(self):
        """Validar diferentes formatos de coordenadas."""
        coordinates = ["A1", "B3", "J10", "E5"]
        for coord in coordinates:
            shot = ShotRequest(coordinate=coord)
            assert shot.coordinate == coord


class TestShotResponse:
    """Tests del modelo ShotResponse."""
    
    def test_shot_response_water(self):
        """Crear respuesta de disparo al agua."""
        response = ShotResponse(
            coordinate="B3",
            coordinate_code=23,
            result=ShotResult.WATER,
            ship_hit=None,
            ship_sunk=False,
            game_finished=False
        )
        assert response.result == ShotResult.WATER
        assert response.ship_hit is None
        assert response.ship_sunk is False
        assert response.game_finished is False
    
    def test_shot_response_hit(self):
        """Crear respuesta de disparo con impacto."""
        response = ShotResponse(
            coordinate="A1",
            coordinate_code=11,
            result=ShotResult.HIT,
            ship_hit="Portaaviones",
            ship_sunk=False,
            game_finished=False
        )
        assert response.result == ShotResult.HIT
        assert response.ship_hit == "Portaaviones"
        assert response.ship_sunk is False
    
    def test_shot_response_sunk(self):
        """Crear respuesta de barco hundido."""
        response = ShotResponse(
            coordinate="C5",
            coordinate_code=35,
            result=ShotResult.SUNK,
            ship_hit="Crucero",
            ship_sunk=True,
            game_finished=False
        )
        assert response.result == ShotResult.SUNK
        assert response.ship_hit == "Crucero"
        assert response.ship_sunk is True
    
    def test_shot_response_game_finished(self):
        """Crear respuesta con juego terminado."""
        response = ShotResponse(
            coordinate="D7",
            coordinate_code=47,
            result=ShotResult.SUNK,
            ship_hit="Último Barco",
            ship_sunk=True,
            game_finished=True
        )
        assert response.game_finished is True
    
    def test_shot_response_default_values(self):
        """Verificar valores por defecto."""
        response = ShotResponse(
            coordinate="A1",
            coordinate_code=11,
            result=ShotResult.WATER
        )
        assert response.ship_hit is None
        assert response.ship_sunk is False
        assert response.game_finished is False


class TestShotHistory:
    """Tests del modelo ShotHistory."""
    
    def test_shot_history_model(self):
        """Crear entrada de historial de disparo."""
        history = ShotHistory(
            coordinate="B3",
            coordinate_code=23,
            result=ShotResult.HIT,
            timestamp=datetime.now()
        )
        assert history.coordinate == "B3"
        assert history.coordinate_code == 23
        assert history.result == ShotResult.HIT
        assert isinstance(history.timestamp, datetime)


class TestGameResponse:
    """Tests del modelo GameResponse."""
    
    def test_game_response_valid(self):
        """Crear respuesta de juego válida."""
        game = GameResponse(
            id="game-id",
            player_id="player-id",
            base_fleet_id="fleet-id",
            board_size=10,
            status=GameStatus.IN_PROGRESS,
            total_shots=15,
            hits=5,
            misses=10,
            ships_total=5,
            ships_remaining=3,
            ships_sunk=2,
            created_at=datetime.now(),
            finished_at=None
        )
        assert game.id == "game-id"
        assert game.status == GameStatus.IN_PROGRESS
        assert game.total_shots == 15
        assert game.hits == 5
        assert game.misses == 10
        assert game.ships_remaining == 3
    
    def test_game_response_finished(self):
        """Crear respuesta de juego terminado."""
        now = datetime.now()
        game = GameResponse(
            id="game-id",
            player_id="player-id",
            base_fleet_id="fleet-id",
            board_size=10,
            status=GameStatus.FINISHED,
            total_shots=50,
            hits=17,
            misses=33,
            ships_total=5,
            ships_remaining=0,
            ships_sunk=5,
            created_at=now,
            finished_at=now
        )
        assert game.status == GameStatus.FINISHED
        assert game.ships_remaining == 0
        assert game.ships_sunk == 5
        assert game.finished_at is not None
    
    def test_game_response_setup_phase(self):
        """Crear respuesta de juego en fase setup."""
        game = GameResponse(
            id="game-id",
            player_id="player-id",
            base_fleet_id="fleet-id",
            board_size=10,
            status=GameStatus.SETUP,
            total_shots=0,
            hits=0,
            misses=0,
            ships_total=5,
            ships_remaining=5,
            ships_sunk=0,
            created_at=datetime.now()
        )
        assert game.status == GameStatus.SETUP
        assert game.total_shots == 0
        assert game.ships_remaining == 5


class TestGameDetailResponse:
    """Tests del modelo GameDetailResponse."""
    
    def test_game_detail_response_valid(self):
        """Crear respuesta detallada de juego."""
        game = GameResponse(
            id="game-id",
            player_id="player-id",
            base_fleet_id="fleet-id",
            board_size=10,
            status=GameStatus.IN_PROGRESS,
            total_shots=5,
            hits=2,
            misses=3,
            ships_total=3,
            ships_remaining=2,
            ships_sunk=1,
            created_at=datetime.now()
        )
        
        ships = [
            ShipInstance(
                ship_template_id="template-1",
                ship_name="Portaaviones",
                size=5,
                segments=[
                    ShipSegment(coordinate="A1", coordinate_code=11, is_hit=True),
                    ShipSegment(coordinate="A2", coordinate_code=12, is_hit=False)
                ],
                is_sunk=False
            )
        ]
        
        shot_history = [
            ShotHistory(
                coordinate="A1",
                coordinate_code=11,
                result=ShotResult.HIT,
                timestamp=datetime.now()
            )
        ]
        
        detail = GameDetailResponse(
            game=game,
            ships=ships,
            shot_history=shot_history
        )
        
        assert detail.game.id == "game-id"
        assert len(detail.ships) == 1
        assert len(detail.shot_history) == 1


class TestGameListResponse:
    """Tests del modelo GameListResponse."""
    
    def test_game_list_response_empty(self):
        """Crear lista vacía de juegos."""
        game_list = GameListResponse(total=0, games=[])
        assert game_list.total == 0
        assert len(game_list.games) == 0
    
    def test_game_list_response_with_games(self):
        """Crear lista con múltiples juegos."""
        games = [
            GameResponse(
                id=f"game-{i}",
                player_id="player-id",
                base_fleet_id="fleet-id",
                board_size=10,
                status=GameStatus.IN_PROGRESS,
                total_shots=i * 5,
                hits=i * 2,
                misses=i * 3,
                ships_total=5,
                ships_remaining=5 - i,
                ships_sunk=i,
                created_at=datetime.now()
            )
            for i in range(3)
        ]
        
        game_list = GameListResponse(total=3, games=games)
        assert game_list.total == 3
        assert len(game_list.games) == 3
    
    def test_game_list_response_total_matches_length(self):
        """Verificar que total coincide con la longitud de la lista."""
        games = [
            GameResponse(
                id="game-1",
                player_id="player-id",
                base_fleet_id="fleet-id",
                board_size=10,
                status=GameStatus.FINISHED,
                total_shots=20,
                hits=10,
                misses=10,
                ships_total=5,
                ships_remaining=0,
                ships_sunk=5,
                created_at=datetime.now()
            )
        ]
        
        game_list = GameListResponse(total=1, games=games)
        assert game_list.total == len(game_list.games)
