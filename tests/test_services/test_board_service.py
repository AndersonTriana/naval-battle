"""
Tests para BoardService.
"""
import pytest
from app.services.board_service import BoardService
from app.structures.binary_search_tree import BinarySearchTree


class TestBoardServiceCreateBalancedBST:
    """Tests de creación de ABB balanceado."""
    
    def test_create_balanced_bst_10x10(self):
        """Crear ABB balanceado para tablero 10x10."""
        bst = BoardService.create_balanced_bst(10)
        
        assert bst is not None
        assert bst.size() == 100
        assert not bst.is_empty()
    
    def test_create_balanced_bst_5x5(self):
        """Crear ABB balanceado para tablero 5x5."""
        bst = BoardService.create_balanced_bst(5)
        
        assert bst.size() == 25
    
    def test_bst_contains_all_coordinates(self):
        """Verificar que el ABB contiene todas las coordenadas."""
        bst = BoardService.create_balanced_bst(3)
        
        # Verificar algunas coordenadas
        assert bst.search(11) is not None  # A1
        assert bst.search(22) is not None  # B2
        assert bst.search(33) is not None  # C3


class TestBoardServiceSearchCoordinate:
    """Tests de búsqueda de coordenadas."""
    
    def test_search_existing_coordinate(self):
        """Buscar coordenada que existe."""
        bst = BoardService.create_balanced_bst(10)
        
        result = BoardService.search_coordinate(bst, "A1")
        assert result is True
    
    def test_search_coordinate_various(self):
        """Buscar varias coordenadas."""
        bst = BoardService.create_balanced_bst(10)
        
        assert BoardService.search_coordinate(bst, "A1") is True
        assert BoardService.search_coordinate(bst, "J10") is True
        assert BoardService.search_coordinate(bst, "E5") is True


class TestBoardServiceMarkCoordinateAsShot:
    """Tests de marcar coordenadas como disparadas."""
    
    def test_mark_coordinate_as_shot(self):
        """Marcar coordenada como disparada."""
        bst = BoardService.create_balanced_bst(10)
        
        result = BoardService.mark_coordinate_as_shot(bst, "A1")
        assert result is True
    
    def test_is_coordinate_shot(self):
        """Verificar si coordenada fue disparada."""
        bst = BoardService.create_balanced_bst(10)
        
        # Inicialmente no disparada
        assert BoardService.is_coordinate_shot(bst, "A1") is False
        
        # Marcar como disparada
        BoardService.mark_coordinate_as_shot(bst, "A1")
        
        # Ahora debe estar disparada
        assert BoardService.is_coordinate_shot(bst, "A1") is True


class TestBoardServiceValidateCoordinate:
    """Tests de validación de coordenadas."""
    
    def test_validate_valid_coordinate(self):
        """Validar coordenada válida."""
        is_valid, msg = BoardService.validate_coordinate_for_board("A1", 10)
        assert is_valid is True
        assert msg == ""
    
    def test_validate_invalid_coordinate(self):
        """Validar coordenada inválida."""
        is_valid, msg = BoardService.validate_coordinate_for_board("K1", 10)
        assert is_valid is False
        assert "fuera del tablero" in msg


class TestBoardServiceCalculateShipCoordinates:
    """Tests de cálculo de coordenadas de barco."""
    
    def test_calculate_horizontal_ship(self):
        """Calcular coordenadas de barco horizontal."""
        is_valid, coords, msg = BoardService.calculate_ship_coordinates(
            "A1", 3, "horizontal", 10
        )
        
        assert is_valid is True
        assert coords == ["A1", "A2", "A3"]
        assert msg == ""
    
    def test_calculate_vertical_ship(self):
        """Calcular coordenadas de barco vertical."""
        is_valid, coords, msg = BoardService.calculate_ship_coordinates(
            "A1", 3, "vertical", 10
        )
        
        assert is_valid is True
        assert coords == ["A1", "B1", "C1"]
        assert msg == ""
    
    def test_calculate_ship_out_of_bounds(self):
        """Calcular barco que se sale del tablero."""
        is_valid, coords, msg = BoardService.calculate_ship_coordinates(
            "A9", 3, "horizontal", 10
        )
        
        assert is_valid is False
        assert coords == []


class TestBoardServiceCheckCoordinatesAvailable:
    """Tests de verificación de disponibilidad de coordenadas."""
    
    def test_check_available_coordinates(self):
        """Verificar coordenadas disponibles."""
        bst = BoardService.create_balanced_bst(10)
        
        coords = ["A1", "A2", "A3"]
        is_available, msg = BoardService.check_coordinates_available(coords, bst)
        
        assert is_available is True
        assert msg == ""
    
    def test_check_occupied_coordinates(self):
        """Verificar coordenadas ocupadas."""
        bst = BoardService.create_balanced_bst(10)
        
        # Marcar A2 como ocupada
        BoardService.mark_coordinates_occupied(["A2"], bst, "ship_ref")
        
        coords = ["A1", "A2", "A3"]
        is_available, msg = BoardService.check_coordinates_available(coords, bst)
        
        assert is_available is False
        assert "ocupada" in msg


class TestBoardServiceMarkCoordinatesOccupied:
    """Tests de marcar coordenadas como ocupadas."""
    
    def test_mark_coordinates_occupied(self):
        """Marcar coordenadas como ocupadas."""
        bst = BoardService.create_balanced_bst(10)
        
        coords = ["A1", "A2", "A3"]
        BoardService.mark_coordinates_occupied(coords, bst, "ship_ref")
        
        # Verificar que están marcadas
        is_available, _ = BoardService.check_coordinates_available(coords, bst)
        assert is_available is False


class TestBoardServiceGetBoardStatistics:
    """Tests de estadísticas del tablero."""
    
    def test_get_board_statistics(self):
        """Obtener estadísticas del tablero."""
        bst = BoardService.create_balanced_bst(5)
        
        stats = BoardService.get_board_statistics(bst)
        
        assert stats["total_cells"] == 25
        assert stats["shot_cells"] == 0
        assert stats["remaining_cells"] == 25
    
    def test_get_board_statistics_with_shots(self):
        """Obtener estadísticas con disparos."""
        bst = BoardService.create_balanced_bst(5)
        
        # Marcar algunas como disparadas
        BoardService.mark_coordinate_as_shot(bst, "A1")
        BoardService.mark_coordinate_as_shot(bst, "B2")
        
        stats = BoardService.get_board_statistics(bst)
        
        assert stats["total_cells"] == 25
        assert stats["shot_cells"] == 2
        assert stats["remaining_cells"] == 23
