# Workflow Spec — QuinotoSpec

## ADDED Requirements

### Requirement: Specs Gate en Apply
Si existe `.quinoto-spec/specs/<domain>/spec.md`, Apply MUST leerlo y detener el trabajo ante contradicción sin delta-spec.

### Requirement: Specs Gate en Create-Proposal
Propuesta que altere/elimine/renombre un REQUIREMENT vigente MUST registrarlo en `delta-specs/` (MODIFIED/REMOVED/RENAMED) o detenerse.

### Requirement: Fix baseline
`@quinotospec.fix` MUST ejecutar baseline de tests existentes antes de modificar producción.

### Requirement: Constitution Gate
Si existe `.quinoto-spec/constitution.md` con `Estado: active`, Apply MUST verificar principios y detener ante violación.
