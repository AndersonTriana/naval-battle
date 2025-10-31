"""
Árbol N-ario implementado con la forma 2: First-Child, Next-Sibling.

Esta estructura se utiliza para representar la flota de cada jugador:
- Raíz: Jugador
- Hijos de nivel 1: Barcos
- Hijos de nivel 2: Segmentos de cada barco
"""
from typing import Any, Optional, List, Dict
from dataclasses import dataclass


@dataclass
class TreeNode:
    """
    Nodo del árbol N-ario usando First-Child, Next-Sibling.
    
    Attributes:
        data: Datos almacenados en el nodo
        first_child: Referencia al primer hijo
        next_sibling: Referencia al siguiente hermano
    """
    data: Any
    first_child: Optional['TreeNode'] = None
    next_sibling: Optional['TreeNode'] = None
    
    def __repr__(self) -> str:
        """Representación en string del nodo."""
        return f"TreeNode(data={self.data})"


class NaryTree:
    """
    Árbol N-ario usando la estructura First-Child, Next-Sibling.
    
    Estructura para la flota:
    Raíz (Jugador) → Barco1 → Barco2 → Barco3
                       ↓
                    Segmento1 → Segmento2 → Segmento3
    """
    
    def __init__(self, root_data: Any):
        """
        Inicializa el árbol con un nodo raíz.
        
        Args:
            root_data: Datos del nodo raíz (información del jugador)
        """
        self.root = TreeNode(data=root_data)
    
    def add_child(self, parent: TreeNode, child_data: Any) -> TreeNode:
        """
        Agrega un hijo a un nodo padre.
        
        Args:
            parent: Nodo padre
            child_data: Datos del nuevo hijo
        
        Returns:
            El nuevo nodo hijo creado
        """
        new_child = TreeNode(data=child_data)
        
        if parent.first_child is None:
            # Si no tiene hijos, este será el primero
            parent.first_child = new_child
        else:
            # Si ya tiene hijos, agregarlo como hermano del último
            current = parent.first_child
            while current.next_sibling is not None:
                current = current.next_sibling
            current.next_sibling = new_child
        
        return new_child
    
    def get_children(self, parent: TreeNode) -> List[TreeNode]:
        """
        Obtiene todos los hijos de un nodo.
        
        Args:
            parent: Nodo padre
        
        Returns:
            Lista de nodos hijos
        """
        children = []
        current = parent.first_child
        
        while current is not None:
            children.append(current)
            current = current.next_sibling
        
        return children
    
    def find_child_by_data(self, parent: TreeNode, predicate) -> Optional[TreeNode]:
        """
        Busca un hijo que cumpla con un predicado.
        
        Args:
            parent: Nodo padre
            predicate: Función que retorna True si el nodo cumple la condición
        
        Returns:
            El nodo encontrado o None
        """
        current = parent.first_child
        
        while current is not None:
            if predicate(current.data):
                return current
            current = current.next_sibling
        
        return None
    
    def count_children(self, parent: TreeNode) -> int:
        """
        Cuenta el número de hijos directos de un nodo.
        
        Args:
            parent: Nodo padre
        
        Returns:
            Número de hijos
        """
        count = 0
        current = parent.first_child
        
        while current is not None:
            count += 1
            current = current.next_sibling
        
        return count
    
    def traverse_preorder(self, node: Optional[TreeNode] = None, 
                         level: int = 0) -> List[tuple]:
        """
        Recorre el árbol en pre-orden (raíz, hijos).
        
        Args:
            node: Nodo desde donde iniciar (None = raíz)
            level: Nivel actual en el árbol
        
        Returns:
            Lista de tuplas (nivel, nodo)
        """
        if node is None:
            node = self.root
        
        result = [(level, node)]
        
        # Recorrer todos los hijos
        current_child = node.first_child
        while current_child is not None:
            result.extend(self.traverse_preorder(current_child, level + 1))
            current_child = current_child.next_sibling
        
        return result
    
    def to_dict(self, node: Optional[TreeNode] = None) -> Dict:
        """
        Convierte el árbol a un diccionario para serialización.
        
        Args:
            node: Nodo desde donde iniciar (None = raíz)
        
        Returns:
            Diccionario representando el árbol
        """
        if node is None:
            node = self.root
        
        result = {
            "data": node.data,
            "children": []
        }
        
        current_child = node.first_child
        while current_child is not None:
            result["children"].append(self.to_dict(current_child))
            current_child = current_child.next_sibling
        
        return result
    
    def get_all_leaves(self, node: Optional[TreeNode] = None) -> List[TreeNode]:
        """
        Obtiene todas las hojas del árbol (nodos sin hijos).
        
        Args:
            node: Nodo desde donde iniciar (None = raíz)
        
        Returns:
            Lista de nodos hoja
        """
        if node is None:
            node = self.root
        
        leaves = []
        
        if node.first_child is None:
            # Es una hoja
            leaves.append(node)
        else:
            # Recorrer todos los hijos
            current_child = node.first_child
            while current_child is not None:
                leaves.extend(self.get_all_leaves(current_child))
                current_child = current_child.next_sibling
        
        return leaves
    
    def update_node_data(self, node: TreeNode, new_data: Any) -> None:
        """
        Actualiza los datos de un nodo.
        
        Args:
            node: Nodo a actualizar
            new_data: Nuevos datos
        """
        node.data = new_data
    
    def remove_child(self, parent: TreeNode, child_to_remove: TreeNode) -> bool:
        """
        Elimina un hijo de un nodo padre.
        
        Args:
            parent: Nodo padre
            child_to_remove: Nodo hijo a eliminar
        
        Returns:
            True si se eliminó, False si no se encontró
        """
        if parent.first_child is None:
            return False
        
        # Caso especial: el hijo a eliminar es el primero
        if parent.first_child == child_to_remove:
            parent.first_child = child_to_remove.next_sibling
            return True
        
        # Buscar en los hermanos
        current = parent.first_child
        while current.next_sibling is not None:
            if current.next_sibling == child_to_remove:
                current.next_sibling = child_to_remove.next_sibling
                return True
            current = current.next_sibling
        
        return False
    
    def add_ship(self, ship_data: dict) -> TreeNode:
        """
        Agrega un barco a la flota (hijo de raíz).
        
        Args:
            ship_data: Información del barco
        
        Returns:
            Nodo del barco creado
        """
        from app.structures.coordinate_utils import coordinate_to_code
        
        # Crear datos del barco sin las coordenadas
        barco_data = {
            "ship_template_id": ship_data.get("ship_template_id"),
            "name": ship_data.get("name"),
            "size": ship_data.get("size"),
            "type": "ship"
        }
        
        # Agregar barco como hijo de raíz
        ship_node = self.add_child(self.root, barco_data)
        
        # Agregar segmentos si hay coordenadas
        if "coordinates" in ship_data:
            for coord in ship_data["coordinates"]:
                segment_data = {
                    "coordinate": coord,
                    "coordinate_code": coordinate_to_code(coord),
                    "is_hit": False,
                    "type": "segment"
                }
                self.add_child(ship_node, segment_data)
        
        return ship_node
    
    def add_segment_to_ship(self, ship_node: TreeNode, segment_data: dict) -> TreeNode:
        """Agrega un segmento a un barco."""
        segment_data["type"] = "segment"
        return self.add_child(ship_node, segment_data)
    
    def get_all_ships(self) -> List[TreeNode]:
        """Obtiene todos los barcos de la flota."""
        return self.get_children(self.root)
    
    def find_ship_by_name(self, ship_name: str) -> Optional[TreeNode]:
        """Busca un barco por su nombre."""
        return self.find_child_by_data(
            self.root,
            lambda data: data.get("name") == ship_name
        )
    
    def get_ship_segments(self, ship_node: TreeNode) -> List[TreeNode]:
        """Obtiene todos los segmentos de un barco."""
        return self.get_children(ship_node)
    
    def is_ship_sunk(self, ship_node: TreeNode) -> bool:
        """Verifica si un barco está completamente hundido."""
        segments = self.get_ship_segments(ship_node)
        if not segments:
            return False
        return all(seg.data.get("is_hit", False) for seg in segments)
    
    def count_sunk_ships(self) -> int:
        """Cuenta cuántos barcos están completamente hundidos."""
        ships = self.get_all_ships()
        return sum(1 for ship in ships if self.is_ship_sunk(ship))
    
    def count_total_ships(self) -> int:
        """Cuenta el total de barcos en la flota."""
        return len(self.get_all_ships())
    
    def mark_segment_hit(self, coordinate: str) -> tuple[bool, Optional[str]]:
        """Marca un segmento como impactado por coordenada."""
        ships = self.get_all_ships()
        
        for ship in ships:
            segments = self.get_ship_segments(ship)
            
            for segment in segments:
                if segment.data.get("coordinate") == coordinate:
                    segment.data["is_hit"] = True
                    ship_sunk = self.is_ship_sunk(ship)
                    ship_name = ship.data.get("name")
                    return ship_sunk, ship_name
        
        return False, None
