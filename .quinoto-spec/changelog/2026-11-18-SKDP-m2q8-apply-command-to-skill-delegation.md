---
date: 2026-11-18
prefix: SKDP-m2q8
slug: apply-command-to-skill-delegation
format: v2
type: change
---

## [2026-11-18] - Tarea: TSK-SKDP-m2q8-001..012 — Command-to-Skill Delegation implementada

### Resumen
- `scripts/generate-command-stubs.py` — [creado] — generador con plantilla única: 48 stubs con `$ARGUMENTS`, resolución del SKILL.md por archivo (repo fuente → local → global), modo `--check` y `--write`; par `review` excluido mientras PWRE-9f2c esté En Curso.
- `agent-dist/workflows/quinotospec.*.md` — [modificado] — 48 comandos convertidos en stubs (H1 + delegación textual), 0 prompts duplicados; `review` intacto con deuda registrada en `.quinoto-spec/reviews/SKDP-m2q8-review-pair-debt.md`.
- `agent-dist/skills/*/SKILL.md` — [modificado] — 42 skills consolidadas con el contenido completo de su workflow + secciones exclusivas (0 pares con contenido workflow-only según inventario); 48 skills pareadas con nota "esta skill contiene el prompt canónico"; ninguna pérdida de H2/scripts.
- `scripts/check-skill-workflow-drift.py` — [modificado] — deja de exigir paridad y valida delegación: stub exacto, skill existente/no vacía, conservación del contenido original vs. HEAD; CLI y esquema JSON conservados; par diferido reportado como INFO.
- `tests/test-skill-workflow-drift.sh` — [modificado] — 6/6 checks (stub válido, duplicado detectado, skill huérfana).
- `tests/test-installed-paths.sh` — [modificado] — checks J/K: resolución del stub en instalación local y global (11/11).
- `tests/test-discovery-sources.sh`, `test-engineering-skills.sh`, `test-constitution.sh`, `test-receive-review.sh`, `test-worktree.sh` — [modificados] — verificaciones de contenido movidas de workflows (stubs) a las skills (fuente de verdad), sin reducir cobertura.
- `AGENTS.md`, `docs/ARCHITECTURE.md` — [modificados] — documentado el patrón de delegación comando→skill.
- `.quinoto-spec/approvals/SKDP-m2q8-APPLY.json` — [creado] — aprobación registrada y validada ANTES del Apply (approval_validate.py).
- `.quinoto-spec/evidence/TSK-SKDP-m2q8-*/` — [creado] — inventario, RED/GREEN, logs de checker/suite/smoke, goldfish (12/12) y verify-before-done (12/12), validados con evidence_validate.py (31/31).
- Gates: RED observado (5 checks, 1 error) antes del checker nuevo; GREEN 6/6 + 11/11; `validate-all.sh --strict` 0/0; `run-all-tests.sh` 31/31; smoke del tarball 3.4.0 en 5 IDEs; Goldfish con veredicto `pass` tras resolver contradicciones normativas.
- Estado DoD: ✅ 48/49 conversiones + `review` diferido con deuda (regla de conteo normativa); skills como fuente única; 0 prompts duplicados en comandos convertidos.

**Tiempo Ahorrado**: ~24h (IA: ~1.5h vs Humano: ~3 días)
