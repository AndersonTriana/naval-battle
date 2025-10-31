"""
Servicio para gestión de tableros y ABB.
"""
from typing import List, Tuple
from app.structures.binary_search_tree import BinarySearchTree
from app.structures.abb_node import Node
from app.structures.coordinate_utils import (
    generate_coordinate_codes,
    balance_array_for_bst,
    coordinate_to_code,
    code_to_coordinate,
    validate_coordinate,
    get_adjacent_coordinates
)
from app.core.exceptions import CoordinateInvalidError, ShipOutOfBoundsError


class BoardService:
    """Servicio para gestión de tableros usando ABB."""
    
    @staticmethod
    def create_balanced_bst(board_size: int) -> BinarySearchTree:
        """
        Crea un ABB balanceado con todas las coordenadas del tablero.
        
        Proceso:
        1. Genera todos los códigos de coordenadas (11, 12, ..., NN)
        2. Reordena usando algoritmo del medio recursivo
        3. Inserta secuencialmente en el ABB
        
        Args:
            board_size: Tamaño del tablero (NxN)
        
        Returns:
            ABB balanceado con todas las coordenadas
        """
        # Generar todos los códigos de coordenadas
        codes = generate_coordinate_codes(board_size)
        
        # Reordenar para inserción balanceada
        balanced_codes = balance_array_for_bst(codes)
        
        # Crear el ABB e insertar en orden balanceado
        bst = BinarySearchTree()
        for code in balanced_codes:
            node = Node(id=code, data={"coordinate": code_to_coordinate(code)})
            bst.insert(node)
        
        return bst
    
    @staticmethod
    def search_coordinate(bst: BinarySearchTree, coordinate: str) -> bool:
        """
        Busca una coordenada en el ABB.
        
        Args:
            bst: Árbol binario de búsqueda
            coordinate: Coordenada a buscar (ej: "A1")
        
        Returns:
            True si la coordenada existe, False en caso contrario
        """
        code = coordinate_to_code(coordinate)
        node = bst.search(code)
        return node is not None
    
    @staticmethod
    def mark_coordinate_as_shot(bst: BinarySearchTree, coordinate: str) -> bool:
        """
        Marca una coordenada como disparada en el ABB.
        
        Args:
            bst: Árbol binario de búsqueda
            coordinate: Coordenada a marcar
        
        Returns:
            True si se marcó exitosamente, False si no existe
        """
        code = coordinate_to_code(coordinate)
        node = bst.search(code)
        
        if node:
            if node.data is None:
                node.data = {}
            node.data["is_shot"] = True
            return True
        
        return False
    
    @staticmethod
    def is_coordinate_shot(bst: BinarySearchTree, coordinate: str) -> bool:
        """
        Verifica si una coordenada ya fue disparada.
        
        Args:
            bst: Árbol binario de búsqueda
            coordinate: Coordenada a verificar
        
        Returns:
            True si ya fue disparada, False en caso contrario
        """
        code = coordinate_to_code(coordinate)
        node = bst.search(code)
        
        if node and node.data:
            return node.data.get("is_shot", False)
        
        return False
    
    @staticmethod
    def get_board_statistics(bst: BinarySearchTree) -> dict:
        """
        Obtiene estadísticas del tablero desde el ABB.
        
        Args:
            bst: Árbol binario de búsqueda
        
        Returns:
            Diccionario con estadísticas
        """
        all_nodes = bst.inOrder()
        
        total_cells = len(all_nodes)
        shot_cells = sum(1 for node in all_nodes if node.get("data", {}).get("is_shot", False))
        
        return {
            "total_cells": total_cells,
            "shot_cells": shot_cells,
            "remaining_cells": total_cells - shot_cells
        }
    
    @staticmethod
    def validate_coordinate_for_board(coordinate: str, board_size: int) -> Tuple[bool, str]:
        """
        Valida que una coordenada sea válida para el tablero.
        
        Args:
            coordinate: Coordenada en formato "A1", "B3", etc.
            board_size: Tamaño del tablero
        
        Returns:
            (es_valida, mensaje_error)
        
        Validaciones:
            - Formato correcto: Letra + Número
            - Letra dentro del rango (A hasta letra correspondiente a board_size)
            - Número dentro del rango (1 hasta board_size)
        """
        if not validate_coordinate(coordinate, board_size):
            return False, f"Coordenada '{coordinate}' fuera del tablero {board_size}x{board_size}"
        return True, ""
    
    @staticmethod
    def calculate_ship_coordinates(
        start_coordinate: str,
        size: int,
        orientation: str,
        board_size: int
    ) -> Tuple[bool, List[str], str]:
        """
        Calcula todas las coordenadas que ocupará un barco.
        
        Args:
            start_coordinate: Coordenada inicial (ej: "A1")
            size: Tamaño del barco
            orientation: "horizontal" o "vertical"
            board_size: Tamaño del tablero
        
        Returns:
            (es_valido, lista_coordenadas, mensaje_error)
        
        Validaciones:
            - start_coordinate válida
            - El barco no se sale del tablero
        """
        # Validar coordenada inicial
        is_valid, error_msg = BoardService.validate_coordinate_for_board(
            start_coordinate, board_size
        )
        if not is_valid:
            return False, [], error_msg
        
        # Calcular coordenadas del barco
        try:
            coordinates = get_adjacent_coordinates(
                start_coordinate, board_size, orientation, size
            )
            return True, coordinates, ""
        except ValueError as e:
            return False, [], str(e)
    
    @staticmethod
    def check_coordinates_available(
        coordinates: List[str],
        bst: BinarySearchTree
    ) -> Tuple[bool, str]:
        """
        Verifica que ninguna coordenada esté ocupada en el ABB.
        
        Args:
            coordinates: Lista de coordenadas a verificar
            bst: Árbol binario de búsqueda del juego
        
        Returns:
            (disponibles, mensaje_error)
        
        Proceso:
            - Convertir cada coordenada a código
            - Buscar en el ABB
            - Si alguna está ocupada, retornar False
        """
        for coord in coordinates:
            code = coordinate_to_code(coord)
            node = bst.search(code)
            
            if node and node.data and node.data.get("occupied", False):
                return False, f"La coordenada {coord} ya está ocupada"
        
        return True, ""
    
    @staticmethod
    def mark_coordinates_occupied(
        coordinates: List[str],
        bst: BinarySearchTree,
        ship_reference: any
    ) -> None:
        """
        Marca coordenadas como ocupadas en el ABB.
        
        Args:
            coordinates: Lista de coordenadas a marcar
            bst: ABB del juego
            ship_reference: Referencia al nodo del barco en el árbol N-ario
        
        Proceso:
            - Convertir cada coordenada a código
            - Actualizar en ABB con referencia al barco
        """
        for coord in coordinates:
            code = coordinate_to_code(coord)
            node = bst.search(code)
            
            if node:
                if node.data is None:
                    node.data = {}
                node.data["occupied"] = True
                node.data["ship_reference"] = ship_reference
                node.data["coordinate"] = coord
