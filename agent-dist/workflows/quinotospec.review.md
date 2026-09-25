---
description: Revisa un branch o PR contra los criterios de aceptación de la tarea y la propuesta correspondiente
---

# Workflow: Review

Este workflow guía al agente para realizar una revisión técnica de código antes de mergear, validando contra los criterios definidos en la especificación.

## Extension hooks

Consulta `before_review` y `after_review` con `extension_manager.py hooks --point <point> --json`. Ejecuta hooks automáticos solo con `--run --yes` y adjunta sus resultados al reporte.

**Parámetros Requeridos:**
- `TASK_ID`: El ID de la tarea técnica asociada al branch (ej. `TSK-AUTH-001`).
- `BRANCH_NAME`: El nombre del branch a revisar (ej. `feature/TSK-AUTH-001-add-login`).

**Instrucciones:**

1. **Contexto de la revisión**:
    - Lee el archivo de tareas correspondiente al `{{TASK_ID}}` en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md`.
    - Lee la propuesta en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md`, en especial las secciones de **Criterios de Aceptación (DoD)** y **Especificación Técnica Detallada**.
    - Lee `01-stack-profile.md` para conocer los estándares de código del proyecto.
    - Si existe `.quinoto-spec/constitution.md` con estado `active`, lee sus principios y gates; si está ausente, registra una advertencia de compatibilidad.

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
    - [ ] **Convenciones del stack**: ¿El código sigue los patrones detectados en `01-stack-profile.md`?
    - [ ] **Archivos declarados**: ¿Los archivos modificados coinciden con los declarados en la columna "Archivos a Modificar" de la tarea?
    - [ ] **Sin regresiones**: ¿La suite de tests completa pasa sin errores?
    - [ ] **Compliance constitucional**: si la constitución está activa, ¿cada principio aplicable tiene evidencia o una excepción aprobada?
    - [ ] **Sin deuda técnica obvia**: ¿No hay TODOs sin resolver, console.logs, o código comentado que no debería estar?

4. **Feedback recibido**:
    - Si una persona, reviewer externo o bot envía comentarios, invoca `quinotospec-receive-review`.
    - Verifica el feedback antes de aceptarlo; no implementes cambios directamente desde este workflow.
    - Si la respuesta es correcta, aplica los cambios mediante `quinotospec-apply` y conserva sus gates.
    - Si el feedback viola YAGNI, falta contexto o rompe funcionalidad, responde con push back técnico.
    - Reconoce feedback corregido con `Fixed. [Brief description]`, sin acuerdo performativo.

5. **Resultado de la revisión**:
    - Si todos los puntos son ✅ → el branch está listo para mergear. Notificar al usuario.
    - Si hay ❌ o ⚠️ → generar un informe detallado de los puntos a corregir antes de mergear.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la revisión, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Code Review: {{TASK_ID}}
- **Resumen**: Se revisó el branch '{{BRANCH_NAME}}'. Resultado: [Aprobado / Requiere Cambios]. Puntos pendientes: [lista si aplica].
