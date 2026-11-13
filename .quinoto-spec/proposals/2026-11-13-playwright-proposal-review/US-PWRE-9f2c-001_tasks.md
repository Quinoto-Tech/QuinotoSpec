---
name: Tasks — US-PWRE-9f2c-001
description: Flag de review visual y ciclo de vida del orquestador
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-001)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-001 | Config | Documentar el flag `--playwright` | Agregar el flag y sus parámetros al workflow y a la skill de review, incluyendo `--playwright-backend`, `--install-playwright`, `--install-playwright-mcp`, `--no-install-prompt` y `--require-playwright`. | US-PWRE-9f2c-001 | review-workflow | `agent-dist/workflows/quinotospec.review.md`<br>`agent-dist/skills/quinotospec-review/SKILL.md` | S | P1 | — | [x] |
| TSK-PWRE-9f2c-002 | Backend | Crear el esqueleto de `playwright_review.py` | Implementar argparse, resolución de `--root`, `--proposal`, `--task-id`, `--json`, validación del contrato y carga del doctor. | US-PWRE-9f2c-001 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py` | M | P1 | TSK-PWRE-9f2c-001 | [x] |
| TSK-PWRE-9f2c-003 | Backend | Implementar ciclo de vida de la UI | Buscar puerto libre en loopback, arrancar `server.py` con `--no-browser`, esperar `/health`, capturar stdout/stderr y detener el proceso en `finally` con SIGTERM y timeout. | US-PWRE-9f2c-001 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py` | M | P1 | TSK-PWRE-9f2c-002 | [x] |
| TSK-PWRE-9f2c-004 | Backend | Resolver propuesta y bloquear path traversal | Validar que el slug exista bajo `.quinoto-spec/proposals/`, rechazar `..`, rutas absolutas y symlinks, y garantizar que el review no escriba en proposals, specs ni discovery. | US-PWRE-9f2c-001 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py` | S | P1 | TSK-PWRE-9f2c-002 | [x] |
| TSK-PWRE-9f2c-005 | Test | Tests de ciclo de vida y aislamiento | Cubrir arranque/parada, puerto ocupado, timeout de health, propuesta inexistente, path traversal, cleanup sin procesos huérfanos y hash sin cambios en artefactos. | US-PWRE-9f2c-001 | review-workflow | `tests/test-review-playwright.py` | M | P1 | TSK-PWRE-9f2c-003<br>TSK-PWRE-9f2c-004 | [x] |
