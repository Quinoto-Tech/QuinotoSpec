# Plan de Tareas (Validator Path Resolution — US-VPAT-k4m7-001)

**Proposal ID:** 2026-11-17-validator-path-resolution
**Prefijo:** VPAT-k4m7
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-VPAT-k4m7-001 | Test | Harness de instalación en temp + RED de rutas rotas | Crear `tests/test-installed-paths.sh`: fixture que instala el payload en un directorio temporal (staging hermano / `QUINOTOSPEC_INSTALL_TEST_MODE=true`, patrón `tests/test-bootstrap.sh`), y aserción que FALLA hoy: los `.md` instalados contienen `agent-dist/`. Registrar evidencia RED en `.quinoto-spec/evidence/TSK-VPAT-k4m7-001/` y validarla con `evidence_validate.py`. | US-VPAT-k4m7-001 | payload-python | tests/test-installed-paths.sh, .quinoto-spec/evidence/TSK-VPAT-k4m7-001/ | M | P1 | — | [x] |
| TSK-VPAT-k4m7-002 | Test | Casos para fallback `resolve_package_root` | Extender el suite con un proyecto fixture SIN `agent-dist/`: invocar `update_agents.py --root .` y `template_resolver.py` desde el fixture y aserciones de fallo actual (RED) + portabilidad Linux/macOS (`$TMPDIR`, sin GNU-only). | US-VPAT-k4m7-001 | payload-python | tests/test-installed-paths.sh, tests/fixtures/installed-project/ | S | P1 | TSK-VPAT-k4m7-001 | [x] |
