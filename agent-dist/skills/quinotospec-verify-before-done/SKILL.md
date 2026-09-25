---
name: quinotospec-verify-before-done
description: Usar inmediatamente antes de marcar una tarea como completada para reclamar evidencia fresca y revisar el DoD.
---

# Skill: QuinotoSpec Verify Before Done

## Iron Law

**No afirmes que una tarea está completada sin evidencia fresca de tests, lint, typecheck y criterios de aceptación aplicables.**

## Gate de cinco pasos

1. **Identifica la tarea**: localiza su `canonical_id`, story y proposal mediante el contrato.
2. **Revisa DoD**: enumera cada criterio y asocia evidencia concreta.
3. **Ejecuta verificaciones**: usa el runner del stack para tests, lint y typecheck disponibles.
4. **Inspecciona el diff**: confirma que no hay cambios accidentales, secretos ni archivos archivados.
5. **Decide**: `completed` solo si la evidencia es fresca; de lo contrario `blocked` o `in_progress`.

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

## Common failures

| Fallo | Acción |
|---|---|
| Tests no ejecutados | Ejecutarlos antes de continuar. |
| Tests stale | Volver a ejecutarlos después del último cambio. |
| Criterio sin test | Añadir test o documentar por qué no aplica. |
| Lint no disponible | Registrar el comando omitido y pedir confirmación. |
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

`quinotospec-mark-done` debe ejecutar este gate antes de cambiar estados o mover archivos. `quinotospec-apply` debe llamarlo después de tests y antes del changelog final.
