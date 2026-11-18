---
date: 2026-11-17
prefix: VPAT-k4m7
slug: apply-validator-path-resolution
format: v2
type: change
---

## [2026-11-17] - Tarea: TSK-VPAT-k4m7-001..010 — Validator Path Resolution implementada

### Resumen
- `install.sh` — [modificado] — nueva fase `normalize_staged_paths` entre el staging del payload y el ownership manifest: reescribe `agent-dist/` → ruta absoluta del destino de instalación en los `.md` de `workflows/commands, skills, rules, bootstrap, templates, agents, config`; el código (`.py/.sh/.js/.json`) queda intacto.
- `agent-dist/skills/quinotospec-update-agents/update_agents.py` — [modificado] — helpers `resolve_package_root`/`resolve_package_dir`: resuelven workflows/skills/rules/templates del layout fuente (`root/agent-dist/`), del layout plano instalado (`<install>/<asset>`) o `commands/` según IDE; `--root` del usuario no cambia de significado.
- `agent-dist/skills/quinotospec-template-resolver/template_resolver.py` — [modificado] — mismo fallback para los candidatos core (templates/workflows/skills).
- `tests/test-installed-paths.sh` — [creado] — suite de regresión con 9 checks: 0 refs `agent-dist/` post-instalación, preflight E2E del bootstrap ejecutable, fallback de entrypoints, regresión cero, reinstall idempotente, ruta con espacios/`&`, código byte-intacto, uninstall coherente.
- `tests/run-all-tests.sh` — [modificado] — registro de la suite nueva (31/31).
- `scripts/smoke-release.sh` — [modificado] — invariant post-install: 0 refs `agent-dist/` en `.md` instalados y preflight del bootstrap absoluto y existente.
- `.quinoto-spec/approvals/VPAT-k4m7-APPLY.json` — [creado] — aprobación humana estructurada del Apply (gate F-05 con override documentado), validada con `approval_validate.py`.
- `.quinoto-spec/evidence/TSK-VPAT-k4m7-*/` — [creado] — evidencia RED/GREEN, auditoría de ocurrencias, logs de smoke y verify-before-done de las 10 tareas, validada 14/14 con `evidence_validate.py`.
- Ciclo TDD: RED observado (4 checks fallando, 85 `.md` con rutas rotas) antes de tocar producción; GREEN con `tests/test-installed-paths.sh` 9/9; gates finales `validate-all.sh --strict` 0/0 y `run-all-tests.sh` 31/31; smoke del tarball 3.4.0 en los 5 IDEs.
- Estado DoD: ✅ criterios de US-VPAT-k4m7-001..005 cumplidos y evidenciados por tarea.

**Tiempo Ahorrado**: ~16h (IA: ~45min vs Humano: ~2.5 días)
