---
name: quinotospec-apply
description: aplicar la tarea correspondiente
---

# Workflow: Apply

[INSTRUCCIÓN MAESTRA]
Debes ejecutar la tarea técnica especificada por el usuario y documentar EXACTAMENTE los cambios realizados en el archivo de registro.

**Tarea a realizar:**
`{{TASK_ID}}` — {{TASK_DESCRIPTION}}

**Opciones opcionales de aislamiento:**
- `USE_WORKTREE`: por defecto `false`; el usuario puede activarlo con `--worktree`.
- `WORKTREE_PATH`: ruta opcional, activada con `--worktree-path`.
- `BASE_REF`: referencia base explícita para crear el worktree; no la adivines.
- Si `USE_WORKTREE=true`, invoca `quinotospec-worktree` y realiza todos los cambios, tests, changelog y mark-done dentro del worktree resultante.

**Contexto Global OBLIGATORIO:**
Antes de realizar cualquier cambio:
1. Ejecuta `python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict` y detén el workflow ante errores.
2. Consulta `python3 agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json`; localiza el `canonical_id` de `{{TASK_ID}}` y usa `story_id` como contexto, sin derivar la story por número.
3. Lee el archivo `*_tasks.md` que contiene la tarea, la story asociada y la proposal.md de la propuesta.
4. Lee `.quinoto-spec/discovery/` para comprender el estado actual del proyecto (especialmente `01-stack-profile.md` para conocer el stack, comandos de test y convenciones).
5. Asegúrate de que esta tarea contribuya coherentemente a la arquitectura global.
6. Si existe `.quinoto-spec/constitution.md` con estado `active`, lee sus principios y verifica que la tarea pueda cumplirlos; si no puede, detén el Apply y solicita una enmienda o decisión explícita.

**Instrucciones de Ejecución:**
1. **Confirmación requerida**: pregunta separadamente si se debe crear un branch nuevo y si se desea usar un worktree. Resuelve `BRANCH_NAME` y `BASE_REF`; no los inventes.
2. **Constitution Gate**: si existe `.quinoto-spec/constitution.md` activo, verifica cada principio aplicable antes de modificar producción; si hay violación, detén el Apply.
2b. **Human Approval Gate**: para configuración crítica, recuperación de archivo archivado u otra decisión humana, registra `.quinoto-spec/approvals/{{APPROVAL_ID}}.json` después de la confirmación explícita y valida `human-approval` con `rules_enforce.py --require-approval --approval-id {{APPROVAL_ID}} --approval-subject {{SUBJECT}} --approval-action apply`; una confirmación conversacional no basta.
3. **Worktree Gate (opcional)**: si `USE_WORKTREE=true` y el usuario confirma, invoca `quinotospec-worktree` con `TASK_ID`, `BRANCH_NAME`, `BASE_REF` y `WORKTREE_PATH` opcional. La skill reutiliza un aislamiento existente o crea uno seguro. Si el usuario lo rechaza, continúa en el checkout actual.
4. Si `USE_WORKTREE=false` y el usuario confirmó crear un branch, usa `quinotospec-generate-github-branch`. Si `USE_WORKTREE=true`, no dupliques la creación del branch con `git checkout -b`.
5. **Baseline y contexto**: después de crear o reutilizar un worktree, verifica su raíz, branch y disponibilidad de los artefactos; ejecuta la baseline de tests definida por `01-stack-profile.md`. Una baseline fallida bloquea TDD y activa `quinotospec-debug`.
6. Si el cambio proviene de feedback de review, ejecuta primero `quinotospec-receive-review` y aplica solo los puntos verificados.
7. **RED obligatorio**: para código de producción, ejecuta `quinotospec-tdd`, escribe el test mínimo y registra el fallo esperado antes de modificar producción. Guarda `.quinoto-spec/evidence/{{TASK_ID}}/tdd.json` y valida con `evidence_validate.py --kind tdd --require --json`.
8. **GREEN mínimo**: implementa solo el comportamiento requerido, ejecuta el test focalizado y confirma que pasa.
9. **REFACTOR**: mejora la estructura sin cambiar el comportamiento y vuelve a ejecutar los tests afectados.
10. Si aparece un fallo después de implementar, cambia a `quinotospec-debug`; registra `.quinoto-spec/evidence/{{TASK_ID}}/debug.json` y valida con `evidence_validate.py --kind debug --require --json` antes del hotfix.
11. **Verificación de Criterios de Aceptación (DoD)**: revisa uno a uno los criterios definidos en la tarea/historia y asocia a cada uno un comando o evidencia.
12. **Calidad del stack**: ejecuta tests, lint y typecheck disponibles usando `01-stack-profile.md`; corrige regresiones antes de continuar.
13. Ejecuta `quinotospec-verify-before-done`, guarda `.quinoto-spec/evidence/{{TASK_ID}}/verify-before-done.json` y valida con `evidence_validate.py --kind verify-before-done --require --json`; no continúes al changelog si la evidencia no está fresca.
14. **Revisión recomendada (opcional)**: si se creó un branch, sugiere `@quinotospec.review` con `TASK_ID={{TASK_ID}}` y `BRANCH_NAME={{BRANCH_NAME}}` antes de mergear.

Para documentación, configuración o migración sin comportamiento ejecutable, reemplaza el gate RED por una validación determinista equivalente y documenta la excepción. No implementes en el checkout original después de activar un worktree.

**Instrucciones de Documentación (Changelog):**
Una vez aplicados los cambios, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Tarea: {{TASK_ID}} — {{TASK_DESCRIPTION}}
- **Resumen**:
  - Lista de archivos modificados con el siguiente formato por cada uno:
    - `ruta/relativa/al/archivo` — [creado | modificado | eliminado] — motivo del cambio
  - Resumen técnico de la solución implementada.
  - Estado de los criterios de aceptación (DoD): ✅ cumplidos / ⚠️ excepciones documentadas.

**Instrucción Final OBLIGATORIA (Mark Done):**
Una vez completado y documentado el changelog, DEBES ejecutar la skill `quinotospec-mark-done` pasando:
- `TASK_ID`: el ID de la tarea completada.
Esto actualizará el estado de la tarea, la historia y la propuesta correspondiente.

IMPORTANTE: Los pasos de documentación y mark-done son OBLIGATORIOS. No termines la ejecución sin completarlos.

---

## Resolucion de Conflictos

Si durante la implementacion detectas conflictos con codigo existente:

### Conflicto de Merge
1. **NO fuerces** la implementacion sobre codigo existente
2. Identifica el conflicto: "El archivo X tiene implementacion incompatible con la tarea"
3. Opciones a presentar al usuario:
   - **Preservar existente**: No aplicar cambios que sobreescriben codigo existente
   - **Merge manual**: Mostrar las diferencias y pedir decision linea por linea
   - **Crear nueva tarea**: Si el conflicto requiere refactor previo, sugiere crear una tarea de desbloqueo
4. Documenta el conflicto en el changelog

### Conflicto de Arquitectura
Si la tarea contradice la arquitectura documentada en `03-architecture.md`:
1. **DETEN** la implementacion
2. Reporta: "La tarea requiere cambiar {componente} que segun la arquitectura actual es {patron}. ¿Actualizar la arquitectura o adaptar la tarea?"
3. Espera decision del usuario antes de continuar

---

## Rollback Automatico

Si los tests fallan despues de implementar cambios:

1. **Intentar corrección automática** (máximo 2 intentos):
   - Si el failure es claro (typo, import faltante), intenta corregir directamente.
2. **Si persiste el fallo**, ejecutar skill `quinotospec-rollback`:
   - La skill revierte los cambios, documenta el error, y reporta al usuario.
   - NO marcar la tarea como completada.
   - Sugerir crear una tarea de debugging.

---

## Sugerencia de Siguiente Tarea

Después de completar una tarea y ejecutar `quinotospec-mark-done`, DEBES buscar y sugerir la siguiente tarea a ejecutar:

1. **Lee el contrato normalizado**: usa `contract.py inspect --root . --json` y localiza la relación `story_id` de `{{TASK_ID}}`.
2. **Encuentra la siguiente tarea**:
   - Recorre las tareas del archivo `*_tasks.md` en orden por `canonical_id`.
   - Una tarea está lista si su estado normalizado es `pending` y todas sus dependencias están `completed`.
   - La primera tarea que cumpla estas condiciones es la siguiente.

3. **Formula la sugerencia**:
   - Si hay una siguiente tarea: *"¿Deseas continuar con la tarea `{{NEXT_TASK_ID}}` — {{NEXT_TASK_TITLE}}?"*
   - Si no hay más tareas en esa story: *"No hay más tareas pendientes en esta story. ¿Deseas continuar con otra user story de la propuesta?"*
   - Si todas las tareas de la propuesta están completas: *"¡Felicidades! Todas las tareas de la propuesta '{{PROPOSAL_SLUG}}' han sido completadas."*

**Nota**: Si el archivo de tareas no existe o no se puede determinar la siguiente tarea, omite esta sugerencia silenciosamente.
