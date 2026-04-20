---
description: Generar user stories basadas en una propuesta existente
---

Este workflow genera user stories derivadas de una propuesta técnica existente.
Requiere que la propuesta (`proposal.md`) ya haya sido creada.

**Parámetro Requerido:**
- `PROPOSAL_SLUG`: El nombre de la carpeta de la propuesta (ej. `refactor-proposal-workflows`).

**Instrucciones:**
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md`.
2. **Validación previa**: Verifica que el `**Estado:**` de la propuesta NO sea `Archivada`. Si lo es, notifica al usuario y detén el proceso.
3. **Inferencia de roles**: Identifica los roles involucrados a partir del contenido de la propuesta y de `00-stack-profile.md` en el discovery (ej. usuario, admin, sistema, operador). Úsalos en las stories en lugar de `[rol]` genérico.
4. **Cantidad de stories**: Genera una story por cada funcionalidad o cambio sustancial de la propuesta. Ordénalas según las fases del **Plan de Implementación** definido en la propuesta.
5. **Merge inteligente**: Si `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-stories.md` ya existe, **no sobreescribas**. Revisa las stories existentes y realiza un merge: agrega solo las stories nuevas y actualiza las que hayan cambiado.
6. Genera el archivo en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-stories.md` con el siguiente formato:
    - **Título**: User Stories ({{PROPOSAL_NAME}}).
    - Tabla con columnas: ID, User Story, Criterios de Aceptación, Prioridad, Estimación, Servicio.
    - **IDs**: Busca el `**Prefijo:** {{PREFIX}}` en el archivo `proposal.md`. Usa ese prefijo para los IDs: `US-{{PREFIX}}-001`.
    - **Prioridad**: `P1` (alta) / `P2` (media) / `P3` (baja), según la fase y relevancia en la propuesta.
    - **Estimación**: Talla de camiseta (`XS` / `S` / `M` / `L` / `XL`) según la complejidad estimada de la historia.
    - **Servicio**: El sub-proyecto o servicio donde se implementa esta historia, inferido de `**Servicios Afectados:**` en `proposal.md`. Si la historia aplica a todos los servicios, usar `todos`.
    - **Template**:
      ```markdown
      # User Stories ({{PROPOSAL_NAME}})

      | ID | User Story | Criterios de Aceptación | Prioridad | Estimación | Servicio |
      | --- | --- | --- | --- | --- | --- |
      | US-{{PREFIX}}-001 | Como **[rol]**, quiero **[acción]**, para **[beneficio/valor]**. | - [Criterio 1]<br>- [Criterio 2] | P1 | M | auth-service |
      | US-{{PREFIX}}-002 | Como **[rol]**, quiero **[acción]**, para **[beneficio/valor]**. | - [Criterio 1]<br>- [Criterio 2] | P2 | S | user-service |
      ```

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: User Stories Generated: {{PROPOSAL_NAME}}
- **Resumen**: Se generaron user stories para la propuesta '{{PROPOSAL_NAME}}' en .quinoto-spec/proposals/{{PROPOSAL_SLUG}}/
