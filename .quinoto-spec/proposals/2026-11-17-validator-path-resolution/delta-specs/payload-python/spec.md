---
name: Delta Spec — payload-python
---

# Delta Spec: payload-python — validator-path-resolution

**Contract Version:** 1
**Proposal ID:** 2026-11-17-validator-path-resolution
**Propuesta:** Validator Path Resolution
**Prefijo:** VPAT-k4m7
**Fecha de Creación:** 2026-11-17
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Resolución de package root con fallback
`update_agents.py` y `template_resolver.py` SHALL resolver workflows, rules, templates y skills del paquete mediante un helper `resolve_package_root(user_root)` que devuelve `user_root/agent-dist` cuando existe, y en su defecto la raíz de instalación del propio script (`Path(__file__).resolve().parents[2]`), siguiendo la convención de `agent-dist/lib/quinotospec_common.py`.

#### Scenario: ejecución desde proyecto instalado
- **GIVEN** un agente corriendo en un proyecto instalado (sin `agent-dist/`) que invoca `update_agents.py --root .`
- **WHEN** el script resuelve los directorios de workflows/rules/templates
- **THEN** los toma de la raíz de instalación del script y `AGENTS.md` se genera sin errores.

#### Scenario: ejecución desde el repo fuente
- **GIVEN** una ejecución dentro del checkout del paquete
- **WHEN** `root/agent-dist` existe
- **THEN** el comportamiento es idéntico al actual (sin cambio de semántica).

### Requirement: El root del usuario no se altera
El fallback de package root MUST NOT cambiar el significado de `--root`: el root del usuario continúa siendo el proyecto donde se leen/escriben artefactos.

#### Scenario: separación de responsabilidades
- **GIVEN** `update_agents.py --root /proyecto --config /proyecto/.quinoto-spec/config.yaml`
- **WHEN** el script corre con fallback activo
- **THEN** lee config desde `/proyecto/.quinoto-spec/config.yaml` y templates desde la raíz de instalación del script.

---

## MODIFIED Requirements

## REMOVED Requirements

## RENAMED Requirements
