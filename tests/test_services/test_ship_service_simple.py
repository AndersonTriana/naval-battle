"""
Tests simplificados para ShipService.
"""
import pytest
from app.services.ship_service import ShipService


class TestShipServiceBasics:
    """Tests básicos de ShipService."""
    
    def test_create_fleet_tree(self):
        """Crear árbol de flota."""
        player_id = "player-123"
        tree = ShipService.create_fleet_tree(player_id)
        
        assert tree is not None
        assert tree.root is not None
        assert tree.root.data["player_id"] == player_id
    
    def test_create_ship_instance(self):
        """Crear instancia de barco."""
        from app.storage.in_memory_store import create_ship_template
        
        # Crear plantilla primero
        template = create_ship_template(
            name="Portaaviones",
            size=5,
            description="Barco grande",
            created_by="admin"
        )
        
        # Crear instancia
        ship_instance = ShipService.create_ship_instance(
            template.id,
            ["A1", "A2", "A3", "A4", "A5"]
        )
        
        assert ship_instance is not None
        assert ship_instance.ship_name == "Portaaviones"
        assert ship_instance.size == 5
        assert len(ship_instance.segments) == 5
