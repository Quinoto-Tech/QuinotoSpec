---
name: Tasks — US-PWRE-9f2c-008
description: CI, documentación y dogfooding
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-008)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-028 | DevOps | Agregar job `ui-playwright` condicionado | Crear job en CI que se ejecute solo ante cambios de UI, review o `agent-dist/skills/quinotospec-review/e2e`, con cache de navegador, timeout menor a 10 minutos y Chromium. | US-PWRE-9f2c-008 | ci | `.github/workflows/ci.yml` | M | P2 | TSK-PWRE-9f2c-015<br>TSK-PWRE-9f2c-016<br>TSK-PWRE-9f2c-019 | [x] |
| TSK-PWRE-9f2c-029 | Docs | Documentar app, MCP y troubleshooting | Crear `docs/PLAYWRIGHT-REVIEW.md` con instalación de app, configuración MCP, flags, outputs, CI, seguridad y problemas comunes. | US-PWRE-9f2c-008 | ci | `docs/PLAYWRIGHT-REVIEW.md` | M | P2 | TSK-PWRE-9f2c-012<br>TSK-PWRE-9f2c-015<br>TSK-PWRE-9f2c-024 | [x] |
| TSK-PWRE-9f2c-030 | Docs | Actualizar README, arquitectura y manifest | Mencionar el flag opcional en README ES/EN, actualizar la matriz de madurez y agregar `features.playwright_review` con madurez `experimental`. | US-PWRE-9f2c-008 | ci | `README.md`<br>`README_EN.md`<br>`docs/ARCHITECTURE.md`<br>`manifest.json` | S | P2 | TSK-PWRE-9f2c-001<br>TSK-PWRE-9f2c-029 | [x] |
| TSK-PWRE-9f2c-031 | DevOps | Ejecutar dogfooding y validación completa | Correr `--playwright` sobre esta propuesta en app y MCP, verificar evidencia y ejecutar `tests/run-all-tests.sh` + `scripts/validate-all.sh --strict`. | US-PWRE-9f2c-008 | ci | `.quinoto-spec/reviews/`<br>`tests/test-review-playwright.sh` | S | P2 | TSK-PWRE-9f2c-019<br>TSK-PWRE-9f2c-027<br>TSK-PWRE-9f2c-028<br>TSK-PWRE-9f2c-029<br>TSK-PWRE-9f2c-030 | [x] |
| TSK-PWRE-9f2c-032 | Docs | Registrar la implementación en changelog | Agregar la entrada v2 append-only con archivos modificados, resultados de tests y evidencia del dogfooding. | US-PWRE-9f2c-008 | ci | `.quinoto-spec/changelog/2026-11-13-PWRE-9f2c-playwright-review-implemented.md` | XS | P2 | TSK-PWRE-9f2c-031 | [x] |
