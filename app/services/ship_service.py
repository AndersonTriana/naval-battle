"""
Servicio para gestión de barcos y árbol N-ario de flota.
"""
from typing import List, Optional, Dict
from app.structures.n_ary_tree import NaryTree, TreeNode
from app.structures.coordinate_utils import (
    get_adjacent_coordinates,
    coordinates_overlap,
    coordinate_to_code
)
from app.storage.data_models import ShipInstanceData, ShipSegmentData
from app.storage.in_memory_store import get_ship_template


class ShipService:
    """Servicio para gestión de barcos usando árbol N-ario."""
    
    @staticmethod
    def create_fleet_tree(player_id: str) -> NaryTree:
        """
        Crea un árbol N-ario para la flota de un jugador.
        
        Estructura:
        Raíz (Jugador) → Barco1 → Barco2 → ...
                           ↓
                        Segmento1 → Segmento2 → ...
        
        Args:
            player_id: ID del jugador
        
        Returns:
            Árbol N-ario inicializado con el jugador como raíz
        """
        root_data = {
            "type": "player",
            "player_id": player_id
        }
        
        return NaryTree(root_data=root_data)
    
    @staticmethod
    def add_ship_to_fleet(fleet_tree: NaryTree, ship_data: ShipInstanceData) -> TreeNode:
        """
        Agrega un barco al árbol de flota.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
            ship_data: Datos del barco a agregar
        
        Returns:
            Nodo del barco creado
        """
        ship_node_data = {
            "type": "ship",
            "ship_template_id": ship_data.ship_template_id,
            "ship_name": ship_data.ship_name,
            "size": ship_data.size,
            "is_sunk": ship_data.is_sunk
        }
        
        # Agregar barco como hijo de la raíz (jugador)
        ship_node = fleet_tree.add_child(fleet_tree.root, ship_node_data)
        
        # Agregar segmentos como hijos del barco
        for segment in ship_data.segments:
            segment_node_data = {
                "type": "segment",
                "coordinate": segment.coordinate,
                "coordinate_code": segment.coordinate_code,
                "is_hit": segment.is_hit
            }
            fleet_tree.add_child(ship_node, segment_node_data)
        
        return ship_node
    
    @staticmethod
    def validate_ship_placement(
        board_size: int,
        start_coordinate: str,
        orientation: str,
        ship_size: int,
        occupied_coordinates: Dict[int, str]
    ) -> tuple[bool, str, List[str]]:
        """
        Valida si un barco puede ser colocado en una posición.
        
        Args:
            board_size: Tamaño del tablero
            start_coordinate: Coordenada inicial
            orientation: "horizontal" o "vertical"
            ship_size: Tamaño del barco
            occupied_coordinates: Diccionario de coordenadas ocupadas
        
        Returns:
            Tupla (es_válido, mensaje, coordenadas)
        """
        try:
            # Obtener coordenadas que ocuparía el barco
            ship_coordinates = get_adjacent_coordinates(
                start_coordinate, board_size, orientation, ship_size
            )
        except ValueError as e:
            return False, str(e), []
        
        # Verificar si alguna coordenada ya está ocupada
        for coord in ship_coordinates:
            code = coordinate_to_code(coord)
            if code in occupied_coordinates:
                return False, f"La coordenada {coord} ya está ocupada", []
        
        return True, "Posición válida", ship_coordinates
    
    @staticmethod
    def create_ship_instance(
        ship_template_id: str,
        coordinates: List[str]
    ) -> Optional[ShipInstanceData]:
        """
        Crea una instancia de barco con sus segmentos.
        
        Args:
            ship_template_id: ID de la plantilla de barco
            coordinates: Lista de coordenadas del barco
        
        Returns:
            Instancia de barco o None si la plantilla no existe
        """
        template = get_ship_template(ship_template_id)
        if not template:
            return None
        
        segments = []
        for coord in coordinates:
            segment = ShipSegmentData(
                coordinate=coord,
                coordinate_code=coordinate_to_code(coord),
                is_hit=False
            )
            segments.append(segment)
        
        return ShipInstanceData(
            ship_template_id=ship_template_id,
            ship_name=template.name,
            size=template.size,
            segments=segments,
            is_sunk=False
        )
    
    @staticmethod
    def find_ship_by_coordinate(
        fleet_tree: NaryTree,
        coordinate_code: int
    ) -> Optional[TreeNode]:
        """
        Encuentra el barco que contiene una coordenada específica.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
            coordinate_code: Código de la coordenada
        
        Returns:
            Nodo del barco o None si no se encuentra
        """
        # Recorrer todos los barcos (hijos de la raíz)
        ships = fleet_tree.get_children(fleet_tree.root)
        
        for ship_node in ships:
            # Recorrer segmentos del barco
            segments = fleet_tree.get_children(ship_node)
            
            for segment_node in segments:
                if segment_node.data.get("coordinate_code") == coordinate_code:
                    return ship_node
        
        return None
    
    @staticmethod
    def hit_ship_segment(
        fleet_tree: NaryTree,
        ship_node: TreeNode,
        coordinate_code: int
    ) -> tuple[bool, bool]:
        """
        Marca un segmento de barco como impactado y verifica si se hundió.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
            ship_node: Nodo del barco
            coordinate_code: Código de la coordenada impactada
        
        Returns:
            Tupla (segmento_encontrado, barco_hundido)
        """
        segments = fleet_tree.get_children(ship_node)
        segment_found = False
        
        # Marcar el segmento como impactado
        for segment_node in segments:
            if segment_node.data.get("coordinate_code") == coordinate_code:
                segment_node.data["is_hit"] = True
                segment_found = True
                break
        
        if not segment_found:
            return False, False
        
        # Verificar si todos los segmentos están impactados (barco hundido)
        all_hit = all(seg.data.get("is_hit", False) for seg in segments)
        
        if all_hit:
            ship_node.data["is_sunk"] = True
        
        return True, all_hit
    
    @staticmethod
    def get_fleet_status(fleet_tree: NaryTree) -> Dict:
        """
        Obtiene el estado completo de la flota.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
        
        Returns:
            Diccionario con estadísticas de la flota
        """
        ships = fleet_tree.get_children(fleet_tree.root)
        
        total_ships = len(ships)
        sunk_ships = sum(1 for ship in ships if ship.data.get("is_sunk", False))
        
        total_segments = 0
        hit_segments = 0
        
        for ship_node in ships:
            segments = fleet_tree.get_children(ship_node)
            total_segments += len(segments)
            hit_segments += sum(1 for seg in segments if seg.data.get("is_hit", False))
        
        return {
            "total_ships": total_ships,
            "ships_remaining": total_ships - sunk_ships,
            "ships_sunk": sunk_ships,
            "total_segments": total_segments,
            "hit_segments": hit_segments,
            "all_ships_sunk": sunk_ships == total_ships
        }
    
    @staticmethod
    def get_ships_list(fleet_tree: NaryTree) -> List[Dict]:
        """
        Obtiene la lista de todos los barcos con su estado.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
        
        Returns:
            Lista de diccionarios con información de cada barco
        """
        ships = fleet_tree.get_children(fleet_tree.root)
        ships_list = []
        
        for ship_node in ships:
            segments = fleet_tree.get_children(ship_node)
            
            segments_data = [
                {
                    "coordinate": seg.data.get("coordinate"),
                    "coordinate_code": seg.data.get("coordinate_code"),
                    "is_hit": seg.data.get("is_hit", False)
                }
                for seg in segments
            ]
            
            ship_info = {
                "ship_template_id": ship_node.data.get("ship_template_id"),
                "ship_name": ship_node.data.get("ship_name"),
                "size": ship_node.data.get("size"),
                "is_sunk": ship_node.data.get("is_sunk", False),
                "segments": segments_data
            }
            
            ships_list.append(ship_info)
        
        return ships_list
    
    @staticmethod
    def check_all_ships_placed(fleet_tree: NaryTree, required_ship_count: int) -> bool:
        """
        Verifica si todos los barcos requeridos han sido colocados.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
            required_ship_count: Número de barcos requeridos
        
        Returns:
            True si todos los barcos están colocados
        """
        ships = fleet_tree.get_children(fleet_tree.root)
        return len(ships) >= required_ship_count
    
    @staticmethod
    def get_ship_by_coordinate(
        coordinate_code: int,
        fleet_tree: NaryTree
    ) -> tuple[bool, Optional[Dict]]:
        """
        Busca si hay un barco en una coordenada específica.
        
        Args:
            coordinate_code: Código de la coordenada a buscar
            fleet_tree: Árbol N-ario de la flota
        
        Returns:
            (hay_barco, info_barco)
            
            info_barco contiene:
            {
                "ship_name": str,
                "ship_node": Node,
                "segment_node": Node
            }
        """
        ship_node = ShipService.find_ship_by_coordinate(fleet_tree, coordinate_code)
        
        if ship_node is None:
            return False, None
        
        # Encontrar el segmento específico
        segments = fleet_tree.get_children(ship_node)
        segment_node = None
        
        for seg in segments:
            if seg.data.get("coordinate_code") == coordinate_code:
                segment_node = seg
                break
        
        if segment_node is None:
            return False, None
        
        return True, {
            "ship_name": ship_node.data.get("ship_name"),
            "ship_node": ship_node,
            "segment_node": segment_node
        }
    
    @staticmethod
    def mark_segment_as_hit(ship_node: any, coordinate_code: int) -> bool:
        """
        Marca un segmento del barco como impactado.
        
        Args:
            ship_node: Nodo del barco en el árbol N-ario
            coordinate_code: Código de la coordenada del segmento impactado
        
        Returns:
            True si el barco está completamente hundido
        
        Proceso:
            1. Recorrer los hijos (segmentos) del nodo barco
            2. Encontrar el segmento con la coordenada
            3. Marcar is_hit = True
            4. Verificar si todos los segmentos están impactados
        """
        # Esta función ya está implementada en hit_ship_segment
        # pero la exponemos con este nombre también
        _, is_sunk = ShipService.hit_ship_segment(
            None,  # fleet_tree no es necesario aquí
            ship_node,
            coordinate_code
        )
        return is_sunk
    
    @staticmethod
    def is_ship_already_placed(fleet_tree: NaryTree, ship_template_id: str) -> bool:
        """
        Verifica si un barco específico ya fue colocado.
        
        Args:
            fleet_tree: Árbol N-ario de la flota
            ship_template_id: ID de la plantilla de barco
        
        Returns:
            True si el barco ya fue colocado
        """
        ships = fleet_tree.get_children(fleet_tree.root)
        
        for ship in ships:
            if ship.data.get("ship_template_id") == ship_template_id:
                return True
        
        return False
