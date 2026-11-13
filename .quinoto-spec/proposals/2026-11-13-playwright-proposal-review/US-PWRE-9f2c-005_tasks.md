---
name: Tasks — US-PWRE-9f2c-005
description: Harness Playwright reproducible
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-005)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-015 | Config | Crear configuración de `agent-dist/skills/quinotospec-review/e2e` | Agregar `package.json` con `@playwright/test` dev-only, lockfile y `playwright.config.js` con Chromium, timeouts, reporter y output dir. | US-PWRE-9f2c-005 | tests | `agent-dist/skills/quinotospec-review/e2e/package.json`<br>`agent-dist/skills/quinotospec-review/e2e/package-lock.json`<br>`agent-dist/skills/quinotospec-review/e2e/playwright.config.js` | S | P2 | TSK-PWRE-9f2c-010 | [x] |
| TSK-PWRE-9f2c-016 | Test | Implementar spec de review visual | Abrir `/proposals/<slug>` y `/tasks/<taskId>`, validar 200, título, Mermaid, consola, `pageerror`, requests, overflow y capturar screenshots en 3 viewports. | US-PWRE-9f2c-005 | tests | `agent-dist/skills/quinotospec-review/e2e/proposal-review.spec.js` | L | P2 | TSK-PWRE-9f2c-015<br>TSK-PWRE-9f2c-020<br>TSK-PWRE-9f2c-021 | [x] |
| TSK-PWRE-9f2c-017 | Test | Implementar reporter JSON | Escribir `playwright.json` con checks, errores, requests, screenshots, resultado y metadatos de dependencia. | US-PWRE-9f2c-005 | tests | `agent-dist/skills/quinotospec-review/e2e/reporter.js` | M | P2 | TSK-PWRE-9f2c-016 | [x] |
| TSK-PWRE-9f2c-018 | Test | Crear fixture de propuesta | Crear `.quinoto-spec` de fixture con propuesta, tarea, tablas, código y bloques Mermaid válidos e inválidos para probar los checks. | US-PWRE-9f2c-005 | tests | `tests/fixtures/quinoto-spec-playwright/.quinoto-spec/proposals/`<br>`tests/fixtures/quinoto-spec-playwright/.quinoto-spec/specs/` | S | P2 | TSK-PWRE-9f2c-015 | [x] |
| TSK-PWRE-9f2c-019 | DevOps | Integrar suite de review visual | Crear `tests/test-review-playwright.sh`, registrar la suite en `run-all-tests.sh` y verificar UI + orquestador + fixture + skip/app. | US-PWRE-9f2c-005 | tests | `tests/test-review-playwright.sh`<br>`tests/run-all-tests.sh` | M | P2 | TSK-PWRE-9f2c-005<br>TSK-PWRE-9f2c-016<br>TSK-PWRE-9f2c-018 | [x] |
