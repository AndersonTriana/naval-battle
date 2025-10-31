# 🚢 Batalla Naval API

API REST para juego de Batalla Naval implementada con **FastAPI**, **Árbol Binario de Búsqueda (ABB)** y **Árbol N-ario (First-Child, Next-Sibling)**.

## 📋 Características

### Estructuras de Datos

- **ABB (Árbol Binario de Búsqueda)**: Para almacenar y buscar coordenadas del tablero
  - Codificación: `FilaNumérica × 10 + Columna` (A1 → 11, J10 → 100)
  - Balanceo automático usando algoritmo del medio recursivo
  - Búsqueda O(log n) para verificar impactos

- **Árbol N-ario (First-Child, Next-Sibling)**: Para gestión de flota
  - Estructura: Jugador → Barcos → Segmentos
  - Cada nodo tiene referencia a primer hijo y siguiente hermano

### Roles del Sistema

#### 👨‍💼 ADMINISTRADOR
- CRUD completo de tipos de barcos (plantillas)
- Crear y modificar "Flota Base"
- Configurar tamaño del tablero (NxN)

#### 🎮 JUGADOR
- Registrarse/Login
- Crear nueva partida
- Colocar barcos en el tablero
- Realizar disparos
- Consultar estado de flota
- Ver historial de partidas

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.12+
- pip

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

El archivo `.env` ya está configurado con valores por defecto:

```env
APP_ENV=development
APP_HOST=0.0.0.0
APP_PORT=8000
LOG_LEVEL=INFO
SECRET_KEY=batalla-naval-secret-key-change-in-production-12345678
```

### 3. Ejecutar la API

```bash
python -m app.main
```

O usando uvicorn directamente:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acceder a la Documentación

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root**: http://localhost:8000/

## 📁 Estructura del Proyecto

```
batalla-naval/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Punto de entrada FastAPI
│   ├── models/                 # Modelos Pydantic
│   │   ├── user.py
│   │   ├── ship.py
│   │   ├── game.py
│   │   └── board.py
│   ├── api/                    # Routers/Endpoints
│   │   ├── auth.py
│   │   ├── admin.py
│   │   └── player.py
│   ├── core/                   # Configuración y utilidades
│   │   ├── config.py
│   │   ├── security.py
│   │   └── dependencies.py
│   ├── services/               # Lógica de negocio
│   │   ├── board_service.py
│   │   ├── game_service.py
│   │   └── ship_service.py
│   ├── structures/             # Estructuras de datos
│   │   ├── binary_search_tree.py  # ABB (movido de api_abb)
│   │   ├── abb_node.py            # Nodo del ABB
│   │   ├── n_ary_tree.py          # Árbol N-ario
│   │   └── coordinate_utils.py    # Utilidades de coordenadas
│   └── storage/                # Almacenamiento en memoria
│       ├── in_memory_store.py
│       └── data_models.py
├── requirements.txt
├── .env
└── README.md
```

## 🔐 Autenticación

La API usa **JWT (JSON Web Tokens)** para autenticación.

### Usuario Administrador por Defecto

```json
{
  "username": "admin",
  "password": "admin123"
}
```

### Flujo de Autenticación

1. **Registrarse** (opcional): `POST /auth/register`
2. **Login**: `POST /auth/login` → Retorna token JWT
3. **Usar token**: Agregar header `Authorization: Bearer <token>` en todas las peticiones

## 📚 Endpoints Principales

### Autenticación

- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Iniciar sesión

### Administrador

#### Plantillas de Barcos
- `POST /admin/ship-templates` - Crear plantilla
- `GET /admin/ship-templates` - Listar plantillas
- `GET /admin/ship-templates/{id}` - Obtener plantilla
- `PUT /admin/ship-templates/{id}` - Actualizar plantilla
- `DELETE /admin/ship-templates/{id}` - Eliminar plantilla

#### Flotas Base
- `POST /admin/base-fleets` - Crear flota base
- `GET /admin/base-fleets` - Listar flotas
- `GET /admin/base-fleets/{id}` - Obtener flota
- `PUT /admin/base-fleets/{id}` - Actualizar flota
- `DELETE /admin/base-fleets/{id}` - Eliminar flota

### Jugador

#### Flotas (Solo lectura)
- `GET /player/base-fleets` - Listar flotas disponibles
- `GET /player/base-fleets/{id}` - Ver detalles de flota

#### Partidas
- `POST /player/games` - Crear nueva partida
- `GET /player/games` - Listar mis partidas
- `GET /player/games/{id}` - Ver detalles de partida
- `POST /player/games/{id}/place-ship` - Colocar barco
- `POST /player/games/{id}/start` - Iniciar partida
- `POST /player/games/{id}/shoot` - Realizar disparo

## 🎮 Flujo de Juego

### 1. Configuración Inicial (Admin)

```bash
# 1. Login como admin
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. Crear plantillas de barcos
curl -X POST http://localhost:8000/admin/ship-templates \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Portaaviones","size":5,"description":"Barco grande"}'

# 3. Crear flota base
curl -X POST http://localhost:8000/admin/base-fleets \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Flota Clásica","board_size":10,"ship_template_ids":["<id1>","<id2>"]}'
```

### 2. Jugar (Jugador)

```bash
# 1. Registrarse
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"jugador1","password":"pass123","role":"player"}'

# 2. Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"jugador1","password":"pass123"}'

# 3. Crear partida
curl -X POST http://localhost:8000/player/games \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"base_fleet_id":"<fleet_id>"}'

# 4. Colocar barcos
curl -X POST http://localhost:8000/player/games/<game_id>/place-ship \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"ship_template_id":"<ship_id>","start_coordinate":"A1","orientation":"horizontal"}'

# 5. Iniciar partida
curl -X POST http://localhost:8000/player/games/<game_id>/start \
  -H "Authorization: Bearer <token>"

# 6. Disparar
curl -X POST http://localhost:8000/player/games/<game_id>/shoot \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"coordinate":"B3"}'
```

## 🧪 Ejemplos de Uso

### Crear Plantilla de Barco (Admin)

```json
POST /admin/ship-templates
{
  "name": "Portaaviones",
  "size": 5,
  "description": "El barco más grande"
}
```

### Crear Flota Base (Admin)

```json
POST /admin/base-fleets
{
  "name": "Flota Clásica",
  "board_size": 10,
  "ship_template_ids": [
    "uuid-portaaviones",
    "uuid-acorazado",
    "uuid-crucero"
  ]
}
```

### Colocar Barco (Jugador)

```json
POST /player/games/{game_id}/place-ship
{
  "ship_template_id": "uuid-portaaviones",
  "start_coordinate": "A1",
  "orientation": "horizontal"
}
```

### Realizar Disparo (Jugador)

```json
POST /player/games/{game_id}/shoot
{
  "coordinate": "B3"
}

// Respuesta
{
  "coordinate": "B3",
  "coordinate_code": 23,
  "result": "hit",
  "ship_hit": "Portaaviones",
  "ship_sunk": false,
  "game_finished": false
}
```

## 🔧 Tecnologías Utilizadas

- **FastAPI** - Framework web moderno y rápido
- **Pydantic** - Validación de datos
- **Passlib** - Hashing de contraseñas
- **Python-Jose** - JWT tokens
- **Uvicorn** - Servidor ASGI

## 📊 Algoritmos Implementados

### Balanceo de ABB

```python
def balance_array_for_bst(arr: List[int]) -> List[int]:
    """
    Reordena un array usando el algoritmo del medio recursivo.
    
    Ejemplo: [1,2,3,4,5,6,7] → [4,2,1,3,6,5,7]
    
    Resultado: ABB balanceado con altura log₂(n)
    """
```

### Codificación de Coordenadas

```python
def coordinate_to_code(coordinate: str) -> int:
    """
    A1 → 11
    B3 → 23
    J10 → 100
    
    Fórmula: FilaNumérica × 10 + Columna
    """
```

## 🎯 Características Técnicas

- ✅ Sin base de datos (todo en memoria)
- ✅ Autenticación JWT
- ✅ Validación con Pydantic
- ✅ Documentación automática (Swagger/ReDoc)
- ✅ CORS configurado
- ✅ Tipado estático completo
- ✅ Arquitectura limpia (separación de capas)
- ✅ Principios SOLID

## 📝 Notas Importantes

1. **Almacenamiento en Memoria**: Los datos se pierden al reiniciar el servidor
2. **Usuario Admin**: Se crea automáticamente al iniciar (admin/admin123)
3. **Balanceo del ABB**: Se garantiza mediante el algoritmo del medio recursivo
4. **Árbol N-ario**: Implementación First-Child, Next-Sibling para eficiencia

## 🐛 Troubleshooting

### Error: ModuleNotFoundError

```bash
# Asegúrate de estar en el directorio raíz del proyecto
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Error: Port already in use

```bash
# Cambiar puerto en .env o usar otro puerto
uvicorn app.main:app --port 8001
```

## 📄 Licencia

Este proyecto es para fines educativos.

---

**Desarrollado con ❤️ usando FastAPI, ABB y Árbol N-ario**
