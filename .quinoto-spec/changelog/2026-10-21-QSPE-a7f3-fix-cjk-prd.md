---
date: 2026-10-21
prefix: QSPE-a7f3
slug: fix-cjk-prd
format: v2
type: fix
---

## [2026-10-21] - Fix: caracteres chinos en el skill y workflow de create-prd

### Resumen
- **Causa raíz**: la plantilla del PRD arrastraba dos fragmentos sin traducir (`陈述` = "declaración" y `功能` = "funcionalidad"), probablemente por copiar una plantilla traducida al chino y reemplazar solo parte del texto.
- **Solución**: `**陈述 del Problema**` → `**Declaración del Problema**` y `[功能]` → `[funcionalidad]` en `QUIERO`.
- **Archivos**:
  - `agent-dist/skills/quinotospec-create-prd/SKILL.md` — [modificado] — dos líneas corregidas (Problem Statement y User Stories).
  - `agent-dist/workflows/quinotospec.create-prd.md` — [modificado] — mismas dos líneas (espejo del workflow).
  - `tests/test-encoding.sh` — [nuevo] — regresión que falla si aparece cualquier carácter Han, kana o fullwidth en `agent-dist/` y `docs/`.
  - `tests/run-all-tests.sh` — [modificado] — registro de la suite `Encoding (sin CJK)`.
- **Tests**: RED 4 ocurrencias → GREEN 0. `bash scripts/validate-all.sh --allow-no-node`: 0 errores, 0 warnings, 23/23 suites.

**Tiempo Ahorrado**: ~15 min (IA: 4 min vs Humano: 15 min)

**Nota de auditoría**: el barrido completo del repo no encontró otros caracteres CJK fuera de esos dos archivos.
