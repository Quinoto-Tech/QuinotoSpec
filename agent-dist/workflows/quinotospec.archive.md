---
description: Archiva propuestas, user stories o planes de tareas
---

# Workflow: Archive

Este workflow permite archivar elementos de la especificación técnica que han sido completados para limpiar el espacio de trabajo.

### Objetivos:
- **Propuesta completa**: Archiva la carpeta entera de una propuesta.
- **User Stories**: Archiva el archivo `user-stories.md` de una propuesta.
- **Tareas**: Archiva un archivo de tareas específico (ej. `US-XXX-001_tasks.md`).

**Elemento a archivar:** `{{TARGET}}` (puede ser un slug de propuesta, un archivo específico o un patrón)

### Instrucciones de Ejecución:

1. **Validación previa (OBLIGATORIA)**:
    - Lee `proposal.md` y verifica que el `**Estado:**` sea `✅ Completada` o equivalente a Done.
    - Si quedan user stories o tareas sin completar (`[ ]` en los archivos de tareas), **advierte al usuario** y detén el proceso a menos que confirme explícitamente continuar.
    - Genera un resumen rápido: cuántas historias y tareas contenía el elemento, cuántas fueron completadas vs pendientes. Documenta esto en el changelog.

2. **Merge de Delta Specs** (solo si la propuesta tiene `delta-specs/`):

   Si el target es una propuesta y existe el directorio `delta-specs/` dentro de ella:

   1. **Por cada dominio en `delta-specs/`:**
      - Determinar archivo target: `.quinoto-spec/specs/{{dominio}}/spec.md`
      - Si NO existe el archivo target:
        - Crear directorio `.quinoto-spec/specs/{{dominio}}/`
        - Crear `spec.md` con header `# Spec: {{dominio}}` y seccion `## Current Requirements`

   2. **Procesar ADDED Requirements:**
      - Leer cada `### Requirement: {{name}}` de la seccion `ADDED Requirements` en `delta-specs/{{dominio}}/spec.md`
      - Para cada uno, append al final de `.quinoto-spec/specs/{{dominio}}/spec.md` con separador `---` antes del bloque

   3. **Procesar MODIFIED Requirements:**
      - Leer cada `### Requirement: {{name}}` de la seccion `MODIFIED Requirements`
      - Buscar el bloque `### Requirement: {{name}}` en el spec target (match por nombre exacto)
      - Si se encuentra: reemplazar el bloque completo (desde `### Requirement:` hasta el siguiente `###` o `---` o EOF)
      - Si NO se encuentra: advertir `⚠️ Requirement '{{name}}' no encontrado en specs/{{dominio}}/spec.md. ¿Agregar como ADDED?`

   4. **Procesar REMOVED Requirements:**
      - Buscar el bloque `### Requirement: {{name}}` en el spec target
      - Si se encuentra: eliminar el bloque completo
      - Si NO se encuentra: advertir `⚠️ Requirement '{{name}}' no encontrado — posiblemente ya fue eliminado`

   5. **Procesar RENAMED Requirements:**
      - Buscar `{{OLD_NAME}}` en el spec target
      - Si se encuentra: renombrar a `{{NEW_NAME}}`
      - Si NO se encuentra: advertir

   6. **Validacion post-merge:**
      - Verificar que no haya requerimientos duplicados en el spec target
      - Mostrar resumen: `Specs mergeados: {{N}} added, {{M}} modified, {{R}} removed, {{X}} renamed en {{D}} dominios`
      - Si hay warnings, mostrarlos antes de continuar

3. **Si el objetivo es una Propuesta (Carpeta):**
    - Localiza `.quinoto-spec/proposals/{{TARGET}}/`.
    - Actualiza el campo `**Estado:**` en `proposal.md` a `🔴 Archivada`.
    - Mueve la carpeta completa a `.quinoto-spec/proposals/_archived/{{TARGET}}/`.
    - En `.quinoto-spec/prefix-registry.md`, mueve la fila del prefijo correspondiente a una sección `## Archivados` al final de la tabla (créala si no existe).

4. **Si el objetivo es un Archivo (Stories o Tareas):**
    - Localiza el archivo dentro de su propuesta (ej. `.quinoto-spec/proposals/{{SLUG}}/{{TARGET}}`)
    - Mueve el archivo a `.quinoto-spec/proposals/{{SLUG}}/_archived/{{TARGET}}`
    - Ejemplo: `user-stories.md` → `_archived/user-stories.md`.

5. **Verificación de referencias internas**:
    - Busca menciones al `{{TARGET}}` o al prefijo usado en otros archivos activos de `.quinoto-spec/`.
    - Si encuentras referencias, añade una nota en esos archivos indicando: `> ⚠️ Este elemento fue archivado. Ver: .quinoto-spec/proposals/_archived/{{TARGET}}`.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la acción, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Element Archived: {{TARGET}}
- **Resumen**: Se archivó '{{TARGET}}' en `.quinoto-spec/proposals/_archived/`. Contenido archivado: [N historias, N tareas — X completadas, Y pendientes].
