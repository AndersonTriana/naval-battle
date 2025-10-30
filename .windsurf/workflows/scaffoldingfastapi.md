---
trigger: manual
---

---
description: Scaffolding FastAPI project (FastAPI + Pydantic)
auto_execution_mode: 1
---

# Pasos para crear el scaffolding de un proyecto FastAPI

- Nota: Este workflow crea la estructura base y una aplicación FastAPI mínima ejecutable con un endpoint GET "/hello" que responde "Hello world".
- Requisitos: macOS con `python3` y `pip` disponibles.

## 1) Solicitar nombre del API

- Pide al usuario el nombre del API cumpliendo las buenas prácticas para nombre de paquete Python:
  - Solo minúsculas, números y `_`.
  - Debe iniciar con una letra.
  - Ejemplos válidos: `order_api`, `customer_service`, `inventory`.
  - Regex sugerida: `^[a-z][a-z0-9_]*$`

- Guarda el valor en una variable `API_NAME`.
  - Además, persiste el valor en el archivo `.fastapi_scaffold.env` para que los siguientes pasos lo puedan usar.

0. Capturar y validar nombre del API (interactivo)

Nota: Este paso es interactivo y puede bloquearse si se auto-ejecuta. Si el workflow no avanza, puedes saltarte este bloque y establecer el nombre manualmente con:

```bash
printf "API_NAME=%s\n" "mi_api_name" > .fastapi_scaffold.env
```

```bash
printf '\033[1;35m[🧩] Validando y capturando API_NAME...\033[0m\n'
# Reusar valor de .fastapi_scaffold.env si existe y es válido
if [ -f .fastapi_scaffold.env ]; then
  set -a
  . .fastapi_scaffold.env
  set +a
  if [[ "${API_NAME:-}" =~ ^[a-z][a-z0-9_]*$ ]]; then
    echo "Using API_NAME from .fastapi_scaffold.env: $API_NAME"
  else
    unset API_NAME
  fi
fi

# Si API_NAME ya viene en el entorno, validarlo y persistirlo
if [ -n "${API_NAME:-}" ] && [[ "$API_NAME" =~ ^[a-z][a-z0-9_]*$ ]]; then
  printf "API_NAME=%s\n" "$API_NAME" > .fastapi_scaffold.env
  echo "Using provided API_NAME: $API_NAME"
else
  while true; do
    read -rp "Enter API name (snake_case, start with letter): " INPUT
    if [[ "$INPUT" =~ ^[a-z][a-z0-9_]*$ ]]; then
      export API_NAME="$INPUT"
      echo "API_NAME set to: $API_NAME"
      printf "API_NAME=%s\n" "$API_NAME" > .fastapi_scaffold.env
      break
    else
      echo "Invalid name. Use snake_case, start with letter."
    fi
  done
fi
```

## 2) Crear estructura de carpetas base

- Estructura recomendada (carpetas en inglés y dentro de `src/`):

```
${API_NAME}/
├── src/
│   └── ${API_NAME}/
│       ├── __init__.py
│       ├── main.py
│       ├── controller/
│       │   └── __init__.py
│       ├── model/
│       │   └── __init__.py
│       ├── service/
│       │   └── __init__.py
│       ├── config/
│       │   └── __init__.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── v1/
│       │       ├── __init__.py
│       │       └── endpoints/
│       │           └── __init__.py
│       └── schemas/
│           └── __init__.py
├── tests/
│   └── __init__.py
├── README.md
├── pyproject.toml
├── .pre-commit-config.yaml
└── requirements.txt
```

// turbo
1. Crear carpetas del proyecto

```bash
printf '\033[1;34m[📁] Creando estructura de carpetas...\033[0m\n'
source .fastapi_scaffold.env
mkdir -p "${API_NAME}/src/${API_NAME}/controller" \
         "${API_NAME}/src/${API_NAME}/model" \
         "${API_NAME}/src/${API_NAME}/service" \
         "${API_NAME}/src/${API_NAME}/config" \
         "${API_NAME}/src/${API_NAME}/api" \
         "${API_NAME}/src/${API_NAME}/api/v1" \
         "${API_NAME}/src/${API_NAME}/api/v1/endpoints" \
         "${API_NAME}/src/${API_NAME}/schemas" \
         "${API_NAME}/tests"
```

// turbo
2. Crear archivos `__init__.py` para convertir en paquetes Python

```bash
printf '\033[1;34m[📦] Creando archivos __init__.py...\033[0m\n'
source .fastapi_scaffold.env
touch "${API_NAME}/src/${API_NAME}/__init__.py" \
      "${API_NAME}/src/${API_NAME}/controller/__init__.py" \
      "${API_NAME}/src/${API_NAME}/model/__init__.py" \
      "${API_NAME}/src/${API_NAME}/service/__init__.py" \
      "${API_NAME}/src/${API_NAME}/config/__init__.py" \
      "${API_NAME}/src/${API_NAME}/api/__init__.py" \
      "${API_NAME}/src/${API_NAME}/api/v1/__init__.py" \
      "${API_NAME}/src/${API_NAME}/api/v1/endpoints/__init__.py" \
      "${API_NAME}/src/${API_NAME}/schemas/__init__.py" \
      "${API_NAME}/tests/__init__.py"
```

// turbo
3. Crear archivo `main.py` con endpoint Hello World

```bash
printf '\033[1;36m[🧪] Generando main.py (GET /hello)...\033[0m\n'
source .fastapi_scaffold.env
cat > "${API_NAME}/src/${API_NAME}/main.py" << 'EOF'
from fastapi import FastAPI

app = FastAPI()


@app.get("/hello")
def hello_world():
    return {"message": "Hello world"}
EOF
```

## 3) Crear requirements.txt con librerías necesarias

- Incluye FastAPI, Pydantic y Uvicorn (servidor ASGI) en `requirements.txt`.

// turbo
3. Generar `requirements.txt`

```bash
printf '\033[1;33m[📦] Generando requirements.txt...\033[0m\n'
source .fastapi_scaffold.env
cat > "${API_NAME}/requirements.txt" << 'EOF'
fastapi==0.111.0
pydantic==2.8.0
uvicorn[standard]==0.30.0
EOF
```

## 4) Crear archivos de soporte del proyecto

- Se generarán archivos auxiliares en la raíz del proyecto: `README.md`, `pyproject.toml` y `.pre-commit-config.yaml`.

// turbo
4.a Generar `README.md`

```bash
printf '\033[1;33m[📝] Generando README.md...\033[0m\n'
source .fastapi_scaffold.env
cat > "${API_NAME}/README.md" << EOF
# ${API_NAME}

Proyecto base con FastAPI + Pydantic.

## Requisitos
- Python 3.12+

## Configuración rápida
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Estructura
Ver árbol de directorios generado por el workflow.

## Desarrollo
- Formateo y chequeos: pre-commit (Black, isort, Flake8, MyPy)

## Ejecución
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn ${API_NAME}.main:app --reload --app-dir "src"
```

## Endpoints
- GET `/hello` → `{"message": "Hello world"}`

EOF
```

// turbo
4.b Generar `pyproject.toml`

```bash
printf '\033[1;33m[⚙️] Generando pyproject.toml...\033[0m\n'
source .fastapi_scaffold.env
cat > "${API_NAME}/pyproject.toml" << EOF
[project]
name = "${API_NAME}"
version = "0.1.0"
description = "FastAPI service: ${API_NAME}"
readme = "README.md"
requires-python = ">=3.12"
authors = [{ name = "Your Name", email = "you@example.com" }]

[tool.black]
line-length = 88
target-version = ["py312"]

[tool.isort]
profile = "black"
line_length = 88

[tool.flake8]
max-line-length = 88
extend-ignore = ["E203", "W503"]

[tool.mypy]
python_version = "3.12"
warn_unused_configs = true
ignore_missing_imports = true
strict = false
EOF
```

// turbo
4.c Generar `.pre-commit-config.yaml`

```bash
printf '\033[1;33m[🧹] Generando .pre-commit-config.yaml...\033[0m\n'
source .fastapi_scaffold.env
cat > "${API_NAME}/.pre-commit-config.yaml" << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace

  - repo: https://github.com/psf/black
    rev: 24.8.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort

  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.10.0
    hooks:
      - id: mypy
        additional_dependencies: ["types-requests"]
EOF
```

// turbo
4.d Instalar y activar pre-commit (opcional)

```bash
printf '\033[1;33m[🧹] Instalando y activando pre-commit (opcional)...\033[0m\n'
source .fastapi_scaffold.env && pip install pre-commit
(cd "${API_NAME}" && pre-commit install)
```

## 5) Ejecutar la API localmente

- Nota: Se asume que `API_NAME` está definido en `.fastapi_scaffold.env`.

// turbo
5.a Instalar dependencias en un entorno virtual (si no lo hiciste antes)

```bash
printf '\033[1;32m[⬇️] Creando venv e instalando dependencias...\033[0m\n'
source .fastapi_scaffold.env
python3 -m venv "${API_NAME}/.venv"
source "${API_NAME}/.venv/bin/activate"
pip install -r "${API_NAME}/requirements.txt"
```

// turbo
5.b Ejecutar el servidor de desarrollo

```bash
printf '\033[1;32m[🚀] Iniciando servidor de desarrollo...\033[0m\n'
source .fastapi_scaffold.env
uvicorn ${API_NAME}.main:app --host 127.0.0.1 --port 8000 --reload --app-dir "${API_NAME}/src"
```

- Probar el endpoint Hello World:

```bash
curl -s http://127.0.0.1:8000/hello
```

## 6) Recomendaciones adicionales (opcional)

- Considera usar un entorno virtual por proyecto:

```bash
python3 -m venv "${API_NAME}/.venv"
source "${API_NAME}/.venv/bin/activate"
pip install -r "${API_NAME}/requirements.txt"
```

- Mantén los nombres siempre en inglés y en `snake_case` para paquetes Python.
- Más adelante puedes añadir módulos como `config/`, `api/`, `schemas/` según crezca el proyecto.

## 7) Resultado esperado

- Al finalizar, tendrás la estructura base, un `requirements.txt` listo para instalar dependencias y una aplicación FastAPI mínima en `src/${API_NAME}/main.py` que puedes ejecutar con Uvicorn. La API expone un endpoint GET `/hello` que responde `{"message": "Hello world"}`.

## 8) Configurar Run and Debug (launch.json)

// turbo
8.a Generar `.vscode/launch.json` para ejecutar la API desde el depurador

```bash
printf '\033[1;36m[🪄] Generando .vscode/launch.json...\033[0m\n'
source .fastapi_scaffold.env
mkdir -p ".vscode"
cat > ".vscode/launch.json" << 'EOF'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI (Uvicorn) - ${env:API_NAME}",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "${env:API_NAME}.main:app",
        "--reload",
        "--host", "127.0.0.1",
        "--port", "8000",
        "--app-dir", "${env:API_NAME}/src"
      ],
      "justMyCode": true,
      "console": "integratedTerminal",
      "envFile": "${workspaceFolder}/.fastapi_scaffold.env",
      "cwd": "${workspaceFolder}"
    }
  ]
}
EOF
```