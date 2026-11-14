---
name: quinotospec-verify-before-done
description: Usar inmediatamente antes de marcar una tarea como completada para reclamar evidencia fresca y revisar el DoD.
---

# Skill: QuinotoSpec Verify Before Done

## Iron Law

**No afirmes que una tarea está completada sin evidencia fresca de tests, lint, typecheck, criterios de aceptación aplicables y una pasada Goldfish del alcance.**

## Gate de seis pasos

1. **Identifica la tarea**: localiza su `canonical_id`, story y proposal mediante el contrato.
2. **Revisa DoD**: enumera cada criterio y asocia evidencia concreta.
3. **Ejecuta verificaciones**: usa el runner del stack para tests, lint y typecheck disponibles.
4. **Goldfish gate**: un agente con contexto limpio lee **solo** la propuesta y las tareas y explica el alcance; si no puede, el documento pierde el gate.
5. **Inspecciona el diff**: confirma que no hay cambios accidentales, secretos ni archivos archivados.
6. **Decide**: `completed` solo si la evidencia es fresca y el Goldfish explicó el alcance; de lo contrario `blocked` o `in_progress`.

## Evidencia requerida

```text
Tarea: TSK-MNEM-suffix-NNN
Criterio 1: <criterio> → <test/comando> → OK
Criterio 2: <criterio> → <test/comando> → N/A justificado
Tests: <comando> → <resultado>
Lint/typecheck: <comando> → <resultado>
Diff: <archivos revisados> → sin hallazgos
```

## Registro verificable

Guarda un registro JSON en `.quinoto-spec/evidence/{{TASK_ID}}/verify-before-done.json` con `schema_version`, `task_id`, `recorded_at`, `checks`, `tests`, `lint`, `typecheck` y `diff`. Cada check incluye criterio y un bloque de ejecución; los comandos no disponibles deben usar `status: not_applicable` y justificación explícita.

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py validate \
  --root . --kind verify-before-done --task-id {{TASK_ID}} --require --json
```

El validador exige frescura, resultados tipados y checks DoD no vacíos; no reemplaza la ejecución real de los comandos.

## Goldfish gate (BLOQUEANTE)

El agente que redactó la tarea no puede auditarla: arrastra el contexto que produjo el hueco. Antes de cerrar, lanza un subagente **sin contexto** con la instrucción:

```text
Lee únicamente estos documentos y los archivos que referencian:
  - {{PROPOSAL_PATH}}
  - {{TASKS_PATH}}
Explícame en 10 líneas qué se está construyendo, qué queda fuera de alcance y
qué criterio de aceptación lo prueba. Si algo no se puede responder con esos
documentos, dilo explícitamente en vez de suponerlo.
```

Si el goldfish no puede explicar el alcance con esos documentos, **no respondas por él**: agregá el contexto faltante a la propuesta o a la tarea, volvé a correr la pasada y recién entonces registrá la evidencia. Guarda `.quinoto-spec/evidence/{{TASK_ID}}/goldfish.json`:

```json
{
  "schema_version": 1,
  "kind": "goldfish",
  "task_id": "TSK-MNEM-suffix-NNN",
  "recorded_at": "2026-01-31T12:00:00+00:00",
  "fresh_context": true,
  "lenses": ["comprehension"],
  "inputs": [".quinoto-spec/proposals/<slug>/proposal.md", ".quinoto-spec/proposals/<slug>/<US_ID>_tasks.md"],
  "comprehension": {"explained_scope": true, "summary": "<qué entendió el goldfish>"},
  "verdict": "pass",
  "findings": [{"severity": "warn", "status": "resolved", "detail": "<ambigüedad y cómo se cerró>"}]
}
```

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py validate \
  --root . --kind goldfish --task-id {{TASK_ID}} --require --json
```

El validador exige `fresh_context: true`, al menos la lente `comprehension`, `explained_scope: true`, veredicto `pass`, cero hallazgos `blocking` abiertos y que cada documento de `inputs` exista y **no haya cambiado después de la revisión** (si cambió, la revisión está stale: repetila).

La pasada Goldfish es una capa de detección de puntos ciegos: no reemplaza tests, revisión humana ni la evidencia de `verify-before-done`.

## Common failures

| Fallo | Acción |
|---|---|
| Tests no ejecutados | Ejecutarlos antes de continuar. |
| Tests stale | Volver a ejecutarlos después del último cambio. |
| Criterio sin test | Añadir test o documentar por qué no aplica. |
| Lint no disponible | Registrar el comando omitido y pedir confirmación. |
| Goldfish no explica el alcance | Completar el documento y repetir la pasada; no aprobar por confianza propia. |
| Evidencia Goldfish stale | Repetir la revisión después del último cambio del documento. |
| Secrets en diff | Detener, eliminar y revisar alcance. |
| Error de tooling | Separar error de entorno de regresión. |

## Red Flags

1. “Debería funcionar” sin ejecución.
2. Suite ejecutada antes del último cambio.
3. Solo se ejecutó el test nuevo.
4. Criterios DoD marcados sin evidencia.
5. `--force` usado para ocultar una verificación fallida.
6. Errores conocidos excluidos de la salida.
7. Secrets presentes en logs o diff.
8. Archivos `_archived/` modificados.
9. Goldfish “revisado” por el mismo agente que redactó la tarea.

## Racionalizaciones

| Racionalización | Respuesta |
|---|---|
| “El cambio es solo una línea” | Una línea puede romper el contrato; verifica igual. |
| “La suite ya pasó antes” | La evidencia debe ser fresca. |
| “El test está en CI” | CI no sustituye la comprobación local del claim. |
| “El error es del entorno” | Demuéstralo con el comando y el estado. |
| “No hay tiempo” | Reporta bloqueado; no declares completado. |
| “El reviewer lo verá” | El claim requiere evidencia local reproducible. |
| “El force mode está permitido” | Force archiva; no elimina la evidencia. |

## Integración

`quinotospec-mark-done` debe ejecutar este gate antes de cambiar estados o mover archivos, incluyendo la evidencia `goldfish`. `quinotospec-apply` debe llamarlo después de tests y antes del changelog final.

`rules_enforce.py` expone el mismo gate como check `goldfish` (regla 16): con `--require-evidence` falla si la evidencia falta o no valida, igual que `verify-before-done`.
