---
description: aplicar la tarea correspondiente
---

[INSTRUCCIÓN MAESTRA]
Debes ejecutar la tarea técnica especificada por el usuario y documentar EXACTAMENTE los cambios realizados en el archivo de registro.

**Tarea a realizar:**
{{TASK_DESCRIPTION}}

**Contexto Global OBLIGATORIO:**
Antes de realizar cualquier cambio:
1. Lee `.quinoto-spec/discovery/` para comprender el estado actual del proyecto.
2. Lee `.quinoto-spec/proposals/` para alinear tu código con las propuestas técnicas aprobadas.
3. Asegúrate de que esta tarea contribuya coherentemente a la arquitectura global.

**Instrucciones de Ejecución:**
1. Genera un branch feature/{{TASK_DESCRIPTION}} con generate_github_branch
2. Analiza el código actual y realiza los cambios necesarios para cumplir con la tarea descrita.
3. Verifica que el código modificado compile/funcione (si aplica).

**Instrucciones de Documentación (Changelog):**
Una vez aplicados los cambios, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Tarea: {{TASK_DESCRIPTION}}
- **Resumen**: 
  - [Listar archivos modificados]
  - Resumen técnico de la solución implementada.

IMPORTANTE: El paso de documentación es OBLIGATORIO. No termines la ejecución sin escribir en el changelog.

Verifica estado de las Tareas, Historias y Propuestas -- Mark Done Skill