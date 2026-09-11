# Propuesta: API de usuarios CRUD

**Prefijo**: USRS-9k1m
**Fecha**: 2026-08-01
**Estado**: Completada (archivada — ejemplo didactico)

## Resumen Ejecutivo

Exponer un CRUD minimo de usuarios (`/users`) con validacion via pydantic y respuestas JSON. Persistencia en memoria para la demo; la version productiva migraria a SQLite + SQLAlchemy.

## Alternativas Consideradas

1. **SQLite directo** — mas realista, pero agrega dependencias a la demo. Descartado para mantener el ejemplo minimo.
2. **PostgreSQL + Docker** — sobredimensionado para un ejemplo de onboarding.

## Riesgos

- Datos se pierden al reiniciar (aceptado: demo)
- Sin autenticacion (fuera de alcance)

## Plan de Verificacion

- `pytest -v` verde
- Endpoints manuales con TestClient
