"""
Utilidades para manejo de coordenadas del tablero.

Codificación: FilaNumérica × 10 + Columna
Ejemplo: A1 → 11, B3 → 23, J10 → 100
"""
from typing import List, Tuple
import re


def coordinate_to_code(coordinate: str) -> int:
    """
    Convierte una coordenada en formato "A1" a su código numérico.
    
    Args:
        coordinate: Coordenada en formato letra+número (ej: "A1", "J10")
    
    Returns:
        Código numérico (FilaNumérica × 10 + Columna)
    
    Raises:
        ValueError: Si el formato de la coordenada es inválido
    
    Examples:
        >>> coordinate_to_code("A1")
        11
        >>> coordinate_to_code("B3")
        23
        >>> coordinate_to_code("J10")
        100
    """
    # Validar formato
    match = re.match(r'^([A-Z])(\d+)$', coordinate.upper())
    if not match:
        raise ValueError(f"Formato de coordenada inválido: {coordinate}")
    
    letter, number = match.groups()
    
    # Convertir letra a número (A=1, B=2, ..., Z=26)
    row = ord(letter) - ord('A') + 1
    col = int(number)
    
    # Validar que la columna esté en rango válido (1-10)
    if col < 1:
        raise ValueError(f"Columna inválida: {col}")
    
    # Aplicar fórmula: FilaNumérica × 10 + (Columna % 10)
    # Esto hace que columna 10 se codifique como 0
    return row * 10 + (col % 10)


def code_to_coordinate(code: int) -> str:
    """
    Convierte un código numérico a coordenada en formato "A1".
    
    Args:
        code: Código numérico
    
    Returns:
        Coordenada en formato letra+número
    
    Examples:
        >>> code_to_coordinate(11)
        'A1'
        >>> code_to_coordinate(23)
        'B3'
        >>> code_to_coordinate(100)
        'J10'
    """
    row = code // 10
    col = code % 10
    
    # Si col es 0, significa que es la columna 10
    if col == 0:
        col = 10
    
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
    Genera todos los códigos de coordenadas para un tablero de tamaño NxN.
    
    Args:
        board_size: Tamaño del tablero (N)
    
    Returns:
        Lista de códigos numéricos
    
    Examples:
        >>> generate_coordinate_codes(3)
        [11, 12, 13, 21, 22, 23, 31, 32, 33]
    """
    codes = []
    
    for row in range(1, board_size + 1):
        for col in range(1, board_size + 1):
            # Usar módulo 10 para que columna 10 se codifique como 0
            codes.append(row * 10 + (col % 10))
    
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
    code = coordinate_to_code(coordinate)
    row = code // 10
    col = code % 10
    
    coordinates = []
    
    if orientation == "horizontal":
        # Verificar que cabe horizontalmente
        if col + length - 1 > board_size:
            raise ValueError(f"El barco no cabe horizontalmente desde {coordinate}")
        
        for i in range(length):
            new_code = row * 10 + (col + i)
            coordinates.append(code_to_coordinate(new_code))
    
    elif orientation == "vertical":
        # Verificar que cabe verticalmente
        if row + length - 1 > board_size:
            raise ValueError(f"El barco no cabe verticalmente desde {coordinate}")
        
        for i in range(length):
            new_code = (row + i) * 10 + col
            coordinates.append(code_to_coordinate(new_code))
    
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
