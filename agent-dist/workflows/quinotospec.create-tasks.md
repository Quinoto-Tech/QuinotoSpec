---
description: crea tareas a partir de user stories o desde un RFC (create-rfc)
---

Este workflow genera un plan de tareas técnicas derivado de user stories.

**Dos orígenes de contexto (usa uno u otro, no ambos):**

| Origen | Requisito | Carpeta de trabajo |
|--------|-----------|-------------------|
| **Propuesta** (modo clásico) | `user-stories.md` bajo la propuesta | `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/` |
| **RFC** (`--from-rfc`) | RFC generado por `quinotospec.create-rfc` con la seccion `## User Stories (entrada para create-tasks)` | `.quinoto-spec/rfc/{{RFC_STEM}}/` |

**Parámetros Requeridos:**

- **Modo propuesta (por defecto):** `PROPOSAL_SLUG` — nombre de la carpeta de la propuesta (ej. `refactor-proposal-workflows`).
- **Modo RFC:** `--from-rfc` + `RFC_PATH` — ruta al archivo Markdown del RFC (ej. `.quinoto-spec/rfc/RFC-20260427-mi-slug-mi-feature.md`). En este modo **no** uses `PROPOSAL_SLUG`.
- `USER_STORY_ID`: (Requerido si se usa `--single`) El ID de la user story objetivo (ej. `US-AUTH-a1b2-001`).

**Flags:**

- `--from-rfc <RFC_PATH>`: Lee el RFC y la tabla de historias incrustada; escribe tareas bajo `.quinoto-spec/rfc/{{RFC_STEM}}/`. `RFC_STEM` = nombre del archivo del RFC **sin** extension `.md`.
- `--single` `-s`: Genera tareas solo para una user story específica (contrario al comportamiento por defecto).
- Si no se especifica `--single`, se genera tareas para TODAS las user stories pendientes del origen activo (propuesta o RFC).

**Instrucciones:**

### Modo RFC (`--from-rfc`) — Tareas desde un RFC

Usar cuando el plan de valor ya esta descrito en el RFC (flujo `quinotospec.create-rfc`) y no hace falta una carpeta de propuesta todavia.

1. Resolver y leer `RFC_PATH` (ruta absoluta o relativa a la raiz del repo).
2. Calcular `RFC_STEM`: nombre del archivo sin `.md` (ej. `RFC-20260427-mi-slug` → stem igual al basename completo).
3. Definir `RFC_BUNDLE_DIR` = `.quinoto-spec/rfc/{{RFC_STEM}}/`. Si no existe, crearlo.
4. Localizar en el RFC el heading **exacto** `## User Stories (entrada para create-tasks)`.
   - Si no existe: **detener** con mensaje claro: completar esa seccion segun `quinotospec.create-rfc` o copiar el formato de `quinotospec.create-user-stories`.
5. Debajo del heading, parsear:
   - La linea `**Prefijo (QuinotoSpec):**` (aceptar tambien `**Prefijo:**` si el contenido es el mismo formato MNEM-xxxx).
   - La tabla markdown (columnas: ID, User Story, Criterios de Aceptacion, Prioridad, Estimacion, Servicio).
6. **Materializar user stories en el bundle (merge inteligente):**
   - Archivo objetivo: `{{RFC_BUNDLE_DIR}}/user-stories.md`.
   - Si **no** existe: crearlo con titulo `User Stories (RFC: {{RFC_STEM}})` y el cuerpo de tabla parseada (mismo formato que en modo propuesta).
   - Si **ya** existe: **no sobreescribas**; haz merge como en modo propuesta (agregar/actualizar filas segun la tabla del RFC).
7. **Contexto tecnico sustituto de `proposal.md`:** usar el **texto completo del RFC** como fuente principal, priorizando secciones de propuesta tecnica, impacto, plan de implementacion, riesgos, pruebas y "Proposal Seed" si estan presentes.
8. A partir de aqui, aplica **la misma logica** que en Modo Individual o Modo Bulk, pero sustituyendo siempre:
   - `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/` → `{{RFC_BUNDLE_DIR}}/`
   - `PROPOSAL_NAME` → titulo del RFC (primer `#` del documento, o `TITLE` del template, o `RFC_STEM` si no hay titulo claro).
9. **Archivo consolidado opcional:** `{{RFC_BUNDLE_DIR}}/all_tasks.md` con la misma regla que en modo bulk (solo si no existe o si el usuario lo pide).

### Modo Individual (una story) — Usar `--single`
Solo aplica cuando **no** se uso `--from-rfc` (en modo RFC, los mismos pasos se aplican con `{{RFC_BUNDLE_DIR}}` segun la seccion anterior).

(Por defecto se procesan todas las stories. Usa `--single` para procesar solo una.)
1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-stories.md`.
2. Lee también `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` para obtener la **Especificación Técnica Detallada** y la **Arquitectura**, que son críticas para identificar qué archivos, servicios o módulos debe tocar cada tarea.
3. Extrae la historia cuya ID coincida con `{{USER_STORY_ID}}`. Si no existe, fallar con mensaje claro.
4. **Merge inteligente**: Si `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md` ya existe, **no sobreescribas**. Revisa las tareas existentes y realiza un merge: agrega solo las tareas nuevas y actualiza las que hayan cambiado.
5. Basado en ESA única historia, genera un desglose de tareas técnicas en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md`.

### Modo Bulk (todas las stories) — Comportamiento por defecto
Solo aplica cuando **no** se uso `--from-rfc` (en modo RFC, equivalente con `{{RFC_BUNDLE_DIR}}`).

1. Lee el archivo `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-stories.md`.
2. Lee también `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` para obtener la **Especificación Técnica Detallada** y la **Arquitectura**.
3. Extrae TODAS las user stories del archivo. Ignora las que ya tienen tareas completadas (marcadas con `[x]` en el archivo de tareas existente).
4. Para cada historia pendiente:
   - **Merge inteligente**: Si `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md` ya existe, NO sobreescribas. Revisa las tareas existentes y realiza un merge: agrega solo las tareas nuevas.
   - Genera el desglose de tareas técnicas en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{USER_STORY_ID}}_tasks.md`.
5. Genera un archivo consolidado `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/all_tasks.md` que contenga TODAS las tareas de todas las historias (solo si no existe o si se solicita explícitamente).

### Formato de las tareas (aplica a modo propuesta y a modo `--from-rfc`)
    - **Título**: Plan de Tareas ({{PROPOSAL_NAME}} — {{USER_STORY_ID}}).
    - Tabla con columnas: ID, Tipo, Título, Descripción, Historia Relacionada, Servicio, Archivos a Modificar, Estimación, Prioridad, Dependencias.
    - **IDs**: Extrae el prefijo de la user story (ej. si la story es `US-{{PREFIX}}-XXX`) y úsalo para las tareas: `TSK-{{PREFIX}}-001`, `TSK-{{PREFIX}}-002`, etc.
    - **Tipo**: Clasifica cada tarea según el tipo de trabajo: `Backend` | `Frontend` | `DB` | `Test` | `DevOps` | `Config`.
    - **Story Relacionada**: DEBE enlazar explícitamente al ID de la story correspondiente (`{{USER_STORY_ID}}`).
    - **Servicio**: Heredar el valor de la columna `Servicio` de la user story en `user-stories.md`. Indica en qué sub-proyecto/repositorio se ejecuta la tarea.
    - **Archivos a Modificar**: Lista los archivos del repo que se espera crear, modificar o eliminar para completar la tarea (inferir desde `proposal.md` y el stack, o desde el RFC completo en modo `--from-rfc`).
    - **Prioridad**: `P1` (alta) / `P2` (media) / `P3` (baja) según relevancia para cumplir los criterios de aceptación.
    - **Estimación**: Talla de camiseta (`XS` / `S` / `M` / `L` / `XL`) según complejidad técnica.

**Notas de generación:**
- Solo genera tareas relacionadas directamente con la historia especificada; no incluyas tareas globales ni de documentación genérica.
- Si la historia contiene criterios de aceptación numerados, mapea cada criterio a una tarea separada cuando tenga sentido.
- **Sí genera** tareas de tipo `Test` cuando los criterios de aceptación (DoD) requieran cobertura de pruebas automatizadas.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.

- **Modo Bulk (por defecto, sin flags)** — propuesta:
  - **Título de la Acción**: Tasks Generated: {{PROPOSAL_NAME}} (All User Stories)
  - **Resumen**: Se generaron tareas para todas las user stories pendientes de la propuesta '{{PROPOSAL_SLUG}}'. User stories procesadas: {{LISTA_DE_US_IDS}}.

- **Modo Single (`--single`)** — propuesta:
  - **Título de la Acción**: Tasks Generated: {{PROPOSAL_NAME}} ({{USER_STORY_ID}})
  - **Resumen**: Se generó el plan de tareas para la propuesta '{{PROPOSAL_NAME}}', enfocadas en la historia '{{USER_STORY_ID}}'.

- **Modo Bulk con `--from-rfc`**:
  - **Título de la Acción**: Tasks Generated from RFC: {{RFC_STEM}} (All User Stories)
  - **Resumen**: Se generaron tareas desde el RFC '{{RFC_PATH}}' en '{{RFC_BUNDLE_DIR}}'. User stories procesadas: {{LISTA_DE_US_IDS}}.

- **Modo Single con `--from-rfc` y `--single`**:
  - **Título de la Acción**: Tasks Generated from RFC: {{RFC_STEM}} ({{USER_STORY_ID}})
  - **Resumen**: Se generó el plan de tareas desde el RFC '{{RFC_PATH}}' para la historia '{{USER_STORY_ID}}' en '{{RFC_BUNDLE_DIR}}'.