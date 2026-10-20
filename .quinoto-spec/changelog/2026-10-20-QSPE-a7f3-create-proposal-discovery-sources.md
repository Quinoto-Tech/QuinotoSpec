---
date: 2026-10-20
prefix: QSPE-a7f3
slug: create-proposal-discovery-sources
format: v2
type: fix
---

## [2026-10-20] - Fix: create-proposal no leía el discovery técnico (02–07)

### Resumen
- **Causa raíz**: `agent-dist/skills/quinotospec-create-proposal/SKILL.md` pedía "atención especial" a `01-stack-profile.md` y `08-product-and-agreements.md`, y el único `Read` explícito con gate bloqueante era el `08`. Ninguna instrucción mapeaba `02`–`07` a las secciones técnicas de la propuesta, así que el agente los omitía y las propuestas nacían sin arquitectura, endpoints, modelos de datos, CI ni deuda técnica.
- **Solución**: nuevo paso **"Lectura dirigida del Discovery"** con tabla `sección de proposal.md → archivo de discovery` (`02` overview, `03` architecture, `04` endpoints, `05` data/services, `06` devops/ci/security, `07` findings) y cuatro reglas: citar hallazgos concretos; declarar supuestos sin inventar endpoints/tablas/pipelines; no bloquear cuando falten `02`–`07` (solo `08` es bloqueante); leer `specs/{dominio}/spec.md` junto con `04`/`05` para habilitar `MODIFIED`/`REMOVED` en delta-specs.
- **Archivos**:
  - `agent-dist/skills/quinotospec-create-proposal/SKILL.md` — [modificado] — bloque de fuentes del discovery por sección.
  - `agent-dist/workflows/quinotospec.create-proposal.md` — [modificado] — mismo bloque, espejo del workflow (cuerpos sincronizados).
  - `tests/test-discovery-sources.sh` — [nuevo] — regresión que exige el bloque y las seis referencias en skill y workflow.
  - `tests/run-all-tests.sh` — [modificado] — registro de la nueva suite.
- **Tests**: RED 16 fallos → GREEN 0 errores. `bash scripts/validate-all.sh --allow-no-node`: 0 errores, 0 warnings, 22/22 suites.

**Tiempo Ahorrado**: ~30 min (IA: 6 min vs Humano: 30 min)
