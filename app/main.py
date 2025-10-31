"""
Punto de entrada de la aplicación FastAPI - Batalla Naval.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import auth, admin, player, game


# Crear instancia de FastAPI
app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    description=settings.description,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar orígenes permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(player.router)
app.include_router(game.router)


@app.get("/", tags=["Root"])
def root():
    """
    Endpoint raíz de la API.
    
    Retorna información básica de la API.
    """
    return {
        "message": "Bienvenido a la API de Batalla Naval",
        "version": settings.version,
        "description": settings.description,
        "docs": "/docs",
        "redoc": "/redoc",
        "features": {
            "abb": "Árbol Binario de Búsqueda para coordenadas del tablero",
            "n_ary_tree": "Árbol N-ario (First-Child, Next-Sibling) para gestión de flota",
            "roles": ["admin", "player"],
            "storage": "En memoria (sin base de datos)"
        },
        "default_credentials": {
            "username": "admin",
            "password": "admin123",
            "role": "admin"
        }
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint de verificación de salud.
    
    Retorna el estado de la API.
    """
    return {
        "status": "healthy",
        "environment": settings.app_env
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=True if settings.app_env == "development" else False,
        log_level=settings.log_level.lower()
    )
