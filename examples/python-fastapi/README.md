# Ejemplo: Python FastAPI con QuinotoSpec

Proyecto de ejemplo mostrando QuinotoSpec con Python + FastAPI + pytest.

## Stack

- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI
- **Package Manager**: pip
- **Testing**: pytest
- **Base de Datos**: SQLite (via SQLAlchemy)

## Estructura

```
python-fastapi/
├── .quinoto-spec/           # Configuracion QuinotoSpec
│   ├── discovery/           # 8 archivos de discovery
│   ├── proposals/           # Propuestas tecnicas
│   └── prefix-registry.md   # Prefijos registrados
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicacion FastAPI
│   ├── models.py            # Modelos de datos
│   └── routes/
│       ├── __init__.py
│       └── users.py         # Endpoints de usuarios
├── tests/
│   ├── __init__.py
│   ├── test_main.py
│   └── test_users.py
├── requirements.txt
└── README.md
```

## Setup

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicacion
uvicorn app.main:app --reload

# Ejecutar tests
pytest -v

# Ejecutar con cobertura
pytest --cov=app --cov-report=term-missing
```

## Uso con QuinotoSpec

### 1. Discovery
```bash
@quinotospec.discovery
```

### 2. Crear Propuesta
```bash
@quinotospec.create-proposal
# Descripcion: "Agregar autenticacion JWT con refresh tokens"
```

### 3. Generar Stories y Tareas
```bash
@quinotospec.create-user-stories --slug auth-jwt
@quinotospec.create-tasks --slug auth-jwt
```

### 4. Implementar
```bash
@quinotospec.apply --task-id TSK-AUTH-001
```

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/users` | Listar usuarios |
| POST | `/users` | Crear usuario |
| GET | `/users/{id}` | Obtener usuario |
