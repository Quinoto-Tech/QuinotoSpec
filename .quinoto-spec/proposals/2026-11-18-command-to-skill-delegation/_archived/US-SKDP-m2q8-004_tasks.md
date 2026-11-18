# Plan de Tareas (Command-to-Skill Delegation — US-SKDP-m2q8-004)

**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Prefijo:** SKDP-m2q8
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-SKDP-m2q8-009 | Backend | Checker invertido: delegación en vez de paridad | Reescribir `check()` para validar stub exacto, skill existente/no vacía y conservación de referencias a scripts; workflow sin skill → ERROR, skill standalone → INFO. Conservar CLI (`--root`, `--json`) y esquema JSON. | US-SKDP-m2q8-004 | drift-checker | scripts/check-skill-workflow-drift.py | M | P2 | TSK-SKDP-m2q8-006 | [x] |
| TSK-SKDP-m2q8-010 | Test | Tests del nuevo contrato + resolución instalada | Actualizar `test-skill-workflow-drift.sh` (stub válido, duplicado detectado, skill huérfana) y extender `test-installed-paths.sh` para verificar que el stub resuelve la skill instalada en layouts local y global. | US-SKDP-m2q8-004 | drift-checker | tests/test-skill-workflow-drift.sh, tests/test-installed-paths.sh | M | P2 | TSK-SKDP-m2q8-009, TSK-SKDP-m2q8-006 | [x] |
