"""
Tests para modelos Pydantic de barcos.
Valida la validación de datos de barcos y plantillas.
"""
import pytest
from pydantic import ValidationError
from datetime import datetime

from app.models.ship import (
    ShipTemplateCreate,
    ShipTemplateUpdate,
    ShipTemplateResponse,
    ShipSegment,
    ShipInstance,
    ShipPlacement
)


class TestShipTemplateCreate:
    """Tests del modelo ShipTemplateCreate."""
    
    def test_ship_template_create_valid(self):
        """Crear plantilla de barco válida."""
        template = ShipTemplateCreate(
            name="Portaaviones",
            size=5,
            description="El barco más grande"
        )
        assert template.name == "Portaaviones"
        assert template.size == 5
        assert template.description == "El barco más grande"
    
    def test_ship_template_create_without_description(self):
        """Crear plantilla sin descripción (opcional)."""
        template = ShipTemplateCreate(name="Acorazado", size=4)
        assert template.name == "Acorazado"
        assert template.size == 4
        assert template.description is None


class TestShipTemplateSizeValidation:
    """Tests de validación del tamaño de barco."""
    
    def test_ship_template_size_minimum(self):
        """Validar tamaño mínimo (1)."""
        template = ShipTemplateCreate(name="Bote", size=1)
        assert template.size == 1
    
    def test_ship_template_size_maximum(self):
        """Validar tamaño máximo (10)."""
        template = ShipTemplateCreate(name="SuperPortaaviones", size=10)
        assert template.size == 10
    
    def test_ship_template_size_zero_invalid(self):
        """Validar que size=0 falla."""
        with pytest.raises(ValidationError) as exc_info:
            ShipTemplateCreate(name="Invalid", size=0)
        
        errors = exc_info.value.errors()
        assert any("size" in str(error) for error in errors)
    
    def test_ship_template_size_negative_invalid(self):
        """Validar que size negativo falla."""
        with pytest.raises(ValidationError):
            ShipTemplateCreate(name="Invalid", size=-1)
    
    def test_ship_template_size_too_large_invalid(self):
        """Validar que size=11 falla."""
        with pytest.raises(ValidationError):
            ShipTemplateCreate(name="Invalid", size=11)


class TestShipTemplateUpdate:
    """Tests del modelo ShipTemplateUpdate."""
    
    def test_ship_template_update_all_fields(self):
        """Actualizar todos los campos."""
        update = ShipTemplateUpdate(
            name="Portaaviones Mejorado",
            size=6,
            description="Versión mejorada"
        )
        assert update.name == "Portaaviones Mejorado"
        assert update.size == 6
        assert update.description == "Versión mejorada"
    
    def test_ship_template_update_partial(self):
        """Actualizar solo algunos campos."""
        update = ShipTemplateUpdate(name="Nuevo Nombre")
        assert update.name == "Nuevo Nombre"
        assert update.size is None
        assert update.description is None
    
    def test_ship_template_update_empty(self):
        """Crear update sin ningún campo."""
        update = ShipTemplateUpdate()
        assert update.name is None
        assert update.size is None
        assert update.description is None


class TestShipTemplateResponse:
    """Tests del modelo ShipTemplateResponse."""
    
    def test_ship_template_response_valid(self):
        """Crear respuesta de plantilla válida."""
        response = ShipTemplateResponse(
            id="550e8400-e29b-41d4-a716-446655440001",
            name="Portaaviones",
            size=5,
            description="Barco grande",
            created_by="user-id",
            created_at=datetime.now()
        )
        assert response.id == "550e8400-e29b-41d4-a716-446655440001"
        assert response.name == "Portaaviones"
        assert response.size == 5


class TestShipSegment:
    """Tests del modelo ShipSegment."""
    
    def test_ship_segment_model(self):
        """Crear segmento de barco con coordenada."""
        segment = ShipSegment(
            coordinate="A1",
            coordinate_code=11,
            is_hit=False
        )
        assert segment.coordinate == "A1"
        assert segment.coordinate_code == 11
        assert segment.is_hit is False
    
    def test_ship_segment_default_is_hit(self):
        """Verificar que is_hit tiene valor por defecto False."""
        segment = ShipSegment(coordinate="B3", coordinate_code=23)
        assert segment.is_hit is False
    
    def test_ship_segment_hit(self):
        """Crear segmento impactado."""
        segment = ShipSegment(
            coordinate="C5",
            coordinate_code=35,
            is_hit=True
        )
        assert segment.is_hit is True


class TestShipInstance:
    """Tests del modelo ShipInstance."""
    
    def test_ship_instance_model(self):
        """Crear instancia de barco."""
        segments = [
            ShipSegment(coordinate="A1", coordinate_code=11, is_hit=False),
            ShipSegment(coordinate="A2", coordinate_code=12, is_hit=True),
            ShipSegment(coordinate="A3", coordinate_code=13, is_hit=False)
        ]
        
        ship = ShipInstance(
            ship_template_id="template-id",
            ship_name="Crucero",
            size=3,
            segments=segments,
            is_sunk=False
        )
        
        assert ship.ship_name == "Crucero"
        assert ship.size == 3
        assert len(ship.segments) == 3
        assert ship.is_sunk is False
    
    def test_ship_instance_default_is_sunk(self):
        """Verificar que is_sunk tiene valor por defecto False."""
        ship = ShipInstance(
            ship_template_id="template-id",
            ship_name="Barco",
            size=2,
            segments=[]
        )
        assert ship.is_sunk is False


class TestShipPlacement:
    """Tests del modelo ShipPlacement."""
    
    def test_ship_placement_model_horizontal(self):
        """Validar modelo de colocación de barco horizontal."""
        placement = ShipPlacement(
            ship_template_id="template-id",
            start_coordinate="A1",
            orientation="horizontal"
        )
        assert placement.ship_template_id == "template-id"
        assert placement.start_coordinate == "A1"
        assert placement.orientation == "horizontal"
    
    def test_ship_placement_model_vertical(self):
        """Validar modelo de colocación de barco vertical."""
        placement = ShipPlacement(
            ship_template_id="template-id",
            start_coordinate="C3",
            orientation="vertical"
        )
        assert placement.orientation == "vertical"


class TestShipPlacementOrientationValidation:
    """Tests de validación de orientación."""
    
    def test_ship_placement_orientation_horizontal_valid(self):
        """Validar que orientation 'horizontal' es válida."""
        placement = ShipPlacement(
            ship_template_id="id",
            start_coordinate="A1",
            orientation="horizontal"
        )
        assert placement.orientation == "horizontal"
    
    def test_ship_placement_orientation_vertical_valid(self):
        """Validar que orientation 'vertical' es válida."""
        placement = ShipPlacement(
            ship_template_id="id",
            start_coordinate="A1",
            orientation="vertical"
        )
        assert placement.orientation == "vertical"
    
    def test_ship_placement_orientation_invalid(self):
        """Validar que orientation inválida falla."""
        with pytest.raises(ValidationError) as exc_info:
            ShipPlacement(
                ship_template_id="id",
                start_coordinate="A1",
                orientation="diagonal"
            )
        
        errors = exc_info.value.errors()
        assert any("orientation" in str(error) for error in errors)
    
    def test_ship_placement_orientation_case_sensitive(self):
        """Verificar que la validación es case-sensitive."""
        with pytest.raises(ValidationError):
            ShipPlacement(
                ship_template_id="id",
                start_coordinate="A1",
                orientation="HORIZONTAL"
            )


class TestShipNameValidation:
    """Tests de validación de nombres de barcos."""
    
    def test_ship_template_name_minimum_length(self):
        """Validar longitud mínima del nombre (1)."""
        template = ShipTemplateCreate(name="A", size=2)
        assert template.name == "A"
    
    def test_ship_template_name_maximum_length(self):
        """Validar longitud máxima del nombre (50)."""
        name = "A" * 50
        template = ShipTemplateCreate(name=name, size=2)
        assert len(template.name) == 50
    
    def test_ship_template_name_too_long(self):
        """Validar que nombre muy largo falla."""
        name = "A" * 51
        with pytest.raises(ValidationError):
            ShipTemplateCreate(name=name, size=2)
    
    def test_ship_template_name_empty(self):
        """Validar que nombre vacío falla."""
        with pytest.raises(ValidationError):
            ShipTemplateCreate(name="", size=2)
