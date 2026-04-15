---
description: Archiva propuestas, historias de usuario o planes de tareas
---

Este workflow permite archivar elementos de la especificación técnica que han sido completados para limpiar el espacio de trabajo.

### Objetivos:
- **Propuesta completa**: Archiva la carpeta entera de una propuesta.
- **Historias de Usuario**: Archiva el archivo `user-histories.md` de una propuesta.
- **Tareas**: Archiva un archivo de tareas específico (ej. `US-XXX-001_tasks.md`).

**Elemento a archivar:** `{{TARGET}}` (puede ser un slug de propuesta, un archivo específico o un patrón)

### Instrucciones de Ejecución:

1. **Validación previa (OBLIGATORIA)**:
    - Lee `proposal.md` y verifica que el `**Estado:**` sea `✅ Completada` o equivalente a Done.
    - Si quedan historias o tareas sin completar (`[ ]` en los archivos de tareas), **advierte al usuario** y detén el proceso a menos que confirme explícitamente continuar.
    - Genera un resumen rápido: cuántas historias y tareas contenía el elemento, cuántas fueron completadas vs pendientes. Documenta esto en el changelog.

2. **Si el objetivo es una Propuesta (Carpeta):**
    - Localiza `.quinoto-spec/proposals/{{TARGET}}/`.
    - Actualiza el campo `**Estado:**` en `proposal.md` a `🔴 Archivada`.
    - Mueve la carpeta completa a `.quinoto-spec/proposals/_archived/{{TARGET}}/`.
    - En `.quinoto-spec/prefix-registry.md`, mueve la fila del prefijo correspondiente a una sección `## Archivados` al final de la tabla (créala si no existe).

3. **Si el objetivo es un Archivo (Historias o Tareas):**
    - Localiza el archivo dentro de su propuesta (ej. `.quinoto-spec/proposals/{{SLUG}}/{{TARGET}}`).
    - Mueve el archivo a `.quinoto-spec/proposals/{{SLUG}}/_archived/{{TARGET}}`.
    - Ejemplo: `user-histories.md` → `_archived/user-histories.md`.

4. **Verificación de referencias internas**:
    - Busca menciones al `{{TARGET}}` o al prefijo usado en otros archivos activos de `.quinoto-spec/`.
    - Si encuentras referencias, añade una nota en esos archivos indicando: `> ⚠️ Este elemento fue archivado. Ver: .quinoto-spec/proposals/_archived/{{TARGET}}`.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la acción, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Element Archived: {{TARGET}}
- **Resumen**: Se archivó '{{TARGET}}' en `.quinoto-spec/proposals/_archived/`. Contenido archivado: [N historias, N tareas — X completadas, Y pendientes].