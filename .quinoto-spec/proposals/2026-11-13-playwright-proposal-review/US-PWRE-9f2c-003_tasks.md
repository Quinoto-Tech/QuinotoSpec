---
name: Tasks — US-PWRE-9f2c-003
description: Onboarding e instalación consentida de Playwright app
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-003)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-009 | Backend | Implementar menú de onboarding y estados | Presentar las opciones app, MCP y omitir; devolver `action_required` en no-TTY, `skipped` con `--no-install-prompt` y mensajes accionables sin instalar nada. | US-PWRE-9f2c-003 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py` | M | P1 | TSK-PWRE-9f2c-003<br>TSK-PWRE-9f2c-008 | [x] |
| TSK-PWRE-9f2c-010 | Backend | Instalar app y Chromium con consentimiento | Implementar `--install-playwright` con confirmación, `npm install` en `agent-dist/skills/quinotospec-review/e2e/`, `npx playwright install chromium`, re-ejecución del doctor y prohibición de `sudo` o instalación global. | US-PWRE-9f2c-003 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py`<br>`agent-dist/skills/quinotospec-review/e2e/package.json` | M | P1 | TSK-PWRE-9f2c-009 | [x] |
| TSK-PWRE-9f2c-011 | Test | Tests del onboarding app | Cubrir confirmación, cancelación, fallo de npm, fallo de Chromium, re-check exitoso, `--yes` sin autorización y ausencia de `sudo`. | US-PWRE-9f2c-003 | review-workflow | `tests/test-review-playwright.py` | M | P1 | TSK-PWRE-9f2c-009<br>TSK-PWRE-9f2c-010 | [x] |
