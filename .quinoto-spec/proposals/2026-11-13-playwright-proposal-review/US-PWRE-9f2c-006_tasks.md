---
name: Tasks — US-PWRE-9f2c-006
description: Selectores E2E, estado de Mermaid y checks visuales
---

# Plan de Tareas (Playwright Proposal Review — US-PWRE-9f2c-006)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-PWRE-9f2c-020 | Frontend | Agregar `data-testid` estables | Añadir atributos aditivos en título de propuesta, contenido Markdown, listas, navegación, buscador y selector de tema sin romper clases o IDs existentes. | US-PWRE-9f2c-006 | ui | `agent-dist/ui/templates.py` | M | P2 | — | [x] |
| TSK-PWRE-9f2c-021 | Frontend | Exponer estado observable de Mermaid | Implementar `data-mermaid-state` con `pending`, `rendered` y `error`, y asegurar que el SVG se marca como renderizado. | US-PWRE-9f2c-006 | ui | `agent-dist/ui/templates.py`<br>`agent-dist/ui/static/mermaid.min.js` | M | P2 | TSK-PWRE-9f2c-020 | [x] |
| TSK-PWRE-9f2c-022 | Test | Implementar checks BLOCKING y WARN | Agregar al spec los checks de HTTP, título, consola, `pageerror`, requests, Mermaid, overflow, screenshots, accesibilidad smoke y enlaces internos. | US-PWRE-9f2c-006 | ui | `agent-dist/skills/quinotospec-review/e2e/proposal-review.spec.js` | M | P2 | TSK-PWRE-9f2c-016<br>TSK-PWRE-9f2c-021 | [x] |
| TSK-PWRE-9f2c-023 | Test | Verificar regresión de la UI existente | Extender `tests/test-ui.sh` con aserciones de selectores y estado Mermaid, y confirmar que los 17 checks actuales siguen verdes. | US-PWRE-9f2c-006 | ui | `tests/test-ui.sh` | S | P2 | TSK-PWRE-9f2c-020<br>TSK-PWRE-9f2c-021 | [x] |
