---
name: Delta Spec — payload-documentacion
---

# Delta Spec: payload-documentacion — validator-path-resolution

**Contract Version:** 1
**Proposal ID:** 2026-11-17-validator-path-resolution
**Propuesta:** Validator Path Resolution
**Prefijo:** VPAT-k4m7
**Fecha de Creación:** 2026-11-17
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Invariant de distribución de docs
Todo `.md` distribuido e instalado (workflows/commands, skills, rules, bootstrap, templates, agents) SHALL referenciar los comandos del paquete con rutas ejecutables en el destino de instalación; en particular, MUST NOT contener referencias a `agent-dist/` que no resuelvan en el destino.

#### Scenario: preflight del bootstrap ejecutable
- **GIVEN** una instalación global completada
- **WHEN** un agente copia el comando de preflight del bootstrap instalado tal cual
- **THEN** el comando existe en disco y `contract.py validate --root . --strict` corre con exit 0 en un proyecto arbitrario.

#### Scenario: regresión protegida
- **GIVEN** el suite `tests/test-installed-paths.sh`
- **WHEN** un cambio futuro reintroduce `agent-dist/` en un `.md` del payload
- **THEN** el test falla antes de llegar a release (`smoke-release.sh` incluye la aserción).

---

## MODIFIED Requirements

## REMOVED Requirements

## RENAMED Requirements
