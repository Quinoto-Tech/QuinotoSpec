# 02 — Overview

## Que es

API REST minima de usuarios (`/users`) usada como **playground** de QuinotoSpec: el
`.quinoto-spec/` de este directorio es un ejemplo real y completo (discovery,
propuesta, historias, tareas y changelog) para ver el resultado antes de invertir
tiempo en un proyecto propio.

## Stack

Python 3.11+ · FastAPI · pydantic v2 · pytest + httpx (`TestClient`)

## Estructura

```text
python-fastapi/
├── .quinoto-spec/                 # Pipeline QuinotoSpec (ejemplo real)
│   ├── discovery/                 # 8 archivos de contexto
│   ├── proposals/users-api/       # proposal + stories + tasks (completada)
│   ├── changelog/                 # entrada v2 de la unica propuesta
│   └── prefix-registry.md         # prefijo USRS-9k1m
├── app/
│   ├── main.py                    # FastAPI app + rutas /
│   ├── models.py                  # User y UserCreate (pydantic)
│   └── routes/users.py            # CRUD de usuarios en memoria
├── tests/                         # pytest + TestClient
└── requirements.txt
```

## Que hace

- `GET /` y `GET /health` para smoke checks
- `GET /users/`, `POST /users/`, `GET /users/{id}` sobre una lista en memoria
- Sin base de datos, sin autenticacion: el foco del ejemplo es el flujo
  QuinotoSpec, no la infraestructura

## Como arrancarlo

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload   # Swagger en http://127.0.0.1:8000/docs
pytest -v
```
