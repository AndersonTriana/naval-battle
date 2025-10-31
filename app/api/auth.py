"""
Endpoints de autenticación.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Annotated

from app.models.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.storage.data_models import User
from app.storage.in_memory_store import (
    create_user,
    get_user_by_username,
    verify_password
)


router = APIRouter(prefix="/api/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """
    Registra un nuevo usuario en el sistema.
    
    - **username**: Nombre de usuario único (3-50 caracteres)
    - **password**: Contraseña (mínimo 6 caracteres)
    - **role**: Rol del usuario (admin o player, por defecto player)
    """
    # Verificar si el usuario ya existe
    existing_user = get_user_by_username(user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está en uso"
        )
    
    # Crear usuario
    user = create_user(
        username=user_data.username,
        password=user_data.password,
        role=user_data.role.value
    )
    
    return UserResponse(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at
    )


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin):
    """
    Inicia sesión y obtiene un token de acceso.
    
    - **username**: Nombre de usuario
    - **password**: Contraseña
    
    Retorna un token JWT válido por 24 horas.
    """
    # Buscar usuario
    user = get_user_by_username(credentials.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verificar contraseña
    if not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token
    access_token = create_access_token(data={"sub": user.id, "role": user.role})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            username=user.username,
            role=user.role,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Obtiene información del usuario autenticado.
    
    **Requiere autenticación.**
    
    Retorna los datos del usuario actual basado en el token JWT.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        role=current_user.role,
        created_at=current_user.created_at
    )
