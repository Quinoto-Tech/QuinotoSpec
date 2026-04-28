---
description: Revisa un branch o PR contra los criterios de aceptación de la tarea y la propuesta correspondiente
---

Este workflow guía al agente para realizar una revisión técnica de código antes de mergear, validando contra los criterios definidos en la especificación.

**Parámetros Requeridos:**
- `TASK_ID`: El ID de la tarea técnica asociada al branch (ej. `TSK-AUTH-001`).
- `BRANCH_NAME`: El nombre del branch a revisar (ej. `feature/TSK-AUTH-001-add-login`).

**Instrucciones:**

1. **Contexto de la revisión**:
    - Lee el archivo de tareas correspondiente al `{{TASK_ID}}` en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md`.
    - Lee la propuesta en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md`, en especial las secciones de **Criterios de Aceptación (DoD)** y **Especificación Técnica Detallada**.
    - Lee `00-stack-profile.md` para conocer los estándares de código del proyecto.

2. **Análisis del branch**:
    - Obtén el diff del branch contra la rama base:
      ```bash
      git diff main...{{BRANCH_NAME}}
      ```
    - Lista los archivos modificados:
      ```bash
      git diff --name-only main...{{BRANCH_NAME}}
      ```

3. **Checklist de revisión**:
    Valida cada uno de los siguientes puntos y documenta el resultado (✅ / ❌ / ⚠️):

    - [ ] **Criterios de Aceptación (DoD)**: ¿Cada criterio definido en la tarea está cubierto por el código?
    - [ ] **Cobertura de tests**: ¿Se agregaron tests para la lógica nueva? ¿Pasan correctamente?
    - [ ] **Convenciones del stack**: ¿El código sigue los patrones detectados en `00-stack-profile.md`?
    - [ ] **Archivos declarados**: ¿Los archivos modificados coinciden con los declarados en la columna "Archivos a Modificar" de la tarea?
    - [ ] **Sin regresiones**: ¿La suite de tests completa pasa sin errores?
    - [ ] **Sin deuda técnica obvia**: ¿No hay TODOs sin resolver, console.logs, o código comentado que no debería estar?

4. **Resultado de la revisión**:
    - Si todos los puntos son ✅ → el branch está listo para mergear. Notificar al usuario.
    - Si hay ❌ o ⚠️ → generar un informe detallado de los puntos a corregir antes de mergear.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la revisión, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Code Review: {{TASK_ID}}
- **Resumen**: Se revisó el branch '{{BRANCH_NAME}}'. Resultado: [Aprobado / Requiere Cambios]. Puntos pendientes: [lista si aplica].
