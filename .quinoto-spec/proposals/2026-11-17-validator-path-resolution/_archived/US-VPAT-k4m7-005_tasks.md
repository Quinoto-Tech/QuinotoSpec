# Plan de Tareas (Validator Path Resolution — US-VPAT-k4m7-005)

**Proposal ID:** 2026-11-17-validator-path-resolution
**Prefijo:** VPAT-k4m7
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-VPAT-k4m7-009 | DevOps | Aserción de invariant en smoke-release | Extender `scripts/smoke-release.sh`: tras instalar el tarball en temp dir, verificar 0 ocurrencias de `agent-dist/` en `.md` instalados y preflight del bootstrap ejecutable (exit 0) en un proyecto fixture. | US-VPAT-k4m7-005 | installer | scripts/smoke-release.sh | S | P1 | TSK-VPAT-k4m7-005, TSK-VPAT-k4m7-006 | [x] |
| TSK-VPAT-k4m7-010 | DevOps | Gates finales en verde + evidencia + changelog | Correr `bash scripts/validate-all.sh --strict` (0/0), `bash tests/run-all-tests.sh` (29/29), registrar evidencia de cierre en `.quinoto-spec/evidence/` validada con `evidence_validate.py`, y generar entrada de changelog vía `quinotospec-update-changelog`. | US-VPAT-k4m7-005 | installer | .quinoto-spec/changelog/, .quinoto-spec/evidence/ | S | P1 | TSK-VPAT-k4m7-007, TSK-VPAT-k4m7-008, TSK-VPAT-k4m7-009 | [x] |
