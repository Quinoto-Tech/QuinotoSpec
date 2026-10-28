---
date: 2026-10-28
prefix: QSPE-a7f3
slug: review-handoff
format: v2
type: change
---

## [2026-10-28] - Review Handoff: guia de code review para el revisor humano

### Resumen
- Se creo `quinotospec.review-handoff` (workflow + skill espejo `quinotospec-review-handoff`): cuando una propuesta esta completada y antes de `archive`, genera `CODE_REVIEW_GUIDE.md` dentro de la propuesta con 11 secciones — resumen para el reviewer, user stories y criterios de aceptacion, tabla de tareas, cambios en git (commits, `--name-status`, `--stat`, mapeo tarea a commits), historial del changelog del prefijo, evidencia de verificacion, delta specs, comandos de verificacion del stack, checklist de revision, riesgos y areas sensibles, y como reportar feedback via `quinotospec-receive-review`.
- Gates del workflow: completitud via `contract.py inspect` (tareas pendientes exigen `--force` y quedan documentadas), evidencia por tarea (advertencia, no bloqueo), discovery obsoleto y constitucion activa/ausente. Flags: `--force`, `--full-diff`, `--output PATH`, `--archived`.
- Routing: `help.py` ahora recomienda `/quinotospec.review-handoff {{slug}}` entre `mark-done` y `archive` cuando todas las tareas estan completas; `test-help-and-routing.sh` extendido con fixture de propuesta completada.
- Documentacion del flujo: seccion dedicada y pipeline completo de feature en `docs/ADVANCED-USAGE.md`, e Integracion Recomendada en `README.md`.
- Inventario sincronizado en 47 workflows y 90 skills: `manifest.json` (+ `features.review_handoff` y `capability_maturity.review_handoff`), `scripts/validate-all.sh`, `install.sh` (thresholds), `config-template.yml` (lista active), `AGENTS.md` (tabla de workflows complementarios), README/README_EN (badges, tabla de comandos y mapa de dependencias) y `docs/ARCHITECTURE.md`.
- Excepcion a Proposal First (implementacion directa) aprobada por el maintainer en la sesion de planificacion y registrada en `.quinoto-spec/approvals/QSPE-REVIEW-HANDOFF.json`, validada con `approval_validate.py`.
- **Evidencia**: `validate-all.sh --strict --allow-no-node` en 0 errores / 0 warnings (23/23 suites); `test-workflows.sh` 47/47; `test-skills.sh` 90/90; `test-encoding.sh` 0 CJK; `test-help-and-routing.sh` 32/32 checks.

**Tiempo Ahorrado**: ~3h (IA: ~25min vs Humano: ~3h)
