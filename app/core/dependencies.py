"""
Dependencias reutilizables de FastAPI.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated

from app.core.security import decode_access_token
from app.storage.in_memory_store import get_user_by_id
from app.storage.data_models import User


# Esquema de seguridad Bearer
security = HTTPBearer()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> User:
    """
    Obtiene el usuario actual desde el token JWT.
    
    Args:
        credentials: Credenciales HTTP Bearer
    
    Returns:
        Usuario autenticado
    
    Raises:
        HTTPException: Si el token es inválido o el usuario no existe
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Verifica que el usuario actual sea administrador.
    
    Args:
        current_user: Usuario actual
    
    Returns:
        Usuario administrador
    
    Raises:
        HTTPException: Si el usuario no es administrador
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador"
        )
    
    return current_user


def get_current_player(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Verifica que el usuario actual sea jugador.
    
    Args:
        current_user: Usuario actual
    
    Returns:
        Usuario jugador
    
    Raises:
        HTTPException: Si el usuario no es jugador
    """
    if current_user.role != "player":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los jugadores pueden realizar esta acción"
        )
    
    return current_user
