---
trigger: manual
---

# Regla para Programador Experto en Python 3.12+, POO, Patrones de Diseño y FastAPI

## 1. Scaffolding (Estructura de Proyecto Recomendada)

```
project_name/
│
├── app/
│   ├── api/              # Rutas y controladores FastAPI
│   ├── core/             # Configuración, utilidades y lógica de negocio central
│   ├── models/           # Modelos Pydantic y entidades de dominio
│   ├── db/               # Conexión y operaciones con la base de datos
│   ├── services/         # Lógica de negocio y servicios desacoplados
│   ├── schemas/          # Esquemas de entrada/salida (DTOs)
│   ├── dependencies/     # Dependencias reutilizables de FastAPI
│   └── main.py           # Punto de entrada de la aplicación FastAPI
│
├── tests/                # Pruebas unitarias y de integración
│
├── alembic/              # Migraciones de base de datos (opcional)
│
├── requirements.txt      # Dependencias del proyecto
├── pyproject.toml        # Configuración de herramientas y dependencias modernas
├── .env                  # Variables de entorno (nunca subir a VCS)
├── .gitignore
└── README.md
```

---

## 2. Buenas Prácticas

### General
- Usa tipado estático y type hints en todo el código.
- Sigue PEP8 y PEP257 (docstrings).
- Aplica principios SOLID y DRY.
- Documenta exhaustivamente con docstrings y comentarios relevantes.
- Utiliza virtual environments y gestiona dependencias con `requirements.txt` o `pyproject.toml`.

### POO y Patrones de Diseño
- Prefiere composición sobre herencia.
- Utiliza patrones como Factory, Repository, Service, Singleton, Dependency Injection, etc., según corresponda.
- Mantén las clases pequeñas, enfocadas y cohesionadas.
- Separa claramente la lógica de negocio de la lógica de infraestructura.

### FastAPI
- Define rutas en módulos separados y usa routers (`APIRouter`).
- Utiliza modelos Pydantic para validación y serialización de datos.
- Maneja errores con excepciones personalizadas y handlers globales.
- Usa dependencias (`Depends`) para inyección de lógica transversal (auth, db, etc).
- Configura CORS, seguridad y middlewares de forma centralizada.
- Documenta los endpoints con descripciones y ejemplos (OpenAPI).

### Pruebas
- Escribe pruebas unitarias y de integración usando `pytest`.
- Usa fixtures para datos y dependencias comunes.
- Aplica mocks para servicios externos.
- Asegura una cobertura alta de código crítico.

### DevOps y Entorno
- Usa archivos `.env` para configuración sensible.
- Configura linters (flake8, black) y formateadores automáticos.
- Usa herramientas de análisis estático (mypy, pylint).
- Automatiza pruebas y despliegue continuo (CI/CD).
