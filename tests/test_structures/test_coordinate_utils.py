"""
Tests para utilidades de coordenadas.
Valida funciones de conversión, validación y generación de coordenadas.
"""
import pytest
from app.structures.coordinate_utils import (
    coordinate_to_code,
    code_to_coordinate,
    generate_all_coordinates,
    generate_coordinate_codes,
    validate_coordinate,
    get_adjacent_coordinates,
    coordinates_overlap
)


class TestCoordinateToCode:
    """Tests de conversión de coordenada a código."""
    
    def test_coordinate_to_code_a1(self):
        """Convertir 'A1' -> 101 (tablero 10x10)."""
        assert coordinate_to_code("A1") == 101
    
    def test_coordinate_to_code_b3(self):
        """Convertir 'B3' -> 203 (tablero 10x10)."""
        assert coordinate_to_code("B3") == 203
    
    def test_coordinate_to_code_j10(self):
        """Convertir 'J10' -> 1010 (tablero 10x10)."""
        assert coordinate_to_code("J10") == 1010
    
    def test_coordinate_to_code_lowercase(self):
        """Convertir 'a1' (minúscula) -> 101."""
        assert coordinate_to_code("a1") == 101
        assert coordinate_to_code("b3") == 203
    
    def test_coordinate_to_code_mixed_case(self):
        """Convertir 'B3' (mixto) -> 203."""
        assert coordinate_to_code("B3") == 203
        assert coordinate_to_code("a1") == 101


class TestCodeToCoordinate:
    """Tests de conversión de código a coordenada."""
    
    def test_code_to_coordinate_11(self):
        """Convertir 101 -> 'A1' (tablero 10x10)."""
        assert code_to_coordinate(101) == "A1"
    
    def test_code_to_coordinate_23(self):
        """Convertir 203 -> 'B3' (tablero 10x10)."""
        assert code_to_coordinate(203) == "B3"
    
    def test_code_to_coordinate_100(self):
        """Convertir 1010 -> 'J10' (tablero 10x10)."""
        assert code_to_coordinate(1010) == "J10"
    
    def test_code_to_coordinate_roundtrip(self):
        """Verificar que la conversión es reversible."""
        original = "C5"
        code = coordinate_to_code(original)
        result = code_to_coordinate(code)
        assert result == original


class TestInvalidCoordinateFormat:
    """Tests de validación de formato de coordenadas."""
    
    def test_invalid_coordinate_format_z99(self):
        """Verificar que 'Z99' es técnicamente válido en formato pero requiere tablero grande."""
        # Z99 es válido en formato si el tablero es suficientemente grande (26x99)
        # Para tablero 10x10 debe lanzar excepción
        with pytest.raises(ValueError, match="fuera de rango"):
            coordinate_to_code("Z99", 10)
        
        # Pero funciona con tablero suficientemente grande
        code = coordinate_to_code("Z99", 99)
        assert code == 2699  # Z=26, col=99 -> 26*100+99=2699
    
    def test_invalid_coordinate_format_a0(self):
        """Verificar que 'A0' lanza excepción por columna inválida."""
        with pytest.raises(ValueError):
            coordinate_to_code("A0")
    
    def test_invalid_coordinate_format_numeric(self):
        """Verificar que '11' lanza excepción."""
        with pytest.raises(ValueError):
            coordinate_to_code("11")
    
    def test_invalid_coordinate_format_empty(self):
        """Verificar que string vacío lanza excepción."""
        with pytest.raises(ValueError):
            coordinate_to_code("")
    
    def test_invalid_coordinate_format_only_letter(self):
        """Verificar que solo letra lanza excepción."""
        with pytest.raises(ValueError):
            coordinate_to_code("A")
    
    def test_invalid_coordinate_format_only_number(self):
        """Verificar que solo número lanza excepción."""
        with pytest.raises(ValueError):
            coordinate_to_code("1")


class TestCoordinateValidation:
    """Tests de validación de coordenadas dentro del rango del tablero."""
    
    def test_validate_coordinate_valid_10x10(self):
        """Verificar que coordenadas válidas para tablero 10x10 pasan."""
        assert validate_coordinate("A1", 10) is True
        assert validate_coordinate("J10", 10) is True
        assert validate_coordinate("E5", 10) is True
    
    def test_validate_coordinate_invalid_10x10(self):
        """Verificar que coordenadas inválidas para tablero 10x10 fallan."""
        assert validate_coordinate("K1", 10) is False  # Fila fuera de rango (K=11)
        # A11: col=11%10=1, que es válido. Necesitamos A12 o mayor
        assert validate_coordinate("A12", 10) is False  # Columna fuera de rango
    
    def test_validate_coordinate_valid_5x5(self):
        """Verificar que coordenadas válidas para tablero 5x5 pasan."""
        assert validate_coordinate("A1", 5) is True
        assert validate_coordinate("E5", 5) is True
    
    def test_validate_coordinate_invalid_5x5(self):
        """Verificar que coordenadas inválidas para tablero 5x5 fallan."""
        assert validate_coordinate("F1", 5) is False
        assert validate_coordinate("A6", 5) is False
    
    def test_validate_coordinate_edge_cases(self):
        """Verificar casos límite."""
        # Primera coordenada válida
        assert validate_coordinate("A1", 10) is True
        # Última coordenada válida
        assert validate_coordinate("J10", 10) is True
        # Justo fuera del límite
        assert validate_coordinate("K1", 10) is False  # Fila 11
        assert validate_coordinate("A11", 10) is False  # col=11%10=1, pero 11>10


class TestGenerateCoordinates:
    """Tests de generación de coordenadas."""
    
    def test_generate_all_coordinates_5x5(self):
        """Generar todas las coordenadas para tablero 5x5."""
        coords = generate_all_coordinates(5)
        assert len(coords) == 25
        assert "A1" in coords
        assert "E5" in coords
    
    def test_generate_all_coordinates_10x10(self):
        """Generar todas las coordenadas para tablero 10x10."""
        coords = generate_all_coordinates(10)
        assert len(coords) == 100
        assert "A1" in coords
        assert "J10" in coords
    
    def test_generate_coordinate_codes_5x5(self):
        """Generar códigos de coordenadas para tablero 5x5."""
        codes = generate_coordinate_codes(5)
        assert len(codes) == 25
        assert 11 in codes  # A1
        assert 55 in codes  # E5
    
    def test_generate_coordinates_order(self):
        """Verificar que las coordenadas se generan en orden."""
        coords = generate_all_coordinates(3)
        expected = ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]
        assert coords == expected


class TestAdjacentCoordinates:
    """Tests de obtención de coordenadas adyacentes."""
    
    def test_get_adjacent_coordinates_horizontal(self):
        """Obtener coordenadas adyacentes horizontalmente."""
        coords = get_adjacent_coordinates("A1", 10, "horizontal", 3)
        assert coords == ["A1", "A2", "A3"]
    
    def test_get_adjacent_coordinates_vertical(self):
        """Obtener coordenadas adyacentes verticalmente."""
        coords = get_adjacent_coordinates("A1", 10, "vertical", 3)
        assert coords == ["A1", "B1", "C1"]
    
    def test_get_adjacent_coordinates_horizontal_out_of_bounds(self):
        """Verificar que lanza excepción si el barco no cabe horizontalmente."""
        with pytest.raises(ValueError):
            get_adjacent_coordinates("A9", 10, "horizontal", 3)
    
    def test_get_adjacent_coordinates_vertical_out_of_bounds(self):
        """Verificar que lanza excepción si el barco no cabe verticalmente."""
        with pytest.raises(ValueError):
            get_adjacent_coordinates("I1", 10, "vertical", 3)
    
    def test_get_adjacent_coordinates_single_cell(self):
        """Obtener coordenadas para barco de 1 celda."""
        coords = get_adjacent_coordinates("E5", 10, "horizontal", 1)
        assert coords == ["E5"]
    
    def test_get_adjacent_coordinates_invalid_orientation(self):
        """Verificar que lanza excepción con orientación inválida."""
        with pytest.raises(ValueError):
            get_adjacent_coordinates("A1", 10, "diagonal", 3)


class TestCoordinatesOverlap:
    """Tests de detección de superposición de coordenadas."""
    
    def test_coordinates_overlap_true(self):
        """Verificar que detecta superposición."""
        coords1 = ["A1", "A2", "A3"]
        coords2 = ["A3", "A4", "A5"]
        assert coordinates_overlap(coords1, coords2) is True
    
    def test_coordinates_overlap_false(self):
        """Verificar que detecta no superposición."""
        coords1 = ["A1", "A2", "A3"]
        coords2 = ["B1", "B2", "B3"]
        assert coordinates_overlap(coords1, coords2) is False
    
    def test_coordinates_overlap_complete(self):
        """Verificar superposición completa."""
        coords1 = ["A1", "A2", "A3"]
        coords2 = ["A1", "A2", "A3"]
        assert coordinates_overlap(coords1, coords2) is True
    
    def test_coordinates_overlap_empty(self):
        """Verificar que listas vacías no se superponen."""
        coords1 = []
        coords2 = ["A1", "A2"]
        assert coordinates_overlap(coords1, coords2) is False
    
    def test_coordinates_overlap_single_match(self):
        """Verificar que una sola coincidencia es suficiente."""
        coords1 = ["A1", "A2", "A3", "A4", "A5"]
        coords2 = ["B1", "B2", "A3", "B4"]
        assert coordinates_overlap(coords1, coords2) is True
