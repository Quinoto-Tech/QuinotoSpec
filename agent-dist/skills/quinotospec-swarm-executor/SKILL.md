---
name: quinotospec-swarm-executor
description: Ejecuta múltiples subagentes en paralelo para tareas masivas
---

# Skill: Quinotospec Swarm Executor

Ejecuta chunks de tareas en paralelo usando múltiples subagentes.

## Entrada

Recibe:
- `chunks.json` generado por swarm-task-splitter
- flags: `--dry-run`, `--limit N`

## Configuración

| Parámetro | Default | Descripción |
|-----------|---------|-------------|
| `max_parallel` | 5 | Máximo de agentes simultáneos |
| `fail_strategy` | partial | "fail-fast" o "partial" |

## Algoritmo de Ejecución

### Paso 1 — Preparación

1. Lee `chunks.json`
2. Ordena chunks por dependencias
3. Agrupa chunks independientes para ejecución paralela

### Paso 2 — Lanzamiento Paralelo

Para cada wave (grupo de chunks independientes):

1. **Lanzar subagentes en paralelo**
   - Usar Task tool con `subagent_type` apropiado
   - Asignar description detallada a cada subagente
   - Setear timeout apropiada (default: 120000ms)

2. **Recolectar resultados**
   - Esperar a que todos completen
   - Capturar output de cada uno

3. **Manejar fallos**
   - Si `fail_strategy: partial`: continuar con los demás
   - Si `fail_strategy: fail-fast`: detener si uno falla

### Paso 3 — Consolidación

1. Combinar resultados de todos los chunks
2. Identificar conflictos o inconsistencias
3. Generar reporte consolidado

## Output

Genera `.quinoto-spec/swarm/results.json`:

```json
{
  "task_id": "battle-frenzy-001",
  "strategy": "parallel",
  "waves": [
    {
      "wave": 1,
      "chunks": ["SWARM-001", "SWARM-002", "SWARM-003"],
      "status": "completed",
      "results": [
        {"chunk_id": "SWARM-001", "status": "success", "output": "..."},
        {"chunk_id": "SWARM-002", "status": "success", "output": "..."},
        {"chunk_id": "SWARM-003", "status": "failed", "error": "..."}
      ]
    }
  ],
  "summary": {
    "total": 5,
    "success": 4,
    "failed": 1,
    "duration_seconds": 45
  }
}
```

## Manejo de Errores

- Si subagente falla → registrar error, continuar con estrategia `partial`
- Si timeout → marcar como `timeout`, continuar
- Si conflicto entre resultados → reportar en `conflicts` array

## Flags

| Flag | Descripción |
|------|-------------|
| `--dry-run` | Simular ejecución sin lanzar agentes |
| `--limit N` | Limitar a N agentes en paralelo |
| `--fail-fast` | Detener al primer fallo |

## Ejemplo de Uso

```
👤: @quinotospec.battle-frenzy Migrar 5 endpoints a v2
🤖: Dividiendo tarea en 5 chunks independientes...
    → SWARM-001: /users
    → SWARM-002: /products
    → SWARM-003: /orders
    → SWARM-004: /payments
    → SWARM-005: /notifications

    Ejecutando en paralelo (3 waves)...

    Wave 1: [SWARM-001] ✅
    Wave 2: [SWARM-002] ✅
    Wave 3: [SWARM-003] ✅

🪓 **Battle Frenzy: Completado**
    ✅ 5/5 exitosos (52s)
    📊 .quinoto-spec/swarm/results.json
```