---
name: Tasks — US-PWRE-9f2c-007
description: Evidencia, informe e integración con review
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-007)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-024 | Backend | Escribir evidencia JSON y Markdown | Generar `reviews/<slug>-playwright.json` con `schema_version: 1` y bloque `dependency`, y `reviews/<slug>-playwright.md` con resumen, opción elegida, checks y hallazgos. | US-PWRE-9f2c-007 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py` | M | P2 | TSK-PWRE-9f2c-017 | [x] |
| TSK-PWRE-9f2c-025 | Backend | Integrar resultado al checklist de review | Mapear `pass`, `warn`, `fail`, `skipped` y `action_required` al informe de review; agregar severidades y el paso visual al workflow y a la skill. | US-PWRE-9f2c-007 | review-workflow | `agent-dist/workflows/quinotospec.review.md`<br>`agent-dist/skills/quinotospec-review/SKILL.md` | M | P2 | TSK-PWRE-9f2c-024<br>TSK-PWRE-9f2c-022 | [x] |
| TSK-PWRE-9f2c-026 | Config | Aislar screenshots y artefactos | Guardar screenshots en `.quinoto-spec/reviews/.artifacts/`, agregar la regla a `.gitignore` y verificar que solo JSON/MD queden versionables. | US-PWRE-9f2c-007 | review-workflow | `.gitignore`<br>`agent-dist/skills/quinotospec-review/playwright_review.py` | S | P2 | TSK-PWRE-9f2c-024 | [x] |
| TSK-PWRE-9f2c-027 | Test | Tests de evidencia y no mutación | Cubrir JSON/MD, `schema_version`, bloque `dependency`, screenshots, estados, hash sin cambios en propuesta/specs/discovery y artefactos ignorados. | US-PWRE-9f2c-007 | review-workflow | `tests/test-review-playwright.py` | M | P2 | TSK-PWRE-9f2c-024<br>TSK-PWRE-9f2c-025<br>TSK-PWRE-9f2c-026 | [x] |
