---
name: quinotospec-artifact-engine
description: Computa el estado del DAG de artefactos basado en el schema YAML — determina que artefactos estan listos, bloqueados o completados
---

# Artifact Dependency Graph Engine

## Overview

Lee `.quinoto-spec/schema.yaml` y computa el estado de cada artefacto para una propuesta dada, basandose en la existencia de archivos en el filesystem y las dependencias declaradas en el schema.

**Core principle:** Las dependencias son habilitadores, no compuertas. Saber que esta listo ayuda a decidir que hacer — no fuerza un orden.

## Modos de Operacion

| Modo | Flag | Output |
|------|------|--------|
| **Status** | `--status --change <slug>` | Estado de artefactos: done/ready/blocked |
| **Instructions** | `--instructions <artifact> --change <slug>` | Instrucciones enriquecidas para generar un artefacto |
| **Validate** | `--validate --change <slug>` | Valida que no haya artefactos creados sin dependencias |
| **List ready** | `--ready --change <slug>` | Lista solo artefactos listos para crear |
| **List blocked** | `--blocked --change <slug>` | Lista artefactos bloqueados y por que |

---

## Paso 1 — Cargar Schema

1. Buscar schema en orden de prioridad:
   - `.quinoto-spec/schema.yaml` (proyecto local, customizado)
   - `agent-dist/templates/schema-template.yaml` (default del paquete)
2. Si no se encuentra ninguno, reportar error y detener.
3. Parsear YAML: extraer `artifacts`, `apply`, `phases`, `validation`.

---

## Paso 2 — Resolver Slug de Propuesta

1. Si se paso `--change <slug>`, usar ese slug.
2. Si no, buscar propuestas activas en `.quinoto-spec/proposals/`:
   - Si hay una sola → usarla.
   - Si hay varias → listar y pedir que se especifique con `--change`.
   - Si no hay ninguna → reportar y detener.

---

## Paso 3 — Computar Estado del DAG

Para cada artefacto definido en el schema:

### 3a — Determinar existencia (filesystem check)

Resolver el glob `generates` reemplazando `{slug}` por el slug de la propuesta:

| Artefacto | Path resuelto |
|-----------|---------------|
| proposal | `.quinoto-spec/proposals/{slug}/proposal.md` |
| delta-specs | `.quinoto-spec/proposals/{slug}/delta-specs/**/*.md` |
| design | `.quinoto-spec/proposals/{slug}/design.md` |
| user-stories | `.quinoto-spec/proposals/{slug}/user-stories.md` |
| tasks | `.quinoto-spec/proposals/{slug}/*_tasks.md` |

- Si el archivo/directorio existe → estado base: `done`
- Si no existe → estado base: `pending`

### 3b — Verificar dependencias

Para artefactos en estado `pending`:
- Revisar la lista `requires`
- Si TODAS las dependencias estan `done` → estado final: `ready`
- Si ALGUNA dependencia esta `pending` o no existe → estado final: `blocked`
  - Listar cuales dependencias faltan

### 3c — Artefactos opcionales

Si un artefacto tiene `optional: true`:
- Si no existe, no bloquea a sus dependientes
- Se muestra como `optional` en el status
- Se omite del calculo de bloqueo para artefactos que dependen de el

---

## Paso 4 — Topological Sort

Ordenar los artefactos respetando el DAG de dependencias:

```
Orden de creacion sugerido (topological sort):
  1. constitution [optional]
  2. discovery [optional]
  3. proposal
  4. delta-specs  |  design   (paralelo)
  5. user-stories
  6. tasks
  7. apply
```

---

## Paso 5 — Generar Output

### Modo Status (`--status`)

```markdown
## Artifact Status — {slug}

| Artefacto | Estado | Dependencias |
|-----------|--------|-------------|
| proposal | ✅ done | — |
| delta-specs | ✅ done | ✅ proposal |
| design | ⏳ ready | ✅ proposal |
| user-stories | 🔒 blocked | ❌ design (pending) |
| tasks | 🔒 blocked | ❌ user-stories (blocked) |

**Listos para crear:** design
**Bloqueados:** user-stories (espera: design), tasks (espera: user-stories)
**Progreso:** 2/7 artefactos completados
```

### Modo Instructions (`--instructions <artifact>`)

Retorna instrucciones enriquecidas combinando:
1. `instruction` del schema para ese artefacto
2. Template path (si existe)
3. Contexto del proyecto desde `.quinoto-spec/config.yaml` (si existe)
4. Contenido de artefactos dependencia (para que el agente tenga contexto)

### Modo Validate (`--validate`)

```
✓ proposal: existe, dependencias satisfechas
✓ delta-specs: existe, dependencias satisfechas
⚠ design: NO existe pero user-stories ya fue creado — fuera de orden
❌ tasks: existe pero user-stories NO existe — dependencia faltante
```

---

## Paso 6 — Manejo de Errores

| Error | Accion |
|-------|--------|
| Schema YAML no encontrado | Reportar paths buscados, sugerir `@quinotospec.schema-fork` |
| Schema YAML malformado | Reportar error de parse, mostrar linea |
| Slug no encontrado | Listar propuestas activas disponibles |
| Artefacto no definido en schema | Reportar artefactos validos conocidos |
| Dependencia circular | Detectar y reportar ciclo |

---

## Integracion con Otros Componentes

### Con `quinotospec.status`
El workflow `@quinotospec.status` invoca este engine con `--status` para cada propuesta activa y agrega la tabla de estado de artefactos al dashboard.

### Con `quinotospec-help`
El skill `quinotospec-help` invoca el engine con `--ready` para sugerir el proximo artefacto a crear.

### Con `quinotospec.suggest-next`
El skill `quinotospec-suggest-next` usa el engine con `--instructions` para obtener contexto al sugerir la siguiente tarea.

---

## Ejemplos

```
# Ver estado de artefactos de una propuesta
Skill: quinotospec-artifact-engine --status --change rewards-stabilization

# Ver que artefactos estan listos
Skill: quinotospec-artifact-engine --ready --change rewards-stabilization

# Obtener instrucciones para crear design
Skill: quinotospec-artifact-engine --instructions design --change rewards-stabilization

# Validar consistencia del DAG
Skill: quinotospec-artifact-engine --validate --change rewards-stabilization
```
