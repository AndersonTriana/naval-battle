#!/usr/bin/env python3
"""Test de coordenadas para tableros grandes"""

from app.structures.coordinate_utils import coordinate_to_code, code_to_coordinate, get_adjacent_coordinates

def test_coordinate(coord, board_size):
    """Prueba una coordenada específica"""
    print(f"\n{'='*60}")
    print(f"Probando: {coord} en tablero {board_size}x{board_size}")
    print(f"{'='*60}")
    
    try:
        # Convertir a código
        code = coordinate_to_code(coord, board_size)
        print(f"✅ coordinate_to_code('{coord}', {board_size}) = {code}")
        
        # Convertir de vuelta
        back = code_to_coordinate(code, board_size)
        print(f"✅ code_to_coordinate({code}, {board_size}) = '{back}'")
        
        if back != coord:
            print(f"⚠️  ADVERTENCIA: {coord} != {back}")
        
        # Probar coordenadas adyacentes horizontales
        print(f"\nProbando barco de 5 casillas horizontal desde {coord}:")
        coords = get_adjacent_coordinates(coord, board_size, "horizontal", 5)
        print(f"✅ Coordenadas: {coords}")
        
        # Probar coordenadas adyacentes verticales
        print(f"\nProbando barco de 5 casillas vertical desde {coord}:")
        coords = get_adjacent_coordinates(coord, board_size, "vertical", 5)
        print(f"✅ Coordenadas: {coords}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

# Tests para tablero 10x10
print("\n" + "="*60)
print("TABLERO 10x10")
print("="*60)
test_coordinate("A1", 10)
test_coordinate("A10", 10)
test_coordinate("J1", 10)
test_coordinate("J10", 10)

# Tests para tablero 15x15
print("\n" + "="*60)
print("TABLERO 15x15")
print("="*60)
test_coordinate("A1", 15)
test_coordinate("A11", 15)
test_coordinate("A15", 15)
test_coordinate("K11", 15)
test_coordinate("O15", 15)

# Tests para tablero 20x20
print("\n" + "="*60)
print("TABLERO 20x20")
print("="*60)
test_coordinate("A1", 20)
test_coordinate("A20", 20)
test_coordinate("T1", 20)
test_coordinate("T20", 20)

print("\n" + "="*60)
print("TESTS COMPLETADOS")
print("="*60)
