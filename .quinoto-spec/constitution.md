---
name: Constitution — QuinotoSpec Package Dogfooding
---

# Constitución del Proyecto — quinotospec-package

> **Versión:** 1.0.0
> **Fecha:** 2026-11-08
> **Stack:** bash 4+, python3 3.8+, Node.js (opcional), OpenCode v1/v2
> **Owner:** Quinoto-Tech
> **Estado:** active

Esta constitución define decisiones de arquitectura e implementación del propio paquete QuinotoSpec. No deroga reglas globales (`agent-dist/rules/quinotospec-rules.md`) ni gates de TDD/verify; solo añade restricciones más estrictas. Todos los workflows deben revisar sus principios antes de Apply/Review/Archive.

---

## Principios Fundamentales

### I. Calidad de Código

- **CODE-01:** Todo cambio en `agent-dist/` debe ser validado con `scripts/validate-all.sh --strict` y `tests/run-all-tests.sh` antes de commit/push.
- **CODE-02:** Preferir stdlib-only en Python; ninguna dependencia externa salvo `static/mermaid.min.js` vendida (3.2M) y cargada lazy.

### II. Estándares de Testing

- **TEST-01:** Cada feature nueva (UI, specs gate, fix baseline, gates) debe tener suite `tests/test-*.sh` o extender existente; `run-all-tests.sh` debe ejecutar todas.
- **TEST-02:** Evidencia fresca TDD/debug/verify (`evidence_validate.py --kind ... --require`) antes de Mark Done.

### III. Consistencia de UX

- **UX-01:** UI read-only — nunca escribe en `.quinoto-spec/`; consumir vía `readers.py`.
- **UX-02:** Toda página nueva de UI debe tener fallback sin JS (Markdown renderizado server-side).

### IV. Requisitos de Performance

- **PERF-01:** UI debe servir en <2s en localhost; Mermaid lazy, no bloqueante.
- **PERF-02:** `server.py --json` debe responder sin levantar HTTP.

### V. Gobernanza y Specs

- **GOV-01:** Toda tarea que contradiga un spec vigente requiere delta-spec (ADDED/MODIFIED/REMOVED) o aprobación explícita.
- **GOV-02:** `manifest.json` y `Norns --check` sin drift antes de release; bump de versión via `scripts/update-version.sh`.

---

## Gates

- **CONSTITUTION_GATE**: `constitution_validate.py --root . --json` debe reportar `valid: true` en Apply/Review/Archive si `Estado: active`.
- **SPECS_GATE**: Apply debe leer `.quinoto-spec/specs/<domain>/spec.md` y registrar alineación en evidencia.
