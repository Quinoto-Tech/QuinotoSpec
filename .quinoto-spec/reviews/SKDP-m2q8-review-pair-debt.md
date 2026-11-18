# Deuda registrada — par `quinotospec.review` (TSK-SKDP-m2q8-008)

**Estado:** diferido — NO convertido a stub en este Apply.

**Motivo:** la propuesta `PWRE-9f2c` (*Playwright Proposal Review*) continúa **🟢 En Curso** y afecta `review-workflow` (`agent-dist/workflows/quinotospec.review.md`) y `ui`. Convertir el par mientras PWRE sigue activa generaría conflicto de contenido. Según `delta-specs/skill-layer/spec.md` y el criterio de TSK-008, se conserva el workflow completo y se difiere su conversión.

**Qué queda pendiente:**
1. Al cerrar PWRE-9f2c, revalidar el contenido de `agent-dist/skills/quinotospec-review/SKILL.md` contra los cambios del workflow.
2. Ejecutar `python3 -B scripts/generate-command-stubs.py --root . --write` (o `--render review`) para generar el stub del par.
3. Quitar `"review"` de `EXCLUDED` en `scripts/generate-command-stubs.py` y de `DEFERRED` en `scripts/check-skill-workflow-drift.py`.
4. Re-ejecutar `tests/test-skill-workflow-drift.sh` y `tests/run-all-tests.sh`.

**Impacto:** el checker actual ignora este par con estado INFO (`deferred`), por lo que la deuda es explícita y no silenciosa. El resto de los 48 pares sí quedó convertido.
