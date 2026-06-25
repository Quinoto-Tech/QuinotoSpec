---
name: Delta Spec Template
description: Template para generar archivos delta-spec con secciones ADDED/MODIFIED/REMOVED/RENAMED
---

# Delta Spec: {{DOMAIN}} — {{PROPOSAL_SLUG}}

> **Propuesta:** {{PROPOSAL_NAME}}
> **Prefijo:** {{PREFIX}}
> **Fecha:** {{DATE}}
> **Estado:** 🟡 Propuesta

---

## ADDED Requirements

<!--
  Nuevos requerimientos que esta propuesta introduce.
  Usa SHALL/MUST para requisitos normativos, SHOULD para recomendaciones.
  GIVEN/WHEN/THEN es opcional.
-->

### Requirement: {{REQUIREMENT_NAME}}
The system SHALL {{requirement}}.

#### Scenario: {{scenario_name}} (optional)
- **GIVEN** {{precondition}}
- **WHEN** {{action}}
- **THEN** {{expected_outcome}}

---

## MODIFIED Requirements

<!--
  Requerimientos existentes que cambian.
  Inclui siempre Was: (texto anterior) y Reason: (motivo del cambio).
  Si no existe specs/ aun, esta seccion queda vacia.
-->

### Requirement: {{REQUIREMENT_NAME}}
{{new_requirement_text}}

**Was:** {{old_requirement_text}}
**Reason:** {{why_this_changed}}

---

## REMOVED Requirements

<!--
  Requerimientos que se eliminan.
  Inclui siempre Reason: (motivo) y Migration: (como manejar la eliminacion).
-->

### Requirement: {{REQUIREMENT_NAME}}
**Reason:** {{why_removed}}
**Migration:** {{how_to_handle — affected endpoints, data, configs, users}}

---

## RENAMED Requirements

<!--
  Requerimientos cuyo nombre cambia (el contenido puede cambiar tambien via MODIFIED).
-->

### Requirement: {{OLD_NAME}} → {{NEW_NAME}}
**Reason:** {{why_renamed}}

---

## Usage Notes

### Formato de Requerimientos
- `SHALL` / `MUST`: obligatorio, normativo
- `SHOULD`: recomendacion fuerte
- `MAY`: opcional, a discrecion

### Escenarios GIVEN/WHEN/THEN
- Opcionales. Si el usuario no los pide, no los fuerces.
- Si se incluyen, cada `### Requirement:` puede tener 1+ escenarios.
- Un escenario prueba UN solo comportamiento.

### Reglas de Bloque
- Cada `### Requirement: {{name}}` es un bloque atomico.
- El engine de merge opera a nivel de bloque (busca por nombre exacto).
- MODIFIED reemplaza el bloque completo.
- REMOVED elimina el bloque completo.

### Sin Cambios en un Dominio
- Si un dominio no tiene cambios, no crear archivo spec para ese dominio.
- Solo crear `delta-specs/<dominio>/spec.md` si hay al menos un ADDED, MODIFIED, REMOVED o RENAMED.
