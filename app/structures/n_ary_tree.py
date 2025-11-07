"""
Árbol N-ario implementado con la estructura: Padre → Lista de Hijos.

Esta estructura se utiliza para representar la flota de cada jugador:
- Raíz: Jugador
- Hijos de nivel 1: Barcos
- Hijos de nivel 2: Segmentos de cada barco
"""
from typing import Any, Optional, List, Dict
from dataclasses import dataclass, field


@dataclass
class TreeNode:
    """
    Nodo del árbol N-ario con lista de hijos.
    
    Attributes:
        data: Datos almacenados en el nodo
        children: Lista de nodos hijos
    """
    data: Any
    children: List['TreeNode'] = field(default_factory=list)
    
    def __repr__(self) -> str:
        """Representación en string del nodo."""
        return f"TreeNode(data={self.data}, children={len(self.children)})"


class NaryTree:
    """
    Árbol N-ario usando la estructura Padre → Lista de Hijos.
    
    Estructura para la flota:
    Raíz (Jugador)
      ├─ Barco1
      │   ├─ Segmento1
      │   ├─ Segmento2
      │   └─ Segmento3
      ├─ Barco2
      │   ├─ Segmento1
      │   └─ Segmento2
      └─ Barco3
          └─ ...
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
        parent.children.append(new_child)
        return new_child
    
    def get_children(self, parent: TreeNode) -> List[TreeNode]:
        """
        Obtiene todos los hijos de un nodo.
        
        Args:
            parent: Nodo padre
        
        Returns:
            Lista de nodos hijos
        """
        return parent.children
    
    def find_child_by_data(self, parent: TreeNode, predicate) -> Optional[TreeNode]:
        """
        Busca un hijo que cumpla con un predicado.
        
        Args:
            parent: Nodo padre
            predicate: Función que retorna True si el nodo cumple la condición
        
        Returns:
            El nodo encontrado o None
        """
        for child in parent.children:
            if predicate(child.data):
                return child
        return None
    
    def count_children(self, parent: TreeNode) -> int:
        """
        Cuenta el número de hijos directos de un nodo.
        
        Args:
            parent: Nodo padre
        
        Returns:
            Número de hijos
        """
        return len(parent.children)
    
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
        for child in node.children:
            result.extend(self.traverse_preorder(child, level + 1))
        
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
        
        for child in node.children:
            result["children"].append(self.to_dict(child))
        
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
        
        if len(node.children) == 0:
            # Es una hoja
            leaves.append(node)
        else:
            # Recorrer todos los hijos
            for child in node.children:
                leaves.extend(self.get_all_leaves(child))
        
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
        try:
            parent.children.remove(child_to_remove)
            return True
        except ValueError:
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
