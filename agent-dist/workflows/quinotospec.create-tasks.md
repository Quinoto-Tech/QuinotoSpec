---
description: crea tareas a partir de historias de usuario
---

Este workflow genera un plan de tareas técnicas derivado de una historia de usuario específica.
Requiere que las historias (`user-histories.md`) ya hayan sido creadas.

**Parámetros Requeridos:**
- `PROPOSAL_SLUG`: El nombre de la carpeta de la propuesta (ej. `refactor-proposal-workflows`).
- `USER_STORY_ID`: (Requerido si se usa `--single`) El ID de la historia de usuario objetivo (ej. `US-REF-123`).

**Flags:**
- `--single` `-s`: Genera tareas solo para una historia de usuario específica (contrario al comportamiento por defecto).
- Si no se especifica `--single`, se genera tareas para TODAS las historias de usuario pendientes de la propuesta.

**Instrucciones:**

### Modo Individual (una historia) — Usar `--single`
(Por defecto se procesan todas las historias. Usa `--single` para procesar solo una.)
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
2. Lee también `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` para obtener la **Especificación Técnica Detallada** y la **Arquitectura**, que son críticas para identificar qué archivos, servicios o módulos debe tocar cada tarea.
3. Extrae la historia cuya ID coincida con `{{USER_STORY_ID}}`. Si no existe, fallar con mensaje claro.
4. **Merge inteligente**: Si `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md` ya existe, **no sobreescribas**. Revisa las tareas existentes y realiza un merge: agrega solo las tareas nuevas y actualiza las que hayan cambiado.
5. Basado en ESA única historia, genera un desglose de tareas técnicas en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md`.

### Modo Bulk (todas las historias) — Comportamiento por defecto
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`.
2. Lee también `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` para obtener la **Especificación Técnica Detallada** y la **Arquitectura**.
3. Extrae TODAS las historias de usuario del archivo. Ignora las que ya tienen tareas completadas (marcadas con `[x]` en el archivo de tareas existente).
4. Para cada historia pendiente:
   - **Merge inteligente**: Si `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md` ya existe, NO sobreescribas. Revisa las tareas existentes y realiza un merge: agrega solo las tareas nuevas.
   - Genera el desglose de tareas técnicas en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md`.
5. Genera un archivo consolidado `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/all_tasks.md` que contenga TODAS las tareas de todas las historias (solo si no existe o si se solicita explícitamente).

### Formato de las tareas (aplica a ambos modos)
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

- **Modo Bulk (por defecto, sin flags)**:
  - **Título de la Acción**: Tasks Generated: {{PROPOSAL_NAME}} (All User Stories)
  - **Resumen**: Se generaron tareas para todas las historias de usuario pendientes de la propuesta '{{PROPOSAL_SLUG}}'. Historias procesadas: {{LISTA_DE_US_IDS}}.

- **Modo Single (`--single`)**:
  - **Título de la Acción**: Tasks Generated: {{PROPOSAL_NAME}} ({{USER_STORY_ID}})
  - **Resumen**: Se generó el plan de tareas para la propuesta '{{PROPOSAL_NAME}}', enfocadas en la historia '{{USER_STORY_ID}}'.