"""
Utilidades para manejo de coordenadas del tablero.

Codificación: FilaNumérica × 10 + Columna
Ejemplo: A1 → 11, B3 → 23, J10 → 100
"""
from typing import List, Tuple
import re


def coordinate_to_code(coordinate: str, board_size: int = 10) -> int:
    """
    Convierte una coordenada en formato "A1" a su código numérico.
    
    Args:
        coordinate: Coordenada en formato letra+número (ej: "A1", "J10")
        board_size: Tamaño del tablero (para determinar el multiplicador)
    
    Returns:
        Código numérico único
    
    Raises:
        ValueError: Si el formato de la coordenada es inválido
    
    Examples:
        >>> coordinate_to_code("A1", 10)
        11
        >>> coordinate_to_code("B3", 10)
        23
        >>> coordinate_to_code("J10", 10)
        100
        >>> coordinate_to_code("A12", 15)
        112
    """
    # Validar formato
    match = re.match(r'^([A-Z])(\d+)$', coordinate.upper())
    if not match:
        raise ValueError(f"Formato de coordenada inválido: '{coordinate}'")
    
    letter, number = match.groups()
    
    # Convertir letra a número (A=1, B=2, ..., Z=26)
    row = ord(letter) - ord('A') + 1
    col = int(number)
    
    # Validar que la fila esté en rango válido
    if row < 1:
        raise ValueError(f"Fila inválida: {letter} (row={row}). Las filas deben ser >= 1. Coordenada recibida: '{coordinate}'")
    if row > board_size:
        raise ValueError(f"Fila {letter} (row={row}) fuera de rango. El tablero es {board_size}x{board_size}. Coordenada: '{coordinate}'")
    
    # Validar que la columna esté en rango válido
    if col < 1:
        raise ValueError(f"Columna inválida: {col}. Las columnas deben ser >= 1. Coordenada recibida: '{coordinate}'")
    if col > board_size:
        raise ValueError(f"Columna {col} fuera de rango. El tablero es {board_size}x{board_size}. Coordenada: '{coordinate}'")
    
    # Usar multiplicador apropiado según tamaño del tablero
    # Para tableros >= 10, necesitamos multiplicador 100 para evitar ambigüedad
    # Ejemplo: J10 en tablero 10x10 = 10*100+10 = 1010 (no 10*10+10 = 110)
    multiplier = 100 if board_size >= 10 else 10
    
    return row * multiplier + col


def code_to_coordinate(code: int, board_size: int = 10) -> str:
    """
    Convierte un código numérico a coordenada en formato "A1".
    
    Args:
        code: Código numérico
        board_size: Tamaño del tablero (para determinar el multiplicador)
    
    Returns:
        Coordenada en formato letra+número
    
    Examples:
        >>> code_to_coordinate(11, 10)
        'A1'
        >>> code_to_coordinate(23, 10)
        'B3'
        >>> code_to_coordinate(100, 10)
        'J10'
        >>> code_to_coordinate(112, 15)
        'A12'
    """
    # Usar multiplicador apropiado según tamaño del tablero
    multiplier = 100 if board_size >= 10 else 10
    
    row = code // multiplier
    col = code % multiplier
    
    # Convertir número a letra (1=A, 2=B, ..., 26=Z)
    letter = chr(ord('A') + row - 1)
    
    return f"{letter}{col}"


def generate_all_coordinates(board_size: int) -> List[str]:
    """
    Genera todas las coordenadas posibles para un tablero de tamaño NxN.
    
    Args:
        board_size: Tamaño del tablero (N)
    
    Returns:
        Lista de coordenadas en formato "A1", "A2", etc.
    
    Examples:
        >>> generate_all_coordinates(3)
        ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
    """
    coordinates = []
    
    for row in range(1, board_size + 1):
        letter = chr(ord('A') + row - 1)
        for col in range(1, board_size + 1):
            coordinates.append(f"{letter}{col}")
    
    return coordinates


def generate_coordinate_codes(board_size: int) -> List[int]:
    """
    Genera todos los códigos de coordenadas para un tablero de tamaño dado.
    
    Para tableros <= 10x10: usa formato row*10 + col (ej: A1=11, B2=22)
    Para tableros > 10x10: usa formato row*100 + col (ej: A1=101, B2=202)
    
    Args:
        board_size: Tamaño del tablero (N)
    
    Returns:
        Lista de códigos numéricos únicos
    
    Examples:
        >>> generate_coordinate_codes(3)
        [11, 12, 13, 21, 22, 23, 31, 32, 33]
        >>> generate_coordinate_codes(12)
        [101, 102, ..., 1212]
    """
    codes = []
    
    # Usar multiplicador más grande para tableros grandes
    multiplier = 100 if board_size > 10 else 10
    
    for row in range(1, board_size + 1):
        for col in range(1, board_size + 1):
            codes.append(row * multiplier + col)
    
    return codes


def balance_array_for_bst(arr: List[int]) -> List[int]:
    """
    Reordena un array usando el algoritmo del medio recursivo para crear un ABB balanceado.
    
    El algoritmo inserta primero el elemento del medio, luego recursivamente
    procesa la mitad izquierda y derecha.
    
    Args:
        arr: Array ordenado de códigos de coordenadas
    
    Returns:
        Array reordenado para inserción balanceada en ABB
    
    Examples:
        >>> balance_array_for_bst([1, 2, 3, 4, 5, 6, 7])
        [4, 2, 1, 3, 6, 5, 7]
    """
    if not arr:
        return []
    
    result = []
    
    def insert_middle(left: int, right: int) -> None:
        """
        Inserta recursivamente el elemento del medio y procesa las mitades.
        
        Args:
            left: Índice izquierdo del rango
            right: Índice derecho del rango
        """
        if left > right:
            return
        
        # Calcular el índice del medio
        mid = (left + right) // 2
        
        # Insertar el elemento del medio
        result.append(arr[mid])
        
        # Recursivamente procesar mitad izquierda y derecha
        insert_middle(left, mid - 1)
        insert_middle(mid + 1, right)
    
    insert_middle(0, len(arr) - 1)
    return result


def validate_coordinate(coordinate: str, board_size: int) -> bool:
    """
    Valida si una coordenada es válida para un tablero dado.
    
    Args:
        coordinate: Coordenada en formato "A1"
        board_size: Tamaño del tablero
    
    Returns:
        True si la coordenada es válida, False en caso contrario
    """
    try:
        # Extraer fila y columna directamente del string
        match = re.match(r'^([A-Z])(\d+)$', coordinate.upper())
        if not match:
            return False
        
        letter, number = match.groups()
        row = ord(letter) - ord('A') + 1
        col = int(number)
        
        # Validar rangos
        return 1 <= row <= board_size and 1 <= col <= board_size
    except (ValueError, AttributeError):
        return False


def get_adjacent_coordinates(coordinate: str, board_size: int, 
                            orientation: str, length: int) -> List[str]:
    """
    Obtiene las coordenadas adyacentes para colocar un barco.
    
    Args:
        coordinate: Coordenada inicial
        board_size: Tamaño del tablero
        orientation: "horizontal" o "vertical"
        length: Longitud del barco
    
    Returns:
        Lista de coordenadas que ocuparía el barco
    
    Raises:
        ValueError: Si el barco no cabe en el tablero
    """
    # Usar multiplicador apropiado según tamaño del tablero
    multiplier = 100 if board_size >= 10 else 10
    
    try:
        code = coordinate_to_code(coordinate, board_size)
    except ValueError as e:
        raise ValueError(f"Error al convertir coordenada '{coordinate}': {e}")
    
    row = code // multiplier
    col = code % multiplier
    
    coordinates = []
    
    if orientation == "horizontal":
        # Verificar que cabe horizontalmente
        if col + length - 1 > board_size:
            raise ValueError(f"El barco no cabe horizontalmente desde {coordinate}. Columna final: {col + length - 1}, Tamaño tablero: {board_size}")
        
        for i in range(length):
            new_code = row * multiplier + (col + i)
            try:
                coord = code_to_coordinate(new_code, board_size)
                coordinates.append(coord)
            except Exception as e:
                raise ValueError(f"Error generando coordenada horizontal {i}: code={new_code}, board_size={board_size}, error={e}")
    
    elif orientation == "vertical":
        # Verificar que cabe verticalmente
        if row + length - 1 > board_size:
            raise ValueError(f"El barco no cabe verticalmente desde {coordinate}. Fila final: {row + length - 1}, Tamaño tablero: {board_size}")
        
        for i in range(length):
            new_code = (row + i) * multiplier + col
            try:
                coord = code_to_coordinate(new_code, board_size)
                coordinates.append(coord)
            except Exception as e:
                raise ValueError(f"Error generando coordenada vertical {i}: code={new_code}, board_size={board_size}, error={e}")
    
    else:
        raise ValueError(f"Orientación inválida: {orientation}")
    
    return coordinates


def coordinates_overlap(coords1: List[str], coords2: List[str]) -> bool:
    """
    Verifica si dos conjuntos de coordenadas se superponen.
    
    Args:
        coords1: Primera lista de coordenadas
        coords2: Segunda lista de coordenadas
    
    Returns:
        True si hay superposición, False en caso contrario
    """
    set1 = set(coords1)
    set2 = set(coords2)
    
    return len(set1 & set2) > 0
