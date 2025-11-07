"""
Tests para el Árbol N-ario (Padre → Lista de Hijos).
Valida la implementación de la estructura de datos para gestión de flota.
"""
import pytest
from app.structures.n_ary_tree import NaryTree, TreeNode


class TestTreeNode:
    """Tests del nodo del árbol N-ario."""
    
    def test_create_tree_node(self):
        """Crear un nodo del árbol."""
        node = TreeNode(data={"type": "player", "id": "player1"})
        assert node.data["type"] == "player"
        assert len(node.children) == 0
    
    def test_tree_node_repr(self):
        """Verificar representación en string del nodo."""
        node = TreeNode(data={"name": "Portaaviones"})
        assert "Portaaviones" in repr(node)


class TestCreateTree:
    """Tests de creación del árbol N-ario."""
    
    def test_create_empty_tree(self):
        """Crear árbol N-ario con raíz."""
        tree = NaryTree(root_data={"type": "player", "id": "player1"})
        assert tree.root is not None
        assert tree.root.data["type"] == "player"
    
    def test_add_root_node(self):
        """Verificar que la raíz se crea correctamente."""
        tree = NaryTree(root_data={"player_id": "test-player"})
        assert tree.root.data["player_id"] == "test-player"
        assert len(tree.root.children) == 0


class TestAddChildNode:
    """Tests de agregar nodos hijos."""
    
    def test_add_child_node(self):
        """Agregar nodo hijo (barco) al jugador."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship_node = tree.add_child(tree.root, {"type": "ship", "name": "Portaaviones"})
        
        assert len(tree.root.children) == 1
        assert tree.root.children[0] == ship_node
        assert ship_node.data["name"] == "Portaaviones"
    
    def test_add_multiple_children(self):
        """Agregar múltiples hijos al mismo padre."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship1 = tree.add_child(tree.root, {"name": "Portaaviones"})
        ship2 = tree.add_child(tree.root, {"name": "Acorazado"})
        ship3 = tree.add_child(tree.root, {"name": "Crucero"})
        
        # Verificar que están en la lista de hijos
        assert len(tree.root.children) == 3
        assert tree.root.children[0] == ship1
        assert tree.root.children[1] == ship2
        assert tree.root.children[2] == ship3


class TestAddSiblingNode:
    """Tests de agregar nodos hermanos."""
    
    def test_add_sibling_node(self):
        """Agregar hermano (otro barco) en la lista de hijos."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship1 = tree.add_child(tree.root, {"name": "Portaaviones"})
        ship2 = tree.add_child(tree.root, {"name": "Acorazado"})
        
        # Verificar que ambos están en la lista de hijos
        assert len(tree.root.children) == 2
        assert tree.root.children[0] == ship1
        assert tree.root.children[1] == ship2
    
    def test_sibling_chain(self):
        """Verificar lista de hermanos."""
        tree = NaryTree(root_data={"type": "player"})
        
        ships = []
        for i in range(5):
            ship = tree.add_child(tree.root, {"name": f"Ship{i}"})
            ships.append(ship)
        
        # Verificar que todos están en la lista
        assert len(tree.root.children) == 5
        for i in range(5):
            assert tree.root.children[i] == ships[i]


class TestAddGrandchildNode:
    """Tests de agregar nodos nietos."""
    
    def test_add_grandchild_node(self):
        """Agregar nieto (segmento de barco)."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship = tree.add_child(tree.root, {"type": "ship", "name": "Portaaviones"})
        segment = tree.add_child(ship, {"type": "segment", "coordinate": "A1"})
        
        assert len(ship.children) == 1
        assert ship.children[0] == segment
        assert segment.data["coordinate"] == "A1"
    
    def test_add_multiple_grandchildren(self):
        """Agregar múltiples segmentos a un barco."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship = tree.add_child(tree.root, {"name": "Portaaviones", "size": 5})
        
        segments = []
        for i in range(5):
            seg = tree.add_child(ship, {"coordinate": f"A{i+1}", "is_hit": False})
            segments.append(seg)
        
        # Verificar que están en la lista de hijos
        assert len(ship.children) == 5
        for i in range(5):
            assert ship.children[i] == segments[i]


class TestTraverseTree:
    """Tests de recorrido del árbol."""
    
    def test_traverse_tree(self):
        """Recorrer todo el árbol y obtener todos los nodos."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship1 = tree.add_child(tree.root, {"name": "Ship1"})
        ship2 = tree.add_child(tree.root, {"name": "Ship2"})
        
        tree.add_child(ship1, {"segment": "A1"})
        tree.add_child(ship1, {"segment": "A2"})
        
        result = tree.traverse_preorder()
        
        # Debe incluir: raíz + 2 barcos + 2 segmentos = 5 nodos
        assert len(result) == 5
    
    def test_traverse_empty_children(self):
        """Recorrer árbol con solo raíz."""
        tree = NaryTree(root_data={"type": "player"})
        result = tree.traverse_preorder()
        
        assert len(result) == 1
        assert result[0][1].data["type"] == "player"
    
    def test_traverse_with_levels(self):
        """Verificar que el recorrido incluye niveles."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship = tree.add_child(tree.root, {"name": "Ship"})
        segment = tree.add_child(ship, {"segment": "A1"})
        
        result = tree.traverse_preorder()
        
        # Verificar niveles: 0 (raíz), 1 (barco), 2 (segmento)
        assert result[0][0] == 0  # Nivel raíz
        assert result[1][0] == 1  # Nivel barco
        assert result[2][0] == 2  # Nivel segmento


class TestFindNode:
    """Tests de búsqueda de nodos."""
    
    def test_find_node_by_data(self):
        """Buscar un nodo específico por su data."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship1 = tree.add_child(tree.root, {"name": "Portaaviones", "id": "ship1"})
        ship2 = tree.add_child(tree.root, {"name": "Acorazado", "id": "ship2"})
        
        # Buscar por predicado
        found = tree.find_child_by_data(tree.root, lambda d: d.get("id") == "ship2")
        
        assert found is not None
        assert found == ship2
        assert found.data["name"] == "Acorazado"
    
    def test_find_node_not_found(self):
        """Buscar un nodo que no existe."""
        tree = NaryTree(root_data={"type": "player"})
        tree.add_child(tree.root, {"name": "Ship1"})
        
        found = tree.find_child_by_data(tree.root, lambda d: d.get("name") == "NonExistent")
        
        assert found is None


class TestTreeStructure:
    """Tests de verificación de estructura del árbol."""
    
    def test_tree_structure_complete_fleet(self):
        """Verificar estructura correcta: raíz->hijos->nietos."""
        tree = NaryTree(root_data={"type": "player", "id": "player1"})
        
        # Agregar barcos
        portaaviones = tree.add_child(tree.root, {
            "type": "ship",
            "name": "Portaaviones",
            "size": 5
        })
        acorazado = tree.add_child(tree.root, {
            "type": "ship",
            "name": "Acorazado",
            "size": 4
        })
        
        # Agregar segmentos al portaaviones
        for i in range(5):
            tree.add_child(portaaviones, {
                "type": "segment",
                "coordinate": f"A{i+1}",
                "is_hit": False
            })
        
        # Agregar segmentos al acorazado
        for i in range(4):
            tree.add_child(acorazado, {
                "type": "segment",
                "coordinate": f"C{i+1}",
                "is_hit": False
            })
        
        # Verificar estructura
        assert len(tree.root.children) == 2
        assert tree.root.children[0] == portaaviones
        assert tree.root.children[1] == acorazado
        
        # Verificar segmentos del portaaviones
        assert len(portaaviones.children) == 5
        segments = tree.get_children(portaaviones)
        assert len(segments) == 5
        
        # Verificar segmentos del acorazado
        assert len(acorazado.children) == 4
        segments = tree.get_children(acorazado)
        assert len(segments) == 4


class TestGetChildren:
    """Tests de obtención de hijos."""
    
    def test_get_children(self):
        """Obtener todos los hijos de un nodo."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship1 = tree.add_child(tree.root, {"name": "Ship1"})
        ship2 = tree.add_child(tree.root, {"name": "Ship2"})
        ship3 = tree.add_child(tree.root, {"name": "Ship3"})
        
        children = tree.get_children(tree.root)
        
        assert len(children) == 3
        assert ship1 in children
        assert ship2 in children
        assert ship3 in children
    
    def test_get_children_empty(self):
        """Obtener hijos de un nodo sin hijos."""
        tree = NaryTree(root_data={"type": "player"})
        children = tree.get_children(tree.root)
        
        assert len(children) == 0
        assert children == []


class TestCountChildren:
    """Tests de conteo de hijos."""
    
    def test_count_children(self):
        """Contar el número de hijos directos."""
        tree = NaryTree(root_data={"type": "player"})
        
        tree.add_child(tree.root, {"name": "Ship1"})
        tree.add_child(tree.root, {"name": "Ship2"})
        tree.add_child(tree.root, {"name": "Ship3"})
        
        count = tree.count_children(tree.root)
        assert count == 3
    
    def test_count_children_zero(self):
        """Contar hijos cuando no hay ninguno."""
        tree = NaryTree(root_data={"type": "player"})
        count = tree.count_children(tree.root)
        assert count == 0


class TestTreeOperations:
    """Tests de operaciones adicionales del árbol."""
    
    def test_to_dict(self):
        """Convertir árbol a diccionario."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship = tree.add_child(tree.root, {"name": "Ship"})
        tree.add_child(ship, {"segment": "A1"})
        
        result = tree.to_dict()
        
        assert result["data"]["type"] == "player"
        assert len(result["children"]) == 1
        assert result["children"][0]["data"]["name"] == "Ship"
    
    def test_get_all_leaves(self):
        """Obtener todas las hojas del árbol."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship = tree.add_child(tree.root, {"name": "Ship"})
        seg1 = tree.add_child(ship, {"segment": "A1"})
        seg2 = tree.add_child(ship, {"segment": "A2"})
        
        leaves = tree.get_all_leaves()
        
        # Solo los segmentos son hojas
        assert len(leaves) == 2
        assert seg1 in leaves
        assert seg2 in leaves
    
    def test_update_node_data(self):
        """Actualizar datos de un nodo."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship = tree.add_child(tree.root, {"name": "Ship", "is_sunk": False})
        
        tree.update_node_data(ship, {"name": "Ship", "is_sunk": True})
        
        assert ship.data["is_sunk"] is True
    
    def test_remove_child(self):
        """Eliminar un hijo de un nodo."""
        tree = NaryTree(root_data={"type": "player"})
        
        ship1 = tree.add_child(tree.root, {"name": "Ship1"})
        ship2 = tree.add_child(tree.root, {"name": "Ship2"})
        ship3 = tree.add_child(tree.root, {"name": "Ship3"})
        
        # Eliminar ship2
        removed = tree.remove_child(tree.root, ship2)
        
        assert removed is True
        children = tree.get_children(tree.root)
        assert len(children) == 2
        assert ship2 not in children
