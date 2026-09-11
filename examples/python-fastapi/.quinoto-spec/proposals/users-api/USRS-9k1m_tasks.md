# Tasks — USRS-9k1m / US-001 a US-003

## TSK-USR-001 — Modelo User + router de usuarios

- **Story**: US-002
- **Estado**: completada
- **Archivos**: `app/models.py`, `app/routes/users.py`
- **Detalles**: Modelos pydantic `User`/`UserCreate`; router con prefix `/users`; store in-memory.

## TSK-USR-002 — Registrar router en la app

- **Story**: US-001
- **Estado**: completada
- **Archivos**: `app/main.py`
- **Detalles**: `app.include_router(users.router)`; endpoints de health en main.

## TSK-USR-003 — Tests de integracion

- **Story**: US-001, US-002, US-003
- **Estado**: completada
- **Archivos**: `tests/test_users.py`, `tests/test_main.py`
- **Detalles**: create (201), list (200), get inexistente (404), root/health.

## TSK-USR-004 — Verificacion final

- **Story**: todas
- **Estado**: completada
- **Comando**: `pytest -v` → 5 passed
