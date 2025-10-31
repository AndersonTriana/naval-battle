"""
Almacenamiento en memoria para todos los datos del sistema.
"""
from typing import Dict
from datetime import datetime
import uuid
import hashlib

from app.storage.data_models import User, ShipTemplate, BaseFleet, Game


# Funciones para hashing de contraseñas
def hash_password(password: str) -> str:
    """Hash de contraseña usando SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return hash_password(plain_password) == hashed_password


# Diccionarios globales para almacenar datos
users_db: Dict[str, User] = {}
ship_templates_db: Dict[str, ShipTemplate] = {}
base_fleets_db: Dict[str, BaseFleet] = {}
games_db: Dict[str, Game] = {}

# Índices secundarios para búsquedas rápidas
username_to_user_id: Dict[str, str] = {}
player_games: Dict[str, list] = {}  # player_id -> [game_ids]


def initialize_default_admin():
    """Inicializa el usuario administrador por defecto."""
    admin_id = str(uuid.uuid4())
    admin_password = "admin123"
    
    admin_user = User(
        id=admin_id,
        username="admin",
        hashed_password=hash_password(admin_password),
        role="admin",
        created_at=datetime.now()
    )
    
    users_db[admin_id] = admin_user
    username_to_user_id["admin"] = admin_id
    
    print(f"✅ Usuario admin creado - username: admin, password: {admin_password}")


# Inicializar admin al cargar el módulo
initialize_default_admin()


# Funciones auxiliares para gestión de usuarios
def get_user_by_username(username: str) -> User | None:
    """Obtiene un usuario por su nombre de usuario."""
    user_id = username_to_user_id.get(username)
    if user_id:
        return users_db.get(user_id)
    return None


def get_user_by_id(user_id: str) -> User | None:
    """Obtiene un usuario por su ID."""
    return users_db.get(user_id)


def create_user(username: str, password: str, role: str) -> User:
    """Crea un nuevo usuario."""
    user_id = str(uuid.uuid4())
    
    user = User(
        id=user_id,
        username=username,
        hashed_password=hash_password(password),
        role=role,
        created_at=datetime.now()
    )
    
    users_db[user_id] = user
    username_to_user_id[username] = user_id
    
    return user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica una contraseña contra su hash."""
    return verify_password_hash(plain_password, hashed_password)


# Funciones auxiliares para plantillas de barcos
def create_ship_template(name: str, size: int, description: str | None, 
                        created_by: str) -> ShipTemplate:
    """Crea una nueva plantilla de barco."""
    template_id = str(uuid.uuid4())
    
    template = ShipTemplate(
        id=template_id,
        name=name,
        size=size,
        description=description,
        created_by=created_by,
        created_at=datetime.now()
    )
    
    ship_templates_db[template_id] = template
    return template


def get_ship_template(template_id: str) -> ShipTemplate | None:
    """Obtiene una plantilla de barco por su ID."""
    return ship_templates_db.get(template_id)


def get_all_ship_templates() -> list[ShipTemplate]:
    """Obtiene todas las plantillas de barcos."""
    return list(ship_templates_db.values())


def update_ship_template(template_id: str, name: str | None = None, 
                        size: int | None = None, 
                        description: str | None = None) -> ShipTemplate | None:
    """Actualiza una plantilla de barco."""
    template = ship_templates_db.get(template_id)
    if not template:
        return None
    
    if name is not None:
        template.name = name
    if size is not None:
        template.size = size
    if description is not None:
        template.description = description
    
    return template


def delete_ship_template(template_id: str) -> bool:
    """Elimina una plantilla de barco."""
    if template_id in ship_templates_db:
        del ship_templates_db[template_id]
        return True
    return False


# Funciones auxiliares para flotas base
def create_base_fleet(name: str, board_size: int, ship_template_ids: list[str], 
                     created_by: str) -> BaseFleet:
    """Crea una nueva flota base."""
    fleet_id = str(uuid.uuid4())
    
    fleet = BaseFleet(
        id=fleet_id,
        name=name,
        board_size=board_size,
        ship_template_ids=ship_template_ids,
        created_by=created_by,
        created_at=datetime.now()
    )
    
    base_fleets_db[fleet_id] = fleet
    return fleet


def get_base_fleet(fleet_id: str) -> BaseFleet | None:
    """Obtiene una flota base por su ID."""
    return base_fleets_db.get(fleet_id)


def get_all_base_fleets() -> list[BaseFleet]:
    """Obtiene todas las flotas base."""
    return list(base_fleets_db.values())


def update_base_fleet(fleet_id: str, name: str | None = None, 
                     board_size: int | None = None, 
                     ship_template_ids: list[str] | None = None) -> BaseFleet | None:
    """Actualiza una flota base."""
    fleet = base_fleets_db.get(fleet_id)
    if not fleet:
        return None
    
    if name is not None:
        fleet.name = name
    if board_size is not None:
        fleet.board_size = board_size
    if ship_template_ids is not None:
        fleet.ship_template_ids = ship_template_ids
    
    return fleet


def delete_base_fleet(fleet_id: str) -> bool:
    """Elimina una flota base."""
    if fleet_id in base_fleets_db:
        del base_fleets_db[fleet_id]
        return True
    return False


# Funciones auxiliares para partidas
def create_game(player_id: str, base_fleet_id: str, board_size: int, 
               abb_tree, fleet_tree) -> Game:
    """Crea una nueva partida."""
    game_id = str(uuid.uuid4())
    
    game = Game(
        id=game_id,
        player_id=player_id,
        base_fleet_id=base_fleet_id,
        board_size=board_size,
        status="setup",
        abb_tree=abb_tree,
        fleet_tree=fleet_tree,
        created_at=datetime.now()
    )
    
    games_db[game_id] = game
    
    # Actualizar índice de partidas por jugador
    if player_id not in player_games:
        player_games[player_id] = []
    player_games[player_id].append(game_id)
    
    return game


def get_game(game_id: str) -> Game | None:
    """Obtiene una partida por su ID."""
    return games_db.get(game_id)


def get_player_games(player_id: str) -> list[Game]:
    """Obtiene todas las partidas de un jugador."""
    game_ids = player_games.get(player_id, [])
    return [games_db[gid] for gid in game_ids if gid in games_db]


def get_all_games() -> list[Game]:
    """Obtiene todas las partidas."""
    return list(games_db.values())


def update_game_status(game_id: str, status: str) -> Game | None:
    """Actualiza el estado de una partida."""
    game = games_db.get(game_id)
    if not game:
        return None
    
    game.status = status
    if status == "finished":
        game.finished_at = datetime.now()
    
    return game
