# Goldfish Review — users-api (ejemplo python-fastapi)

- **Fecha:** 2026-11-08
- **Documento revisado:** `examples/python-fastapi/.quinoto-spec/proposals/users-api/proposal.md`
- **Modalidad:** Elephant-Goldfish, contexto aislado
- **Revisores (subagentes frescos):** 3 — Design Critic, Implementation Readiness, Comprehension+Zoom Out
- **Código modificado:** no

## Resumen

| Severidad | Hallazgos |
|-----------|-----------|
| BLOCKING | 6 |
| WARN | 7 |
| INFO | 2 |

El documento está **desalineado con su propio código** y no es implementable de forma literal. Los hallazgos se deduplicaron entre las tres lentes.

---

## BLOCKING

1. **Alcance "CRUD" no coincide con el código** — `proposal.md:1,9` vs `app/routes/users.py:9-26`: solo existen list/create/get; no hay update ni delete. El estado dice "Completada".
   → Renombrar a "Create/Read" + `Fuera de alcance`, o implementar `PUT/PATCH/DELETE` antes de declararla completada.

2. **IDs por `len(users_db)+1`** — `app/routes/users.py:16`: O(n), no atómico, colisiona tras cualquier borrado y viola unicidad histórica.
   → Contador monótono (`itertools.count` / `max(id)+1` persistido) o delegar el ID a la persistencia.

3. **Condición de carrera en `POST`** — `app/routes/users.py:16-17`: dos corrutinas pueden leer el mismo `len()` antes del `append` y generar IDs duplicados.
   → Lock (`asyncio.Lock`) alrededor de asignación+append + test de concurrencia.

4. **Estado global mutable como única persistencia** — `app/routes/users.py:6`: no inyectable, no se resetea entre tests, diverge con `--workers>1`. La propuesta solo admite "datos se pierden al reiniciar" (`proposal.md:18`), omitiendo el modo de fallo multi-worker.
   → Ocultar el store tras `Depends` y declarar la restricción de un proceso.

5. **La propuesta no declara archivos ni firmas** — `proposal.md:1-24`: no nombra `app/models.py`, `app/routes/users.py`, `app/main.py` ni schemas; el detalle solo está en las tareas.
   → Añadir sección "Archivos y contratos" con rutas, schemas y handlers.

6. **Plan de verificación no reproducible** — `proposal.md:23`: `pytest -v` falla en colección (`ModuleNotFoundError: fastapi`) sin setup/venv/`conftest.py`.
   → Documentar `python -m venv .venv && pip install -r requirements.txt && pytest -v` desde la raíz del ejemplo.

## WARN

1. **"Validación vía pydantic" sobrevendida** — `proposal.md:9` vs `app/models.py:7,11`: `email: str`, sin `EmailStr`, sin unicidad, sin test 422.
   → Usar `EmailStr` + `Field(min_length=...)` o acotar la afirmación.

2. **`User(**user.model_dump())` acopla por nombre de campo** — `app/routes/users.py:16`: un campo `id`/`status` nuevo en `UserCreate` rompe en runtime.
   → Construcción explícita o `model_validate({**dump, "id": ...})`.

3. **`GET /users/` sin `response_model` ni paginación** — `app/routes/users.py:9-11`: leak de representación interna y payload sin límite.
   → `UserOut` + `response_model` + `limit/offset`.

4. **Contradicción con dependencias** — `proposal.md:13` descarta SQLite por "agregar dependencias", pero `requirements.txt:3` ya pinea `sqlalchemy==2.0.23` y `README.md:11` afirma SQLite.
   → Eliminar la dependencia o justificar por qué se mantiene declarada.

5. **Ruta canónica ambigua `/users` vs `/users/`** — `proposal.md:9` vs `app/routes/users.py:4,9` y tests usan `/users/`; `/users` responde 307.
   → Fijar la forma con barra final en propuesta, stories, README y tests.

6. **IDs no siguen el prefijo declarado** — `USRS-9k1m_tasks.md` usa `TSK-USR-001` y `user-stories.md` usa `US-001`, sin el sufijo `9k1m`.
   → Normalizar a `US-USRS-9k1m-001` / `TSK-USRS-9k1m-001` o declarar legacy.

7. **Auto-contención** — el documento no enlaza discovery/stories/tasks ni define contrato de API (rutas, request/response, códigos).
   → Añadir "Contexto / Referencias" y una tabla de endpoints.

## INFO

1. **Estado "archivada" pero el artefacto sigue activo** — `proposal.md:5` vs `proposals/users-api/` (`_archived/` vacío).
   → Mover a `_archived/` o corregir el estado.

2. **Tests comparten estado** — `tests/test_users.py:4,7-19`: un solo `TestClient` y `users_db` global; `test_list_users` depende del orden.
   → `conftest.py` con fixture de client y reset del store por test.

---

## Veredicto Goldfish

**REQUIERE CAMBIOS.** El documento no está listo para implementación literal ni para declararse completado: alcance, contratos, IDs y verificación no coinciden con el código. Priorizar BLOCKING 1 (alcance), 2-4 (store/IDs) y 5-6 (contratos/verificación).

> Nota: esta revisión no reemplaza tests ni juicio humano; es una capa de detección de puntos ciegos.
