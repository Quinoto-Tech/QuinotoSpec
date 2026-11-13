# 04 — Endpoints y contrato

No hay archivo OpenAPI versionado: FastAPI genera el schema en runtime
(`/docs` para Swagger UI y `/openapi.json` para el contrato).

## Endpoints

| Metodo | Ruta | Body | Respuesta OK | Errores |
|--------|------|------|--------------|---------|
| GET | `/` | — | 200 `{"status":"ok","message":"..."}` | — |
| GET | `/health` | — | 200 `{"status":"healthy"}` | — |
| GET | `/users/` | — | 200 `[User]` | — |
| POST | `/users/` | `UserCreate` | 201 `User` | 422 si el body no valida |
| GET | `/users/{user_id}` | — | 200 `User` | 404 si no existe |

## Modelos de entrada y salida

```text
UserCreate (entrada)      User (salida)
-------------------       ---------------------
username: str             id: int
email: str                username: str
                          email: str
```

## Ejemplo de uso

```bash
curl -s -X POST localhost:8000/users/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"ada","email":"ada@example.com"}'
# {"id":1,"username":"ada","email":"ada@example.com"}

curl -s localhost:8000/users/1
curl -s localhost:8000/users/99    # {"detail":"User not found"} (404)
```

## Observaciones de contrato

- Las rutas de coleccion llevan **barra final** (`/users/`) por como esta
  declarado el router (`APIRouter(prefix="/users")` + `@router.get("/")`).
  `/users` sin barra responde **307** hacia `/users/` (redirect_slashes de
  Starlette): si se consume desde un cliente que no sigue redirects, el body
  llega vacio. Los tests del ejemplo usan `/users/`.

- El `id` se deriva de `len(users_db) + 1`: si en el futuro se borran usuarios,
  pueden repetirse ids. Hoy no hay endpoint de borrado, asi que no ocurre.
- `email` no se valida con `EmailStr` (pydantic lo permite con `pydantic[email]`).
- No hay paginacion ni filtros: `GET /users` devuelve la lista completa.
