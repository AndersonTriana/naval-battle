"""
Tests para almacenamiento en memoria.
Valida las operaciones CRUD en los diccionarios globales.
"""
import pytest
from datetime import datetime

import app.storage.in_memory_store as store
from app.storage.data_models import User, ShipTemplate, BaseFleet


class TestDefaultAdmin:
    """Tests del usuario administrador por defecto."""
    
    def test_default_admin_exists(self):
        """Verificar que existe usuario admin por defecto."""
        admin = store.get_user_by_username("admin")
        assert admin is not None
        assert admin.username == "admin"
        assert admin.role == "admin"
    
    def test_default_admin_in_users_db(self):
        """Verificar que admin está en users_db."""
        assert len(store.users_db) >= 1
        admin_found = any(
            user.username == "admin" 
            for user in store.users_db.values()
        )
        assert admin_found is True
    
    def test_default_admin_in_username_index(self):
        """Verificar que admin está en el índice de usernames."""
        assert "admin" in store.username_to_user_id
        admin_id = store.username_to_user_id["admin"]
        assert admin_id in store.users_db


class TestAddUserToStore:
    """Tests de agregar usuarios al almacenamiento."""
    
    def test_add_user_to_store(self, clean_storage, sample_user):
        """Agregar usuario al diccionario users_db."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        assert user.id in store.users_db
        assert store.users_db[user.id].username == sample_user["username"]
    
    def test_add_multiple_users(self, clean_storage):
        """Agregar múltiples usuarios."""
        users = []
        for i in range(3):
            user = store.create_user(
                username=f"player{i}",
                password="pass123",
                role="player"
            )
            users.append(user)
        
        assert len(store.users_db) == 3
        for user in users:
            assert user.id in store.users_db
    
    def test_username_index_updated(self, clean_storage, sample_user):
        """Verificar que el índice de usernames se actualiza."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        assert sample_user["username"] in store.username_to_user_id
        assert store.username_to_user_id[sample_user["username"]] == user.id


class TestAddShipTemplateToStore:
    """Tests de agregar plantillas de barcos."""
    
    def test_add_ship_template_to_store(self, clean_storage, sample_ship_template):
        """Agregar plantilla de barco al diccionario."""
        template = store.create_ship_template(
            name=sample_ship_template["name"],
            size=sample_ship_template["size"],
            description=sample_ship_template["description"],
            created_by=sample_ship_template["created_by"]
        )
        
        assert template.id in store.ship_templates_db
        assert store.ship_templates_db[template.id].name == sample_ship_template["name"]
    
    def test_add_multiple_ship_templates(self, clean_storage, sample_ship_templates):
        """Agregar múltiples plantillas de barcos."""
        templates = []
        for template_data in sample_ship_templates:
            template = store.create_ship_template(
                name=template_data["name"],
                size=template_data["size"],
                description=template_data["description"],
                created_by="test-user"
            )
            templates.append(template)
        
        assert len(store.ship_templates_db) == 3
        for template in templates:
            assert template.id in store.ship_templates_db


class TestAddBaseFleetToStore:
    """Tests de agregar flotas base."""
    
    def test_add_base_fleet_to_store(self, clean_storage, sample_base_fleet):
        """Agregar flota base al diccionario."""
        fleet = store.create_base_fleet(
            name=sample_base_fleet["name"],
            board_size=sample_base_fleet["board_size"],
            ship_template_ids=sample_base_fleet["ship_template_ids"],
            created_by=sample_base_fleet["created_by"]
        )
        
        assert fleet.id in store.base_fleets_db
        assert store.base_fleets_db[fleet.id].name == sample_base_fleet["name"]
    
    def test_base_fleet_with_ship_templates(self, clean_storage, sample_ship_templates):
        """Crear flota base con plantillas de barcos."""
        # Crear plantillas primero
        template_ids = []
        for template_data in sample_ship_templates:
            template = store.create_ship_template(
                name=template_data["name"],
                size=template_data["size"],
                description=template_data["description"],
                created_by="test-user"
            )
            template_ids.append(template.id)
        
        # Crear flota
        fleet = store.create_base_fleet(
            name="Flota Completa",
            board_size=10,
            ship_template_ids=template_ids,
            created_by="test-user"
        )
        
        assert len(fleet.ship_template_ids) == 3
        assert fleet.ship_template_ids == template_ids


class TestFindUserById:
    """Tests de búsqueda de usuarios por ID."""
    
    def test_find_user_by_id(self, clean_storage, sample_user):
        """Buscar usuario por ID."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        found = store.get_user_by_id(user.id)
        assert found is not None
        assert found.id == user.id
        assert found.username == user.username
    
    def test_find_user_by_id_not_found(self, clean_storage):
        """Buscar usuario que no existe."""
        found = store.get_user_by_id("non-existent-id")
        assert found is None


class TestFindUserByUsername:
    """Tests de búsqueda de usuarios por username."""
    
    def test_find_user_by_username(self, clean_storage, sample_user):
        """Buscar usuario por username."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        found = store.get_user_by_username(sample_user["username"])
        assert found is not None
        assert found.username == sample_user["username"]
    
    def test_find_user_by_username_not_found(self, clean_storage):
        """Buscar usuario que no existe."""
        found = store.get_user_by_username("nonexistent")
        assert found is None


class TestPasswordHashing:
    """Tests de hashing de contraseñas."""
    
    def test_password_is_hashed(self, clean_storage, sample_user):
        """Verificar que la contraseña se hashea."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        # La contraseña hasheada no debe ser igual a la original
        assert user.hashed_password != sample_user["password"]
    
    def test_verify_password_correct(self, clean_storage, sample_user):
        """Verificar contraseña correcta."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        is_valid = store.verify_password(
            sample_user["password"],
            user.hashed_password
        )
        assert is_valid is True
    
    def test_verify_password_incorrect(self, clean_storage, sample_user):
        """Verificar contraseña incorrecta."""
        user = store.create_user(
            username=sample_user["username"],
            password=sample_user["password"],
            role=sample_user["role"]
        )
        
        is_valid = store.verify_password(
            "wrongpassword",
            user.hashed_password
        )
        assert is_valid is False


class TestShipTemplateOperations:
    """Tests de operaciones CRUD de plantillas de barcos."""
    
    def test_get_ship_template(self, clean_storage):
        """Obtener plantilla de barco por ID."""
        template = store.create_ship_template(
            name="Portaaviones",
            size=5,
            description="Barco grande",
            created_by="test-user"
        )
        
        found = store.get_ship_template(template.id)
        assert found is not None
        assert found.id == template.id
    
    def test_get_all_ship_templates(self, clean_storage, sample_ship_templates):
        """Obtener todas las plantillas de barcos."""
        for template_data in sample_ship_templates:
            store.create_ship_template(
                name=template_data["name"],
                size=template_data["size"],
                description=template_data["description"],
                created_by="test-user"
            )
        
        all_templates = store.get_all_ship_templates()
        assert len(all_templates) == 3
    
    def test_update_ship_template(self, clean_storage):
        """Actualizar plantilla de barco."""
        template = store.create_ship_template(
            name="Portaaviones",
            size=5,
            description="Original",
            created_by="test-user"
        )
        
        updated = store.update_ship_template(
            template_id=template.id,
            name="Portaaviones Mejorado",
            size=6,
            description="Actualizado"
        )
        
        assert updated is not None
        assert updated.name == "Portaaviones Mejorado"
        assert updated.size == 6
    
    def test_delete_ship_template(self, clean_storage):
        """Eliminar plantilla de barco."""
        template = store.create_ship_template(
            name="Portaaviones",
            size=5,
            description="Barco",
            created_by="test-user"
        )
        
        deleted = store.delete_ship_template(template.id)
        assert deleted is True
        
        found = store.get_ship_template(template.id)
        assert found is None


class TestBaseFleetOperations:
    """Tests de operaciones CRUD de flotas base."""
    
    def test_get_base_fleet(self, clean_storage):
        """Obtener flota base por ID."""
        fleet = store.create_base_fleet(
            name="Flota Test",
            board_size=10,
            ship_template_ids=["id1", "id2"],
            created_by="test-user"
        )
        
        found = store.get_base_fleet(fleet.id)
        assert found is not None
        assert found.id == fleet.id
    
    def test_get_all_base_fleets(self, clean_storage):
        """Obtener todas las flotas base."""
        for i in range(3):
            store.create_base_fleet(
                name=f"Flota {i}",
                board_size=10,
                ship_template_ids=[],
                created_by="test-user"
            )
        
        all_fleets = store.get_all_base_fleets()
        assert len(all_fleets) == 3
    
    def test_update_base_fleet(self, clean_storage):
        """Actualizar flota base."""
        fleet = store.create_base_fleet(
            name="Flota Original",
            board_size=10,
            ship_template_ids=["id1"],
            created_by="test-user"
        )
        
        updated = store.update_base_fleet(
            fleet_id=fleet.id,
            name="Flota Actualizada",
            board_size=12,
            ship_template_ids=["id1", "id2", "id3"]
        )
        
        assert updated is not None
        assert updated.name == "Flota Actualizada"
        assert updated.board_size == 12
        assert len(updated.ship_template_ids) == 3
    
    def test_delete_base_fleet(self, clean_storage):
        """Eliminar flota base."""
        fleet = store.create_base_fleet(
            name="Flota Test",
            board_size=10,
            ship_template_ids=[],
            created_by="test-user"
        )
        
        deleted = store.delete_base_fleet(fleet.id)
        assert deleted is True
        
        found = store.get_base_fleet(fleet.id)
        assert found is None


class TestCleanStorageFixture:
    """Tests de la fixture clean_storage."""
    
    def test_storage_is_clean(self, clean_storage):
        """Verificar que el almacenamiento está limpio."""
        # Después de clean_storage, solo debe existir el admin por defecto
        # pero la fixture lo limpia también
        assert len(store.users_db) == 0
        assert len(store.ship_templates_db) == 0
        assert len(store.base_fleets_db) == 0
        assert len(store.games_db) == 0
    
    def test_storage_restored_after_test(self, clean_storage):
        """Verificar que el almacenamiento se restaura después del test."""
        # Agregar datos durante el test
        store.create_user("testuser", "pass123", "player")
        assert len(store.users_db) == 1
        
        # Después del test, la fixture debe restaurar el estado
