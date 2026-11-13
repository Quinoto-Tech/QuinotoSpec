# 05 — Datos y servicios

## Modelos

| Modelo | Campos | Uso |
|--------|--------|-----|
| `User` | `id:int`, `username:str`, `email:str` | Respuesta de la API |
| `UserCreate` | `username:str`, `email:str` | Body de `POST /users` |

Ambos viven en `app/models.py` y son pydantic v2 (`.model_dump()` en el router).

## Persistencia

| Aspecto | Estado actual |
|---------|---------------|
| Almacenamiento | Lista en memoria (`users_db` en `app/routes/users.py`) |
| Migraciones | No aplica |
| Transacciones | No aplica |
| Vida util | Se pierde al reiniciar el proceso |

## Servicios externos

Ninguno. El ejemplo no hace llamadas salientes ni requiere credenciales.

## Dependencias declaradas y su uso real

| Paquete | Se usa | Para que |
|---------|--------|----------|
| `fastapi`, `uvicorn` | Si | App y servidor dev |
| `pydantic` | Si (via fastapi) | `User` y `UserCreate` |
| `pytest`, `httpx`, `pytest-cov` | Si | Suite de tests y cobertura |

Rangos abiertos (`>=x,<y`) para que instale en Python 3.11-3.15. Los pins exactos
viejos (`fastapi==0.104`, `pydantic==2.5`) no tienen wheels para 3.13+ y fallaban
compilando `pydantic-core`.

Si se migra a base de datos real, el cambio se limita a `app/routes/users.py`
(sesion SQLAlchemy) y a un `db.py` nuevo; los contratos de `app/models.py` no
cambian. `SQLAlchemy` se agrega **cuando se implemente**, no antes.
