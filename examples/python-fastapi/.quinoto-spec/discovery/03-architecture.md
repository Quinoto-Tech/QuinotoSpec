# 03 — Architecture

## Estilo

Monolito de una sola capa con separacion por responsabilidad, sin capa de
persistencia: el ejemplo prioriza legibilidad sobre realismo de produccion.

```text
HTTP request
    |
    v
app/main.py          FastAPI app, monta los routers y expone / y /health
    |
    v
app/routes/users.py  Router /users: valida entrada, aplica reglas, responde
    |
    v
app/models.py        Contratos pydantic: User (salida) y UserCreate (entrada)
```

## Decisiones

| Decision | Motivo | Consecuencia |
|----------|--------|--------------|
| Persistencia en lista (`users_db`) | Cero dependencias externas para una demo | Los datos se pierden al reiniciar |
| Router separado por recurso | Mostrar la estructura que crece con el proyecto | Un archivo por recurso |
| `APIRouter(prefix="/users")` | El prefijo vive en un solo lugar | Cambiar la ruta base es una linea |
| Sin capa de servicios | El ejemplo no justifica abstraccion extra | La logica vive en el router |
| `from app.routes import users` | Import absoluto, sin sorpresas | Requiere correr desde la raiz del ejemplo |

## Flujo de una escritura

1. FastAPI parsea el body contra `UserCreate` (422 si no valida).
2. El router asigna `id = len(users_db) + 1` y construye el `User`.
3. Se agrega a `users_db` y se responde 201 con el modelo de salida.

## Limites conocidos

- `users_db` es global al proceso: no hay aislamiento entre requests de escritura
  concurrentes ni entre workers de uvicorn.
- `sqlalchemy` figura en `requirements.txt` pero no se importa (ver `07-findings`).
