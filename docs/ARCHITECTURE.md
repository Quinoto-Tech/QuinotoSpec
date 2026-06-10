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
|  | workflows/  | |  <-- 33 workflows
|  | skills/     | |  <-- 27 skills
|  | rules/      | |  <-- 12 reglas
|  | agents/     | |  <-- 9 agentes
|  | templates/  | |  <-- Templates
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
                                    |
                                    v
                              Rules (gobierno)
                                    |
                                    v
                              Changelog (trazabilidad)
```

## Componentes

### Workflows (33)

Los workflows se dividen en categorias:

**Core (flujo principal):**
- discovery, create-proposal, create-user-stories, create-tasks, apply

**Gestion:**
- archive, status, review, pre-commit, release

**Discovery:**
- stack-discovery, refresh-discovery, dependency-graph

**Especiales:**
- battle-frenzy, blood-bond, mjolnir-refactor, heimdallr

**Soporte:**
- init, migrate, backup, export, import, onboard, agent-train

**Sprints:**
- sprints.init, sprint.create, sprint.plan

**Mantenimiento:**
- health, cleanup, retrospective

### Skills (27)

Organizadas por dominio:

**Basicas:** stack-detect, file-creation, generate-github-branch, mark-done, update-changelog, validate

**Gobernanza:** rules-enforce, syntax-validate, rollback, metrics

**Busqueda y Analisis:** search, stats, diff, sync, estimate, conflict-detector, suggest-next

**Blood-Bond:** blood-bond-analyzer, blood-bond-monitor, blood-bond-predictor

**Swarm:** swarm-executor, swarm-task-splitter

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
