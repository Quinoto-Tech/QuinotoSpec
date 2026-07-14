# Arquitectura Interna de QuinotoSpec

## Vision General

QuinotoSpec es un sistema de configuracion de agentes basado en tres pilares:

1. **Workflows**: Secuencias de instrucciones que el agente ejecuta
2. **Skills**: Capacidades especializadas reutilizables
3. **Rules**: Restricciones inmutables que gobiernan el comportamiento

## Diagrama de Arquitectura

```
+------------------+
|   install.sh     |  <-- Punto de entrada
+--------+---------+
         |
         v
+--------+---------+
|   agent-dist/    |  <-- Distribucion
|  +-------------+ |
|  | workflows/  | |  <-- 38 workflows
|  | skills/     | |  <-- 31 skills
|  | rules/      | |  <-- 12 reglas
|  | agents/     | |  <-- 9 agentes
|  | templates/  | |  <-- 5 templates
|  +-------------+ |
+--------+---------+
         |
         v
+--------+---------+
|  IDE Target      |  <-- .opencode/, .cursor/, .agent/
|  +-------------+ |
|  | commands/   | |  <-- Workflows renombrados
|  | skills/     | |
|  | rules/      | |
|  +-------------+ |
+--------+---------+
         |
         v
+--------+---------+
|  AGENTS.md       |  <-- Instrucciones globales
+------------------+
```

## Flujo de Datos

```
Usuario -> IDE -> Agente -> Workflow -> Skills -> .quinoto-spec/
              │                      │              ├── specs/
              │                      │              ├── proposals/
              │                      │              └── discovery/
              │                      v
              │                Rules (gobierno)
              │                      │
              │                      v
              └────────────── Changelog (trazabilidad)
```

## Componentes

### Workflows (35)

Los workflows se dividen en categorias:

**Core (flujo principal):**
- discovery, create-proposal, create-user-stories, create-tasks, apply

**Specs (sistema de especificacion):**
- specs-init: Inicializa specs/ con requerimientos desde discovery o propuestas existentes
- schema-fork: Crea schema YAML personalizado del DAG de artefactos

**Gestion:**
- archive, status, review, pre-commit, release

**Discovery:**
- stack-discovery, refresh-discovery, dependency-graph

**Especiales:**
- battle-frenzy, blood-bond, mjolnir-refactor, heimdallr, tiwaz-rune

**Soporte:**
- init, migrate, backup, export, import, onboard, agent-train

**Colaboracion Multi-Agente:**
- battle-frenzy: Ejecucion paralela de tareas masivas con subagentes
- party-mode: Mesa redonda multi-agente — debate en caracter, dos modos (voiced/spawned). Integrado via `--party` en create-proposal y create-rfc

**Sprints:**
- sprints.init, sprint.create, sprint.plan

**Mantenimiento:**
- health, cleanup, retrospective

---

## Sistema de Delta Specs (v2.2+)

### Arquitectura de Especificacion Incremental

QuinotoSpec usa especificaciones incrementales (delta specs) para describir cambios al sistema:

```
.quinoto-spec/
├── specs/                   # Source of truth canonico
│   ├── auth/
│   │   └── spec.md          # Requerimientos actuales del dominio auth
│   ├── payments/
│   │   └── spec.md
│   └── README.md
│
├── proposals/
│   └── <DATE>-<slug>/
│       ├── proposal.md      # Resumen ejecutivo + ref a delta-specs/
│       ├── delta-specs/     # DELTA (cambios incrementales)
│       │   ├── auth/
│       │   │   └── spec.md  # ADDED/MODIFIED/REMOVED/RENAMED
│       │   └── payments/
│       │       └── spec.md
│       ├── user-stories.md
│       └── *_tasks.md
│
├── discovery/
└── ...
```

### Flujo de Delta Specs

```
create-proposal  →  genera delta-specs/ (ADDED/MODIFIED/REMOVED/RENAMED)
                            ↓
apply + archive  →  engine de merge aplica deltas en specs/
                            ↓
specs/           →  source of truth actualizado automaticamente
```

### Operaciones de Merge

| Operacion | Accion |
|-----------|--------|
| ADDED | Append al final de `specs/<dominio>/spec.md` |
| MODIFIED | Reemplazar bloque existente por nombre exacto |
| REMOVED | Eliminar bloque existente |
| RENAMED | Renombrar seccion existente |

### Compatibilidad hacia atras

Las propuestas sin `delta-specs/` se archivan normalmente sin merge de specs.
El sistema coexiste con el formato anterior de propuestas.

---

### Skills (31)

Organizadas por dominio:

**Basicas:** stack-detect, file-creation, generate-github-branch, mark-done, update-changelog, validate, entropy-calculator

**Gobernanza:** rules-enforce, syntax-validate, rollback, metrics

**Busqueda y Analisis:** search, stats, diff, sync, estimate, conflict-detector, suggest-next

**Specs y Artefactos:** artifact-engine

**Blood-Bond:** blood-bond-analyzer, blood-bond-monitor, blood-bond-predictor

**Swarm:** swarm-executor, swarm-task-splitter

**Party Mode:** party-orchestrator

**Onboarding:** onboard-developer, onboard-product, onboard-support, onboard-general, onboard-simple

### Reglas (12)

Las reglas tienen niveles de severidad:

**BLOCKING (detienen ejecucion):**
- #3 Product Agreement Check
- #9 Validacion Pre-Workflow Critico
- #10 Backup Pre-Refactor
- #12 Proteccion de Archivos Archivados

**WARNING (advierten pero permiten):**
- #11 Validacion de Sintaxis Pre-Apply

**STANDARD (siempre activas):**
- #1 Gestion del Changelog
- #2 Gestion de Prefijos e IDs
- #4 No Sobreescribir
- #5 Validacion de Estado Antes de Archivar
- #6 Convencion de Archivado
- #7 Nombrado de Branches
- #8 Aprobacion de Configuracion Critica

## Extension

### Agregar un Workflow

1. Crea `agent-dist/workflows/quinotospec.<name>.md`
2. Incluye frontmatter con `description`
3. Incluye heading H1
4. Documenta precondiciones, pasos, output, ejemplos y errores
5. Actualiza README.md

### Agregar una Skill

1. Crea `agent-dist/skills/quinotospec-<name>/SKILL.md`
2. Incluye frontmatter con `name` y `description`
3. Documenta instrucciones, parametros, ejemplos
4. Actualiza README.md

### Agregar un Agente

1. Crea `agent-dist/agents/<name>.md`
2. Incluye frontmatter con `name`, `specialization`, `trigger_workflows`, `model_suggestion`
3. Documenta personalidad, capacidades, casos de uso
4. Actualiza README.md
