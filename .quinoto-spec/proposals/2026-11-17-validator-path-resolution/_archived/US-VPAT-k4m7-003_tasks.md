# Plan de Tareas (Validator Path Resolution — US-VPAT-k4m7-003)

**Proposal ID:** 2026-11-17-validator-path-resolution
**Prefijo:** VPAT-k4m7
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-VPAT-k4m7-006 | Backend | Orden transaccional: normalización antes del manifest | Garantizar en `install.sh` el orden staging → normalización → SHA-256 del ownership manifest → `verify_installation` → `mv` a destino. Añadir aserciones al suite: uninstall posterior verifica/remueve los `.md` reescritos sin conflictos, y `*.py/*.sh/*.js/*.json` staged son byte-idénticos al source. | US-VPAT-k4m7-003 | installer | install.sh, tests/test-installed-paths.sh | S | P1 | TSK-VPAT-k4m7-004 | [x] |
