# Delta Spec — review

## ADDED Requirements

### Requirement: Revisión con contexto aislado
El sistema MUST permitir revisar una propuesta con subagentes aislados (contexto limpio) que no compartan el hilo del agente redactor, y MUST fallar explícitamente si no puede crearlos.

#### Scenario: Subagentes no disponibles
- **GIVEN** un IDE que no permite subagentes frescos
- **WHEN** se invoca `@quinotospec.goldfish-review`
- **THEN** el workflow se detiene y reporta el límite, sin simular una revisión.

### Requirement: Pipeline de cinco etapas
La revisión Goldfish MUST ejecutar Comprehension, Design Critic, Zoom Out, Implementation Readiness y Synthesis, y MUST escribir `review-findings.md` deduplicado.

### Requirement: Implementation Readiness Gate
Antes de Apply, el sistema MUST validar que la propuesta/tareas declaren archivos objetivo, comandos de test y criterios de aceptación; MUST detener Apply si faltan con `--require`.

## MODIFIED Requirements

### Requirement: Review existente
`@quinotospec.review` MUST seguir disponible; Goldfish es una capa opcional que no lo reemplaza.

## REMOVED Requirements

(Ninguno)
