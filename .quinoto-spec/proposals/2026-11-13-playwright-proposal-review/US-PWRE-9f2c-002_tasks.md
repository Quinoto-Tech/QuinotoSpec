---
name: Tasks — US-PWRE-9f2c-002
description: Doctor de dependencias de Playwright
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-002)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-006 | Backend | Detectar app, Chromium y MCP | Implementar `playwright_doctor.py --check` con detección de Node 18+, `@playwright/test`, Chromium instalado y configuración MCP best-effort en los paths del IDE. | US-PWRE-9f2c-002 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_doctor.py` | M | P1 | TSK-PWRE-9f2c-001 | [x] |
| TSK-PWRE-9f2c-007 | Backend | Definir salida JSON y recomendación | Emitir `schema_version`, `node`, `app`, `mcp`, `options` y `recommended` con una estructura estable y sin efectos secundarios. | US-PWRE-9f2c-002 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_doctor.py` | S | P1 | TSK-PWRE-9f2c-006 | [x] |
| TSK-PWRE-9f2c-008 | Test | Tests del doctor | Cubrir app presente, app ausente, Chromium ausente, MCP configurado, MCP ausente, Node ausente y JSON inválido. Verificar que el doctor no instala ni escribe. | US-PWRE-9f2c-002 | review-workflow | `tests/test-playwright-doctor.py` | M | P1 | TSK-PWRE-9f2c-006<br>TSK-PWRE-9f2c-007 | [x] |
