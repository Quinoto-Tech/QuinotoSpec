# Playground: Python FastAPI con QuinotoSpec

API REST minima (usuarios) con el pipeline QuinotoSpec **ya generado**: es el
ejemplo que conviene clonar cuando queres ver como se ve `.quinoto-spec/` en un
proyecto real antes de invertir tiempo en el tuyo.

## En 5 minutos

```bash
# 1. Levantar el ejemplo (sin instalar el paquete)
cd examples/python-fastapi
pip install -r requirements.txt
pytest -v                       # 5 tests verdes
uvicorn app.main:app --reload   # Swagger en http://127.0.0.1:8000/docs

# 2. Mirar el pipeline ya generado
cat .quinoto-spec/discovery/01-stack-profile.md
cat .quinoto-spec/proposals/users-api/proposal.md
cat .quinoto-spec/changelog/*.md

# 3. (Opcional) Instalar QuinotoSpec y pedirle el siguiente paso
cd ../..
./install.sh --opencode
# en el IDE, dentro de examples/python-fastapi:
@quinotospec.help
```

`@quinotospec.help` lee el `.quinoto-spec/` existente y recomienda el proximo
comando concreto (no hace falta correr discovery de cero).

## Stack

- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI
- **Package Manager**: pip
- **Testing**: pytest + `fastapi.testclient`
- **Persistencia**: lista en memoria (demo; el discovery propone SQLite + SQLAlchemy)

## Estructura

```text
python-fastapi/
├── .quinoto-spec/
│   ├── discovery/                 # 8 archivos (01..08) + README indice
│   ├── proposals/users-api/       # proposal + user stories + tasks (completada)
│   ├── changelog/                 # entrada v2 de la propuesta
│   └── prefix-registry.md         # prefijo USRS-9k1m
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app + / y /health
│   ├── models.py                  # User y UserCreate (pydantic)
│   └── routes/
│       ├── __init__.py
│       └── users.py               # CRUD de usuarios
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

### 0. Ver donde estas parado
```bash
@quinotospec.help
```

### 1. Discovery (ya generado en este ejemplo)
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

## Que muestra el `.quinoto-spec/`

| Artefacto | Donde mirar | Que aprender |
|-----------|-------------|--------------|
| Discovery | `discovery/01..08` | Contexto que el agente lee antes de proponer |
| Propuesta | `proposals/users-api/proposal.md` | Alcance, alternativas, riesgos y plan de verificacion |
| Historias | `proposals/users-api/user-stories.md` | Valor + criterios de aceptacion verificables |
| Tareas | `proposals/users-api/USRS-9k1m_tasks.md` | Desglose atomico con estados |
| Changelog v2 | `changelog/2026-08-01-USRS-9k1m-usuarios-crud.md` | Registro append-only de la entrega |
| Prefijos | `prefix-registry.md` | ID unico por propuesta (`USRS-9k1m`) |

## Endpoints

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Status |
| GET | `/users/` | Listar usuarios (con barra final) |
| POST | `/users/` | Crear usuario (con barra final) |
| GET | `/users/{id}` | Obtener usuario |
