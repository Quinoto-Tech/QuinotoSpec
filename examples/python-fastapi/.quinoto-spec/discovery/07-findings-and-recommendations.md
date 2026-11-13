# 07 — Hallazgos y recomendaciones

## Deuda tecnica

| # | Hallazgo | Impacto | Recomendacion |
|---|----------|---------|---------------|
| 1 | Persistencia en lista en memoria | Datos volatiles; no apto para produccion | SQLAlchemy + SQLite, como ya sugiere `05-data-and-services.md` |
| 2 | `sqlalchemy`, `python-jose` y `passlib` declaradas sin uso | Instalacion mas lenta y superficie de ataque mayor | **Resuelto**: se quitaron de `requirements.txt` (se agregan cuando se implemente la feature) |
| 3 | `id = len(users_db) + 1` | Ids repetibles si se agrega borrado | Contador monotono o `id` de la base |
| 4 | `email` sin validacion de formato | Acepta valores invalidos | `EmailStr` (`pydantic[email]`) |
| 5 | Sin paginacion en `GET /users` | La respuesta crece sin limite | `limit`/`offset` con defaults |
| 6 | Sin CI del ejemplo | Una regresion pasa desapercibida | Workflow `pytest` en cada push |
| 7 | Sin `CORS` ni auth | Inutilizable fuera de localhost | Definir antes de exponerlo |

## Lo que esta bien y conviene mantener

- Contratos separados (`User` vs `UserCreate`): evita aceptar `id` desde el cliente.
- Un router por recurso con prefijo propio.
- Tests con `TestClient`, sin levantar servidor real.
- Versiones fijas en `requirements.txt`.

## Proximos pasos sugeridos

1. Migrar a SQLite + SQLAlchemy detras de `app/db.py` (no cambia el contrato).
2. Agregar `EmailStr` y un test de validacion (422).
3. Implementar `DELETE /users/{id}` y recien despues revisar la estrategia de ids.
4. Sumar workflow de CI del ejemplo.
