"""
Tests de integración para el Árbol Binario de Búsqueda (ABB).
Verifica que la implementación funciona correctamente para el caso de uso del juego.
"""
import pytest
import math
from app.structures.binary_search_tree import BinarySearchTree
from app.structures.abb_node import Node
from app.structures.coordinate_utils import (
    coordinate_to_code,
    generate_coordinate_codes,
    balance_array_for_bst
)


class TestABBImport:
    """Tests de importación del ABB."""
    
    def test_abb_import(self):
        """Verificar que se puede importar el ABB."""
        assert BinarySearchTree is not None
        assert Node is not None
    
    def test_abb_has_required_methods(self):
        """Verificar que el ABB tiene los métodos necesarios."""
        bst = BinarySearchTree()
        assert hasattr(bst, 'insert')
        assert hasattr(bst, 'search')
        assert hasattr(bst, 'delete')
        assert hasattr(bst, 'inOrder')
        assert hasattr(bst, 'size')


class TestCoordinateEncoding:
    """Tests de codificación de coordenadas."""
    
    def test_coordinate_encoding_a1(self):
        """Verificar codificación A1 -> 11."""
        assert coordinate_to_code("A1") == 11
    
    def test_coordinate_encoding_b3(self):
        """Verificar codificación B3 -> 23."""
        assert coordinate_to_code("B3") == 23
    
    def test_coordinate_encoding_j10(self):
        """Verificar codificación J10 -> 100."""
        assert coordinate_to_code("J10") == 100
    
    def test_coordinate_encoding_case_insensitive(self):
        """Verificar que la codificación es case-insensitive."""
        assert coordinate_to_code("a1") == 11
        assert coordinate_to_code("A1") == 11


class TestGenerateAllCoordinates:
    """Tests de generación de coordenadas."""
    
    def test_generate_coordinates_5x5(self, sample_coordinates_5x5):
        """Generar todas las coordenadas para un tablero 5x5."""
        coords = sample_coordinates_5x5
        assert len(coords) == 25
        assert coords[0] == 11  # A1
        assert coords[-1] == 55  # E5
    
    def test_generate_coordinates_10x10(self, sample_coordinates_10x10):
        """Generar todas las coordenadas para un tablero 10x10."""
        coords = sample_coordinates_10x10
        assert len(coords) == 100
        assert coords[0] == 11  # A1
        assert coords[-1] == 100  # J10
    
    def test_generate_coordinates_sequential(self):
        """Verificar que las coordenadas se generan secuencialmente."""
        coords = generate_coordinate_codes(3)
        expected = [11, 12, 13, 21, 22, 23, 31, 32, 33]
        assert coords == expected


class TestBalancedInsertion:
    """Tests del algoritmo de reordenamiento para inserción balanceada."""
    
    def test_reorder_for_balanced_insertion(self, balanced_coordinates_array):
        """Verificar algoritmo de reordenamiento por el medio recursivo."""
        coords = balanced_coordinates_array  # [11, 12, 13, 14, 15, 16, 17]
        reordered = balance_array_for_bst(coords)
        
        # El primer elemento debe ser el del medio
        assert reordered[0] == 14
        
        # Verificar que todos los elementos están presentes
        assert sorted(reordered) == sorted(coords)
        assert len(reordered) == len(coords)
    
    def test_reorder_empty_array(self):
        """Verificar que un array vacío retorna array vacío."""
        assert balance_array_for_bst([]) == []
    
    def test_reorder_single_element(self):
        """Verificar que un array con un elemento retorna el mismo elemento."""
        assert balance_array_for_bst([11]) == [11]
    
    def test_reorder_two_elements(self):
        """Verificar que un array con dos elementos se reordena correctamente."""
        result = balance_array_for_bst([11, 12])
        assert result[0] == 11 or result[0] == 12  # Cualquiera puede ser primero
        assert len(result) == 2


class TestABBBalancedInsertion:
    """Tests de inserción balanceada en el ABB."""
    
    def test_abb_balanced_insertion(self):
        """Insertar coordenadas reordenadas y verificar que el ABB está balanceado."""
        coords = generate_coordinate_codes(5)  # 25 coordenadas
        balanced_coords = balance_array_for_bst(coords)
        
        bst = BinarySearchTree()
        for code in balanced_coords:
            node = Node(id=code, data={"coordinate": code})
            bst.insert(node)
        
        # Verificar que se insertaron todas
        assert bst.size() == 25
        
        # Verificar que el árbol está relativamente balanceado
        # Altura esperada: log2(25) ≈ 4.64, permitimos hasta 7
        height = self._calculate_height(bst.root)
        expected_height = math.ceil(math.log2(25))
        assert height <= expected_height + 2  # Permitir margen de error
    
    def test_abb_insertion_order_matters(self):
        """Verificar que el orden de inserción afecta el balance."""
        # Inserción secuencial (peor caso)
        bst_sequential = BinarySearchTree()
        for i in range(11, 18):
            bst_sequential.insert(Node(id=i))
        height_sequential = self._calculate_height(bst_sequential.root)
        
        # Inserción balanceada
        coords = list(range(11, 18))
        balanced_coords = balance_array_for_bst(coords)
        bst_balanced = BinarySearchTree()
        for code in balanced_coords:
            bst_balanced.insert(Node(id=code))
        height_balanced = self._calculate_height(bst_balanced.root)
        
        # El árbol balanceado debe tener menor o igual altura
        assert height_balanced <= height_sequential
    
    def _calculate_height(self, node) -> int:
        """Calcular altura del árbol recursivamente."""
        if node is None:
            return 0
        left_height = self._calculate_height(node.left)
        right_height = self._calculate_height(node.right)
        return 1 + max(left_height, right_height)


class TestABBSearch:
    """Tests de búsqueda en el ABB."""
    
    def test_abb_search_existing_coordinate(self):
        """Buscar una coordenada que existe en el ABB."""
        bst = BinarySearchTree()
        coords = [11, 12, 13, 21, 22]
        
        for code in coords:
            bst.insert(Node(id=code, data={"coordinate": code}))
        
        # Buscar coordenada existente
        node = bst.search(13)
        assert node is not None
        assert node.id == 13
    
    def test_abb_search_non_existing_coordinate(self):
        """Buscar una coordenada que NO existe en el ABB."""
        bst = BinarySearchTree()
        coords = [11, 12, 13]
        
        for code in coords:
            bst.insert(Node(id=code))
        
        # Buscar coordenada no existente
        node = bst.search(99)
        assert node is None
    
    def test_abb_search_in_empty_tree(self):
        """Buscar en un árbol vacío."""
        bst = BinarySearchTree()
        node = bst.search(11)
        assert node is None
    
    def test_abb_search_all_coordinates(self):
        """Verificar que todas las coordenadas insertadas se pueden buscar."""
        bst = BinarySearchTree()
        coords = generate_coordinate_codes(5)
        balanced_coords = balance_array_for_bst(coords)
        
        for code in balanced_coords:
            bst.insert(Node(id=code))
        
        # Buscar todas las coordenadas
        for code in coords:
            node = bst.search(code)
            assert node is not None
            assert node.id == code


class TestABBOperations:
    """Tests de operaciones adicionales del ABB."""
    
    def test_abb_size(self):
        """Verificar que size() retorna el número correcto de nodos."""
        bst = BinarySearchTree()
        assert bst.size() == 0
        
        bst.insert(Node(id=11))
        assert bst.size() == 1
        
        bst.insert(Node(id=12))
        assert bst.size() == 2
    
    def test_abb_is_empty(self):
        """Verificar que is_empty() funciona correctamente."""
        bst = BinarySearchTree()
        assert bst.is_empty() is True
        
        bst.insert(Node(id=11))
        assert bst.is_empty() is False
    
    def test_abb_inorder_traversal(self):
        """Verificar que inOrder() retorna nodos en orden ascendente."""
        bst = BinarySearchTree()
        coords = [14, 12, 16, 11, 13, 15, 17]
        
        for code in coords:
            bst.insert(Node(id=code))
        
        result = bst.inOrder()
        ids = [node["id"] for node in result]
        
        # Debe estar ordenado ascendentemente
        assert ids == sorted(ids)
        assert ids == [11, 12, 13, 14, 15, 16, 17]
    
    def test_abb_delete_node(self):
        """Verificar que delete() elimina un nodo correctamente."""
        bst = BinarySearchTree()
        coords = [14, 12, 16, 11, 13]
        
        for code in coords:
            bst.insert(Node(id=code))
        
        assert bst.size() == 5
        
        # Eliminar nodo
        deleted = bst.delete(13)
        assert deleted is True
        assert bst.size() == 4
        
        # Verificar que no se puede encontrar
        node = bst.search(13)
        assert node is None
    
    def test_abb_delete_non_existing(self):
        """Verificar que delete() retorna False si el nodo no existe."""
        bst = BinarySearchTree()
        bst.insert(Node(id=11))
        
        deleted = bst.delete(99)
        assert deleted is False
        assert bst.size() == 1
