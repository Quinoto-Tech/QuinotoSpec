---
date: 2026-09-24
prefix: QSPE-a7f3
slug: g0-1-governance-dispatcher
format: v2
type: change
---

## [2026-09-24] - G0.1: Dispatcher read-only de gobernanza

### Resumen
- Se añadió `rules_enforce.py` como entrypoint ejecutable y read-only para checks observables de contrato, prefijos, changelog, acuerdo de producto, branches, rutas protegidas y configuración crítica.
- La salida JSON distingue `violations`, `blocking` y checks `deferred`; TDD, debug, verify, backup y aprobaciones humanas no se declaran ejecutables.
- `validate-all.sh` y los workflows de CI/release usan el dispatcher sin duplicar la validación del contrato.
- Se añadió una suite sandbox con casos de éxito, bloqueo, aprobación explícita, paths inseguros y garantía read-only.

**Tiempo Ahorrado**: ~4h (IA: ~30min vs Humano: ~4h)
