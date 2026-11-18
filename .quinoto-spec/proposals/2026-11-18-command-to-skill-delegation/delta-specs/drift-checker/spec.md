---
name: Delta Spec — drift-checker
---

# Delta Spec: drift-checker — command-to-skill-delegation

**Contract Version:** 1
**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Propuesta:** Command-to-Skill Delegation
**Prefijo:** SKDP-m2q8
**Fecha de Creación:** 2026-11-18
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Validación de delegación
`scripts/check-skill-workflow-drift.py` SHALL validar, para cada par workflow↔skill, que el workflow es el stub canónico generado (sin prompt propio), que la skill referenciada existe y no está vacía, y que conserva las referencias a scripts del workflow original.

#### Scenario: prompt duplicado reintroducido
- **GIVEN** un workflow con el cuerpo completo del prompt copiado de nuevo desde la skill
- **WHEN** corre el checker (o `validate-all.sh --strict`)
- **THEN** falla con ERROR identificando el par y el tipo de desviación.

#### Scenario: par sin skill
- **GIVEN** un workflow sin skill pareada
- **WHEN** corre el checker
- **THEN** reporta ERROR (antes las skills huérfanas eran INFO).

### Requirement: Salida y tests actualizados
El checker SHALL conservar su CLI (`--root`, `--json`) y su esquema JSON (`schema_version`, `pairs`, `errors`, `warnings`), y `tests/test-skill-workflow-drift.sh` SHALL verificar la nueva semántica: stub válido, duplicado detectado, skill huérfana detectada.

#### Scenario: gates de CI
- **GIVEN** la suite completa de release
- **WHEN** corre `tests/run-all-tests.sh`
- **THEN** la suite `test-skill-workflow-drift.sh` pasa con 0 errores y los tests de regresión confirman que detecta duplicados deliberados.

---

## MODIFIED Requirements

## REMOVED Requirements

## RENAMED Requirements
