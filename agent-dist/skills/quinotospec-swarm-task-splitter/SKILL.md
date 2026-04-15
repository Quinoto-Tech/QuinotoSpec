---
name: Quinotospec Swarm Task Splitter
description: Divide tareas masivas en chunks paralelizables para ejecución en paralelo
---

# Skill: Quinotospec Swarm Task Splitter

Divide una tarea masiva en unidades independientes que pueden ejecutarse en paralelo.

## Entrada

Recibe:
- Descripción de la tarea masiva
- Límite opcional de chunks (`--limit`, default: 5)
- flags: `--dry-run` para solo mostrar división sin ejecutar

## Algoritmo de División

### Paso 1 — Análisis de Tarea

1. Lee el contexto del proyecto (discovery, tareas existentes)
2. Analiza la descripción de la tarea
3. Determina si es paralelizable o secuencial

### Paso 2 — Criterios de Paralelización

Una tarea ES paralelizable si:
- Los chunks son independientes entre sí
- No hay dependencias de estado compartido
- Cada chunk puede ejecutarse sin esperar resultado de otro

Una tarea es SECUENCIAL si:
- Hay dependencias entre chunks
- Requiere estado acumulado
- El orden afecta el resultado

### Paso 3 — Generación de Chunks

1. Identifica subtareas independientes
2. Asigna un ID único a cada chunk: `SWARM-001`, `SWARM-002`, etc.
3. Define el tipo de tarea para cada chunk:
   - Código → implementación
   - Revisión → revisión
   - Análisis → análisis
   - General → tarea simple

### Paso 4 — Validación de Independencia

Para cada chunk, verificar:
- ✅ No depende de output de otro chunk
- ✅ No modifica estado compartido sin coordinación
- ✅ Puede ejecutarse en cualquier orden

## Output

Genera `.quinoto-spec/swarm/chunks.json`:

```json
{
  "task_id": "battle-frenzy-001",
  "total_chunks": 5,
  "max_parallel": 5,
  "strategy": "parallel",
  "chunks": [
    {
      "id": "SWARM-001",
      "description": "Implementar función de validación de email",
      "type": "implementación",
      "dependencies": [],
      "estimated_time": "10min"
    },
    {
      "id": "SWARM-002", 
      "description": "Crear tests unitarios para validación",
      "type": "implementación",
      "dependencies": ["SWARM-001"],
      "estimated_time": "5min"
    },
    ...
  ]
}
```

## Flags

| Flag | Descripción |
|------|-------------|
| `--limit N` | Límite máximo de chunks (default: 5) |
| `--dry-run` | Solo mostrar división, no ejecutar |
| `--force` | Forzar paralelización aunque no sea óptimo |

## Manejo de Errores

- Si tarea no es paralelizable → retornar con `strategy: "sequential"` y recomendar `@quinotospec.apply`
- Si más de 10 chunks → preguntar al usuario si desea continuar
- Si hay dependencias entre chunks → marcar con `dependencies: ["CHUNK_ID"]` para ejecución secuencial

## Ejemplo

Input: "Migrar 10 endpoints de v1 a v2"

Output:
```json
{
  "task_id": "battle-frenzy-002", 
  "total_chunks": 10,
  "max_parallel": 5,
  "strategy": "parallel",
  "chunks": [
    {"id": "SWARM-001", "endpoint": "/users", "type": "implementación"},
    {"id": "SWARM-002", "endpoint": "/products", "type": "implementación"},
    {"id": "SWARM-003", "endpoint": "/orders", "type": "implementación"},
    ...
  ]
}
```