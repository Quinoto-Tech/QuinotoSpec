---
description: Archiva propuestas, historias de usuario o planes de tareas
---

Este workflow permite archivar elementos de la especificación técnica que han sido completados para limpiar el espacio de trabajo.

### Objetivos:
- **Propuesta completa**: Archiva la carpeta entera de una propuesta.
- **Historias de Usuario**: Archiva el archivo `user-histories.md` de una propuesta.
- **Tareas**: Archiva un archivo de tareas específico (ej. `US-XXX-001_tasks.md`).

**Elemento a archivar:** {{TARGET}} (puede ser un slug de propuesta, un archivo específico o un patrón)

### Instrucciones de Ejecución:

1. **Si el objetivo es una Propuesta (Carpeta):**
    - Localiza `.quinoto-spec/proposals/{{TARGET}}/`.
    - Renombra la carpeta agregando un doble guión bajo: `__${TARGET}`.

2. **Si el objetivo es un Archivo (Historias o Tareas):**
    - Localiza el archivo dentro de su propuesta (ej. `.quinoto-spec/proposals/{{SLUG}}/{{TARGET}}`).
    - Renombra el archivo agregando un doble guión bajo: `__${TARGET}`.
    - Ejemplo: `user-histories.md` -> `__user-histories.md` o `US-AUTH-001_tasks.md` -> `__US-AUTH-001_tasks.md`.

3. **Verificación**:
    - Asegúrate de que los enlaces internos no se rompan o deja una nota de que el archivo ha sido archivado si es necesario.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la acción, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Element Archived: {{TARGET}}
- **Resumen**: Se archivó el elemento '{{TARGET}}' siguiendo la convención de prefijo '__'.