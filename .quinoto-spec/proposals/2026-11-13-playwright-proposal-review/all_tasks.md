# Plan de Tareas Consolidado (Playwright Proposal Review)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

> Índice derivado. La fuente primaria de cada tarea es el archivo `US-*_tasks.md` correspondiente.

## US-PWRE-9f2c-001

- Completada: `TSK-PWRE-9f2c-001` — Documentar el flag `--playwright` — `US-PWRE-9f2c-001_tasks.md` — dependencias: —
- Completada: `TSK-PWRE-9f2c-002` — Crear el esqueleto de `playwright_review.py` — `US-PWRE-9f2c-001_tasks.md` — dependencias: TSK-PWRE-9f2c-001
- Completada: `TSK-PWRE-9f2c-003` — Implementar ciclo de vida de la UI — `US-PWRE-9f2c-001_tasks.md` — dependencias: TSK-PWRE-9f2c-002
- Completada: `TSK-PWRE-9f2c-004` — Resolver propuesta y bloquear path traversal — `US-PWRE-9f2c-001_tasks.md` — dependencias: TSK-PWRE-9f2c-002
- Completada: `TSK-PWRE-9f2c-005` — Tests de ciclo de vida y aislamiento — `US-PWRE-9f2c-001_tasks.md` — dependencias: TSK-PWRE-9f2c-003<br>TSK-PWRE-9f2c-004
## US-PWRE-9f2c-002

- Completada: `TSK-PWRE-9f2c-006` — Detectar app, Chromium y MCP — `US-PWRE-9f2c-002_tasks.md` — dependencias: TSK-PWRE-9f2c-001
- Completada: `TSK-PWRE-9f2c-007` — Definir salida JSON y recomendación — `US-PWRE-9f2c-002_tasks.md` — dependencias: TSK-PWRE-9f2c-006
- Completada: `TSK-PWRE-9f2c-008` — Tests del doctor — `US-PWRE-9f2c-002_tasks.md` — dependencias: TSK-PWRE-9f2c-006<br>TSK-PWRE-9f2c-007
## US-PWRE-9f2c-003

- Completada: `TSK-PWRE-9f2c-009` — Implementar menú de onboarding y estados — `US-PWRE-9f2c-003_tasks.md` — dependencias: TSK-PWRE-9f2c-003<br>TSK-PWRE-9f2c-008
- Completada: `TSK-PWRE-9f2c-010` — Instalar app y Chromium con consentimiento — `US-PWRE-9f2c-003_tasks.md` — dependencias: TSK-PWRE-9f2c-009
- Completada: `TSK-PWRE-9f2c-011` — Tests del onboarding app — `US-PWRE-9f2c-003_tasks.md` — dependencias: TSK-PWRE-9f2c-009<br>TSK-PWRE-9f2c-010
## US-PWRE-9f2c-004

- Completada: `TSK-PWRE-9f2c-012` — Implementar adaptador de configuración MCP — `US-PWRE-9f2c-004_tasks.md` — dependencias: TSK-PWRE-9f2c-009
- Completada: `TSK-PWRE-9f2c-013` — Implementar backend MCP y manejo de reinicio — `US-PWRE-9f2c-004_tasks.md` — dependencias: TSK-PWRE-9f2c-012
- Completada: `TSK-PWRE-9f2c-014` — Tests del onboarding MCP — `US-PWRE-9f2c-004_tasks.md` — dependencias: TSK-PWRE-9f2c-012<br>TSK-PWRE-9f2c-013
## US-PWRE-9f2c-005

- Completada: `TSK-PWRE-9f2c-015` — Crear configuración de `agent-dist/skills/quinotospec-review/e2e` — `US-PWRE-9f2c-005_tasks.md` — dependencias: TSK-PWRE-9f2c-010
- Completada: `TSK-PWRE-9f2c-016` — Implementar spec de review visual — `US-PWRE-9f2c-005_tasks.md` — dependencias: TSK-PWRE-9f2c-015<br>TSK-PWRE-9f2c-020<br>TSK-PWRE-9f2c-021
- Completada: `TSK-PWRE-9f2c-017` — Implementar reporter JSON — `US-PWRE-9f2c-005_tasks.md` — dependencias: TSK-PWRE-9f2c-016
- Completada: `TSK-PWRE-9f2c-018` — Crear fixture de propuesta — `US-PWRE-9f2c-005_tasks.md` — dependencias: TSK-PWRE-9f2c-015
- Completada: `TSK-PWRE-9f2c-019` — Integrar suite de review visual — `US-PWRE-9f2c-005_tasks.md` — dependencias: TSK-PWRE-9f2c-005<br>TSK-PWRE-9f2c-016<br>TSK-PWRE-9f2c-018
## US-PWRE-9f2c-006

- Completada: `TSK-PWRE-9f2c-020` — Agregar `data-testid` estables — `US-PWRE-9f2c-006_tasks.md` — dependencias: —
- Completada: `TSK-PWRE-9f2c-021` — Exponer estado observable de Mermaid — `US-PWRE-9f2c-006_tasks.md` — dependencias: TSK-PWRE-9f2c-020
- Completada: `TSK-PWRE-9f2c-022` — Implementar checks BLOCKING y WARN — `US-PWRE-9f2c-006_tasks.md` — dependencias: TSK-PWRE-9f2c-016<br>TSK-PWRE-9f2c-021
- Completada: `TSK-PWRE-9f2c-023` — Verificar regresión de la UI existente — `US-PWRE-9f2c-006_tasks.md` — dependencias: TSK-PWRE-9f2c-020<br>TSK-PWRE-9f2c-021
## US-PWRE-9f2c-007

- Completada: `TSK-PWRE-9f2c-024` — Escribir evidencia JSON y Markdown — `US-PWRE-9f2c-007_tasks.md` — dependencias: TSK-PWRE-9f2c-017
- Completada: `TSK-PWRE-9f2c-025` — Integrar resultado al checklist de review — `US-PWRE-9f2c-007_tasks.md` — dependencias: TSK-PWRE-9f2c-024<br>TSK-PWRE-9f2c-022
- Completada: `TSK-PWRE-9f2c-026` — Aislar screenshots y artefactos — `US-PWRE-9f2c-007_tasks.md` — dependencias: TSK-PWRE-9f2c-024
- Completada: `TSK-PWRE-9f2c-027` — Tests de evidencia y no mutación — `US-PWRE-9f2c-007_tasks.md` — dependencias: TSK-PWRE-9f2c-024<br>TSK-PWRE-9f2c-025<br>TSK-PWRE-9f2c-026
## US-PWRE-9f2c-008

- Completada: `TSK-PWRE-9f2c-028` — Agregar job `ui-playwright` condicionado — `US-PWRE-9f2c-008_tasks.md` — dependencias: TSK-PWRE-9f2c-015<br>TSK-PWRE-9f2c-016<br>TSK-PWRE-9f2c-019
- Completada: `TSK-PWRE-9f2c-029` — Documentar app, MCP y troubleshooting — `US-PWRE-9f2c-008_tasks.md` — dependencias: TSK-PWRE-9f2c-012<br>TSK-PWRE-9f2c-015<br>TSK-PWRE-9f2c-024
- Completada: `TSK-PWRE-9f2c-030` — Actualizar README, arquitectura y manifest — `US-PWRE-9f2c-008_tasks.md` — dependencias: TSK-PWRE-9f2c-001<br>TSK-PWRE-9f2c-029
- Completada: `TSK-PWRE-9f2c-031` — Ejecutar dogfooding y validación completa — `US-PWRE-9f2c-008_tasks.md` — dependencias: TSK-PWRE-9f2c-019<br>TSK-PWRE-9f2c-027<br>TSK-PWRE-9f2c-028<br>TSK-PWRE-9f2c-029<br>TSK-PWRE-9f2c-030
- Completada: `TSK-PWRE-9f2c-032` — Registrar la implementación en changelog — `US-PWRE-9f2c-008_tasks.md` — dependencias: TSK-PWRE-9f2c-031

## Resumen

- Total de tareas: **32**.
- Todas las tareas están en estado `[x]` (completed).
- Orden sugerido: seguir las dependencias y el orden de las historias 001 a 008.
