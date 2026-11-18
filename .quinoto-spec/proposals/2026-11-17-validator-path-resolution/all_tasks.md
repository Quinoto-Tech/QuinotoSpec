# All Tasks (Validator Path Resolution)

**Proposal ID:** 2026-11-17-validator-path-resolution
**Prefijo:** VPAT-k4m7
**Estado:** completed

Consolidado de las tareas de todas las user stories. Fuente por story: `US-VPAT-k4m7-00N_tasks.md`.

| ID | Tipo | Título | Historia Relacionada | Servicio | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|
| TSK-VPAT-k4m7-001 | Test | Harness de instalación en temp + RED de rutas rotas | US-VPAT-k4m7-001 | payload-python | M | P1 | — | [x] |
| TSK-VPAT-k4m7-002 | Test | Casos para fallback `resolve_package_root` | US-VPAT-k4m7-001 | payload-python | S | P1 | TSK-VPAT-k4m7-001 | [x] |
| TSK-VPAT-k4m7-003 | Config | Auditoría de los ~108 archivos con `agent-dist/` | US-VPAT-k4m7-002 | installer | S | P1 | TSK-VPAT-k4m7-001 | [x] |
| TSK-VPAT-k4m7-004 | Backend | `normalize_staged_paths` en install.sh + wiring | US-VPAT-k4m7-002 | installer | M | P1 | TSK-VPAT-k4m7-001, TSK-VPAT-k4m7-003 | [x] |
| TSK-VPAT-k4m7-005 | Test | E2E del preflight del bootstrap instalado | US-VPAT-k4m7-002 | installer | S | P1 | TSK-VPAT-k4m7-004 | [x] |
| TSK-VPAT-k4m7-006 | Backend | Orden transaccional: normalización antes del manifest | US-VPAT-k4m7-003 | installer | S | P1 | TSK-VPAT-k4m7-004 | [x] |
| TSK-VPAT-k4m7-007 | Backend | Fallback en `update_agents.py` | US-VPAT-k4m7-004 | payload-python | S | P1 | TSK-VPAT-k4m7-002 | [x] |
| TSK-VPAT-k4m7-008 | Backend | Fallback en `template_resolver.py` + regresión cero en fuente | US-VPAT-k4m7-004 | payload-python | XS | P1 | TSK-VPAT-k4m7-007 | [x] |
| TSK-VPAT-k4m7-009 | DevOps | Aserción de invariant en smoke-release | US-VPAT-k4m7-005 | installer | S | P1 | TSK-VPAT-k4m7-005, TSK-VPAT-k4m7-006 | [x] |
| TSK-VPAT-k4m7-010 | DevOps | Gates finales en verde + evidencia + changelog | US-VPAT-k4m7-005 | installer | S | P1 | TSK-VPAT-k4m7-007, TSK-VPAT-k4m7-008, TSK-VPAT-k4m7-009 | [x] |
