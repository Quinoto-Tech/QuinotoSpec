# Acuerdos de Producto y de Trabajo

> **Discovery Date:** 2026-11-08

## Visión de Producto

QuinotoSpec es una metodología + sistema de configuración de agentes para que el desarrollo asistido por IA sea Proposal First, trazable y verificable, sin depender de que el agente “lea AGENTS.md por su cuenta”.

## Business Goals / KPIs

- % de cambios que pasan por propuesta antes de código (objetivo >80% en dogfooding).
- 0 regresiones por falta de validación en releases (medido por `validate-all.sh --strict` + suites verdes).
- Tiempo medio propuesta → archive < 14 días.
- Adopción: nº de proyectos con `.quinoto-spec/` activo y `contract validate --strict` en verde.

## Definition of Ready (DoR)

- Discovery fresco (<30 días) y `08-product-and-agreements.md` sin placeholders.
- `contract.py validate --root . --strict` en verde.
- Prefijo registrado en `prefix-registry.md`.
- Propuesta con `**ID:**`, `**Prefijo:**`, `**Fecha de Creación:**`, `**Estado:**`, `**Prioridad:**`, `**Complejidad:**`, `**Servicios Afectados:**`.

## Definition of Done (DoD)

- Gates mecánicos en verde: TDD (si aplica), evidencia fresca (`evidence_validate.py`), `verify-before-done`.
- Tests, lint y typecheck del stack (`01-stack-profile.md`) en verde.
- Changelog v2 append-only con `quinotospec-update-changelog`.
- `Norns --check` sin drift; `validate-all.sh --strict` + `run-all-tests.sh` en verde.
- Marcas: UI *(en desarrollo)* donde aplique hasta promoción a `beta`.
