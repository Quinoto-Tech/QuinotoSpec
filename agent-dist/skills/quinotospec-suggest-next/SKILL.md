---
name: quinotospec-suggest-next
description: Sugiere la siguiente tarea a ejecutar analizando el archivo de tareas de la propuesta activa. Detecta dependencias y orden lógico.
---

# Skill: Suggest Next

Analiza el estado actual de las tareas de una propuesta y sugiere cuál debería ejecutarse a continuación, respetando dependencias y orden numérico.

## Instrucciones de Ejecución

### Paso 1 - Recibir parámetros

Recibir uno de:
- `--task-id {{TASK_ID}}` (ej. `TSK-AUTH-a1b2-001`): deriva US_ID y busca en la propuesta
- `--proposal-slug {{SLUG}}`: busca siguiente tarea en toda la propuesta, no solo en la story actual
- `--us-id {{US_ID}}` + `--proposal-slug {{SLUG}}`: busca siguiente tarea en una story específica

### Paso 2 - Derivar contexto

Si se usó `--task-id`:
1. Consulta `python3 agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json`.
2. Busca el `raw_id` o `canonical_id` de la tarea en el snapshot.
3. Obtén la story desde `story_id`/`story_raw_id`; nunca la derivas del número de la tarea.
4. Busca el archivo `*_tasks.md` que contenga esa relación explícita.

### Paso 3 - Encontrar siguiente tarea

1. Usa el contrato común para leer `status`, `dependencies` y `story_id`; acepta tablas canónicas y legacy.
2. Recorre las tareas por `canonical_id` numérico.
3. Una tarea está lista si `status == pending` y todas sus dependencias están `completed`.
4. La primera tarea que cumpla ambas condiciones es la siguiente.
5. `all_tasks.md` es un índice derivado y no debe duplicar candidatos.

### Paso 4 - Formular sugerencia

Responder con uno de estos 3 mensajes:

**Caso A - Hay siguiente tarea en la misma story:**
```
Siguiente tarea: {{NEXT_TASK_ID}} — {{NEXT_TASK_DESCRIPTION}}
¿Deseas continuar? Ejecutá: @quinotospec.apply --task-id {{NEXT_TASK_ID}}
```

**Caso B - No hay más tareas en esta story, pero sí en la propuesta:**
```
No hay más tareas pendientes en {{US_ID}}.
Próxima story con tareas: {{NEXT_US_ID}}
Primera tarea: {{NEXT_TASK_ID}} — {{NEXT_TASK_DESCRIPTION}}
```

**Caso C - Todas las tareas de la propuesta completadas:**
```
¡Propuesta {{PROPOSAL_SLUG}} completada! Todas las tareas están [x].
```

### Paso 5 - Modo alternativo (--next para saltear)

Si se usa `--next`, buscar el penúltimo `[x]` y sugerir la tarea siguiente a esa (útil cuando se quiere saltear manualmente una tarea).

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--task-id {{ID}}` | ID de la tarea actual (deriva contexto automáticamente) |
| `--proposal-slug {{SLUG}}` | Buscar en toda la propuesta, no solo la story actual |
| `--us-id {{US_ID}}` | Buscar siguiente tarea en una user story específica |
| `--next` | Saltea la tarea actual (busca la siguiente después de la última completada) |

## Ejemplos

```
@quinotospec-suggest-next --task-id TSK-AUTH-a1b2-001
@quinotospec-suggest-next --proposal-slug auth-jwt
@quinotospec-suggest-next --us-id US-AUTH-a1b2-001 --proposal-slug auth-jwt --next
```

## Notas

- Si el archivo de tareas no existe, retornar error con sugerencia: "Ejecutá @quinotospec.create-tasks primero."
- Si no hay discovery, advertir pero continuar.
- Esta skill también se ejecuta automáticamente al final de `@quinotospec.apply`.
