---
date: 2026-11-08
prefix: QSPE-a7f3
slug: ui-fase1-dashboard-readonly
format: v2
type: feature
---

## [2026-11-08] - UI Fase 1: dashboard web local read-only

### Resumen
- Nuevo `agent-dist/ui/` (solo stdlib): `readers.py` (lectores read-only de `.quinoto-spec/`), `templates.py` (HTML server-side + CSS embebido) y `server.py` (`http.server`, sin dependencias ni CDN).
- Paginas: `/` (panel con alertas y contadores), `/proposals`, `/proposals/<slug>`, `/tasks` (kanban multi-propuesta), `/changelog`, `/discovery`, `/constitution`; API `/api/summary` y healthcheck `/health`.
- Parsers: propuestas (`**Campo:**`), tareas en formato tabla y heading (estado/archivos/story/deps), changelog v1 y v2, discovery con frescura de 30 dias, constitucion con principios y prefix registry.
- Skill `quinotospec-ui` + workflow `quinotospec.ui` para lanzarla con `@quinotospec.ui` (inventario 49 workflows / 95 skills).
- Instalador: `agent-dist/ui` registrado en el ownership manifest (opencode y cursor) para que `--uninstall` no deje residuos.
- Tests: nueva suite `tests/test-ui.sh` (readers sobre fixture y ejemplo, roundtrip HTTP de 8 rutas, 404 y garantia read-only).
- Sin escritura: la UI no modifica `.quinoto-spec/` ni el repositorio.

**Validacion**: `bash scripts/validate-all.sh --strict` -> 0 errores, 0 warnings; `tests/run-all-tests.sh` -> 25/25 suites verdes.

**Tiempo Ahorrado**: ~14h (IA: ~45min vs Humano: ~14h de backend + templates + tests)

**Version**: sin bump (sigue 3.3.0).
