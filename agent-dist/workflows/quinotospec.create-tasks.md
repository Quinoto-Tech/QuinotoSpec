---
description: crea tareas a partir de historias de usuario
---

Este workflow genera un plan de tareas técnicas derivado de una historia de usuario específica.
Requiere que las historias (`user-histories.md`) ya hayan sido creadas.

**Parámetros Requeridos:**
- `PROPOSAL_SLUG`: El nombre de la carpeta de la propuesta (ej. `refactor-proposal-workflows`).
- `USER_STORY_ID`: El ID de la historia de usuario objetivo (ej. `US-REF-123`).

**Instrucciones:**
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
2. Lee también `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` para obtener la **Especificación Técnica Detallada** y la **Arquitectura**, que son críticas para identificar qué archivos, servicios o módulos debe tocar cada tarea.
3. Extrae la historia cuya ID coincida con `{{USER_STORY_ID}}`. Si no existe, fallar con mensaje claro.
4. **Merge inteligente**: Si `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md` ya existe, **no sobreescribas**. Revisa las tareas existentes y realiza un merge: agrega solo las tareas nuevas y actualiza las que hayan cambiado.
5. Basado en ESA única historia, genera un desglose de tareas técnicas en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md`.
6. El formato de las tareas debe ser:
    - **Título**: Plan de Tareas ({{PROPOSAL_NAME}} — {{USER_STORY_ID}}).
    - Tabla con columnas: ID, Tipo, Título, Descripción, Historia Relacionada, Servicio, Archivos a Modificar, Estimación, Prioridad, Dependencias.
    - **IDs**: Extrae el prefijo de la historia de usuario (ej. si la historia es `US-{{PREFIX}}-XXX`) y úsalo para las tareas: `TSK-{{PREFIX}}-001`, `TSK-{{PREFIX}}-002`, etc.
    - **Tipo**: Clasifica cada tarea según el tipo de trabajo: `Backend` | `Frontend` | `DB` | `Test` | `DevOps` | `Config`.
    - **Historia Relacionada**: DEBE enlazar explícitamente al ID de la historia correspondiente (`{{USER_STORY_ID}}`).
    - **Servicio**: Heredar el valor de la columna `Servicio` de la historia de usuario en `user-histories.md`. Indica en qué sub-proyecto/repositorio se ejecuta la tarea.
    - **Archivos a Modificar**: Lista los archivos del repo que se espera crear, modificar o eliminar para completar la tarea (inferir desde la propuesta y el stack).
    - **Prioridad**: `P1` (alta) / `P2` (media) / `P3` (baja) según relevancia para cumplir los criterios de aceptación.
    - **Estimación**: Talla de camiseta (`XS` / `S` / `M` / `L` / `XL`) según complejidad técnica.

**Notas de generación:**
- Solo genera tareas relacionadas directamente con la historia especificada; no incluyas tareas globales ni de documentación genérica.
- Si la historia contiene criterios de aceptación numerados, mapea cada criterio a una tarea separada cuando tenga sentido.
- **Sí genera** tareas de tipo `Test` cuando los criterios de aceptación (DoD) requieran cobertura de pruebas automatizadas.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Tasks Generated: {{PROPOSAL_NAME}} ({{USER_STORY_ID}})
- **Resumen**: Se generó el plan de tareas para la propuesta '{{PROPOSAL_NAME}}', enfocadas en la historia '{{USER_STORY_ID}}', en .quinoto-spec/proposals/{{PROPOSAL_SLUG}}/