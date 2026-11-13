---
name: Tasks — US-PWRE-9f2c-004
description: Onboarding y backend Playwright MCP
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-004)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-012 | Backend | Implementar adaptador de configuración MCP | Detectar el IDE y escribir la entrada MCP o mostrar el snippet genérico cuando no sea seguro escribirla. Soportar `--install-playwright-mcp` y no simular configuración. | US-PWRE-9f2c-004 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py`<br>`agent-dist/skills/quinotospec-review/mcp_config.py` | M | P1 | TSK-PWRE-9f2c-009 | [x] |
| TSK-PWRE-9f2c-013 | Backend | Implementar backend MCP y manejo de reinicio | Usar herramientas MCP del agente, armar evidencia con `selected_backend: "mcp"`, indicar reinicio cuando corresponda y degradar a app u omitir si MCP no está disponible. | US-PWRE-9f2c-004 | review-workflow | `agent-dist/skills/quinotospec-review/playwright_review.py`<br>`agent-dist/workflows/quinotospec.review.md` | M | P1 | TSK-PWRE-9f2c-012 | [x] |
| TSK-PWRE-9f2c-014 | Test | Tests del onboarding MCP | Cubrir MCP detectado, no detectado, configuración escrita, snippet mostrado, reinicio requerido, backend MCP sin resultados y ausencia de simulación. | US-PWRE-9f2c-004 | review-workflow | `tests/test-review-playwright.py`<br>`tests/test-playwright-doctor.py` | M | P1 | TSK-PWRE-9f2c-012<br>TSK-PWRE-9f2c-013 | [x] |
