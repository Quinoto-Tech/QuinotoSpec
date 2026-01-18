---
description: Generar historias de usuario basadas en una propuesta existente
---

Este workflow genera historias de usuario derivadas de una propuesta técnica existente.
Requiere que la propuesta (`proposal.md`) ya haya sido creada.

**Parámetro Requerido:**
- `PROPOSAL_SLUG`: El nombre de la carpeta de la propuesta (ej. `refactor-proposal-workflows`).

**Instrucciones:**
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md`.
2. Basado en el contenido de la propuesta, genera una lista de Historias de Usuario en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
3. El formato de las historias debe ser:
    - **Título**: Historias de Usuario ({{PROPOSAL_NAME}}).
    - Tabla con columnas: ID, Historia de Usuario, Criterios de Aceptación.
    - **IDs**: Busca el `**Prefijo:** {{PREFIX}}` en el archivo `proposal.md`. Usa ese prefijo para los IDs: `US-{{PREFIX}}-001`.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: User Histories Generated: {{PROPOSAL_NAME}}
- **Resumen**: Se generaron historias de usuario para la propuesta '{{PROPOSAL_NAME}}' en .quinoto-spec/proposals/{{PROPOSAL_SLUG}}/
