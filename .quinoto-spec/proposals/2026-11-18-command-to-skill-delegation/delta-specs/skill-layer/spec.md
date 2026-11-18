---
name: Delta Spec — skill-layer
---

# Delta Spec: skill-layer — command-to-skill-delegation

**Contract Version:** 1
**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Propuesta:** Command-to-Skill Delegation
**Prefijo:** SKDP-m2q8
**Fecha de Creación:** 2026-11-18
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Skill como fuente de verdad del prompt
Cada skill pareada SHALL contener el prompt completo del workflow que antes duplicaba: secciones, gates, parámetros y referencias a scripts ejecutables. Ningún comando SHALL conservar una copia de ese contenido.

#### Scenario: cambio de proceso
- **GIVEN** una regla de gobernanza que cambia (p. ej., gate Goldfish)
- **WHEN** se actualiza el prompt
- **THEN** se edita una sola vez, en el SKILL.md, y el comando hereda el cambio sin edits adicionales.

### Requirement: Consolidación previa de skills resumidas
Antes de convertir su comando, las skills actualmente resumidas (`flow`, `constitution`, `agent-config`, `review-handoff`, `help`, `ui`, `quick-dev`, `preset-install`, `update-agents`, `extension-install`) SHALL incorporar todo el contenido funcional presente en su workflow (inventario comparado por headings H2 y referencias a `*.py|sh|js`).

#### Scenario: par con similitud baja
- **GIVEN** el par `flow` (similitud 0.18) cuyo workflow es un orquestador con gates entre fases
- **WHEN** se consolida y se convierte el comando
- **THEN** la skill contiene todas las fases, gates y snapshots de paridad que el workflow original tenía; la ejecución del comando no pierde capacidades.

#### Scenario: par review con propuesta activa
- **GIVEN** PWRE-9f2c aún En Curso sobre `review-workflow`
- **WHEN** se alcanza el par `review` en la conversión
- **THEN** se revalida su contenido contra los cambios de PWRE; si continúa activa, se excluye temporalmente y se registra la deuda.

### Requirement: Documentación de fuente de verdad
La cabecera de cada SKILL.md y la documentación del paquete SHALL declarar la skill como fuente de verdad del prompt, sustituyendo las referencias actuales a "workflow como fuente de verdad; skill a sincronizar".

---

## MODIFIED Requirements

## REMOVED Requirements

## RENAMED Requirements
