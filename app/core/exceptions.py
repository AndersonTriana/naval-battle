"""
Excepciones personalizadas del juego Batalla Naval.
"""


class BattleshipException(Exception):
    """Excepción base del juego."""
    pass


class CoordinateInvalidError(BattleshipException):
    """Coordenada inválida."""
    pass


class CoordinateOccupiedError(BattleshipException):
    """Coordenada ya ocupada."""
    pass


class ShipOutOfBoundsError(BattleshipException):
    """Barco se sale del tablero."""
    pass


class ShipAlreadyPlacedError(BattleshipException):
    """Barco ya fue colocado."""
    pass


class CoordinateAlreadyShotError(BattleshipException):
    """Coordenada ya fue disparada."""
    pass


class GameNotInProgressError(BattleshipException):
    """Juego no está en progreso."""
    pass


class UnauthorizedError(BattleshipException):
    """Usuario no autorizado."""
    pass
