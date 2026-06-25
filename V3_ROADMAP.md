# QuinotoSpec v3.0 — Plan de Implementacion

## Resumen Ejecutivo

Este documento detalla el plan de evolucion de QuinotoSpec desde v2.1.0 (Yggdrasil) hacia v3.0.0 (Warband: Phalanx), incorporando las mejores caracteristicas identificadas en el analisis competitivo de los 4 frameworks lideres del ecosistema:

- **Superpowers** (obra/superpowers) — Disciplina de ingenieria (TDD, debugging, verificacion)
- **OpenSpec** (Fission-AI/OpenSpec) — Spec-driven con delta specs y artifact DAG
- **Spec-Kit** (github/spec-kit) — Extensiones/presets, constitution, workflow engine
- **BMAD-METHOD** (bmad-code-org/bmad-method) — Agentes con personalidad, party mode, scale-adaptive

**Version actual:** 2.4.0
**Version objetivo:** 3.3.0
**Fases:** 4 fases incrementales, cada una entregable independientemente
**Progreso:** 15/118 tareas completadas (13%)

> ⚠️ **Nota de implementacion:** Las features F2.1 (Delta Specs), F2.2 (Artifact DAG) y F3.2 (Party Mode) se implementaron como versiones incrementales (v2.2.0 → v2.4.0) antes de Fase 1. Fase 1 permanece sin implementar. Ver [Conflictos con Dependencias](#conflictos-con-dependencias-conocidos) al final de este documento.

---

## Tabla de Contenido

1. [Fase 1 — Fundamentos de Ingenieria (v3.0.0)](#fase-1--fundamentos-de-ingenieria-v300)
2. [Fase 2 — Extensibilidad (v3.1.0)](#fase-2--extensibilidad-v310)
3. [Fase 3 — Agentes y Coordinacion (v3.2.0)](#fase-3--agentes-y-coordinacion-v320)
4. [Fase 4 — Producto y Metodologia (v3.3.0)](#fase-4--producto-y-metodologia-v330)
5. [Dependencias entre Fases](#dependencias-entre-fases)
6. [Estructura de Archivos Resultante](#estructura-de-archivos-resultante)
7. [Criterios de Aceptacion por Fase](#criterios-de-aceptacion-por-fase)

---

## Fase 1 — Fundamentos de Ingenieria (v3.0.0)

**Objetivo:** Dotar a QuinotoSpec de disciplina de ingenieria de software que actualmente falta: TDD con enforcement, debugging sistematico, verificacion de evidencia, y bootstrap automatico. Esta fase es la de mayor impacto inmediato.

**Fuentes principales:** Superpowers (90%), Spec-Kit (10%)

---

### F1.1 — Session-Start Bootstrap Automatico

| Campo | Detalle |
|-------|---------|
| **Fuente** | Superpowers (`hooks/session-start`, `.opencode/plugins/superpowers.js`) |
| **Problema actual** | QuinotoSpec depende de que el agente lea `AGENTS.md` por su cuenta. Si el agente lo ignora, no hay QuinotoSpec |
| **Solucion** | Inyectar el contenido bootstrap de QuinotoSpec automaticamente al inicio de cada sesion |
| **Prioridad** | CRITICO |

#### Arquitectura

Implementar 3 mecanismos de inyeccion en paralelo (uno por IDE):

```
agent-dist/
├── hooks/
│   ├── session-start.sh          # Script bash que lee bootstrap y emite JSON
│   ├── hooks.json                # Config de hook para Claude Code
│   ├── hooks-cursor.json         # Config de hook para Cursor
│   ├── hooks-opencode.json       # Config de hook para OpenCode
│   └── run-hook.cmd              # Polyglot Windows/Unix (de Superpowers)
├── plugins/
│   └── opencode/
│       └── quinotospec-plugin.js # Plugin JS para OpenCode (config + transform)
└── ...
```

#### Mecanismo de Inyeccion por IDE

**OpenCode** (`.opencode/plugins/quinotospec-plugin.js`):
```javascript
// Config hook: registra directorios de skills/workflows/rules en el config del IDE
// Message transform hook: inyecta <EXTREMELY_IMPORTANT>quinotospec-bootstrap</EXTREMELY_IMPORTANT>
// en el primer mensaje del usuario de cada sesion
// Cache a nivel de modulo para evitar I/O repetido
```

**Cursor** (`.cursor-plugin/plugin.json` + `hooks/hooks-cursor.json`):
- `plugin.json` referencia `hooks/hooks-cursor.json`
- `hooks-cursor.json` registra `sessionStart` hook
- `session-start.sh` emite `{"additional_context": "<bootstrap>"}`

**Claude Code / Generic** (`hooks/hooks.json`):
- Mismo patron que Cursor pero con `hookSpecificOutput.additionalContext`

#### Contenido del Bootstrap (`agent-dist/bootstrap/quinotospec-bootstrap.md`)

Skill meta que se inyecta automaticamente. Enseña al agente:
1. Que esta en un proyecto QuinotoSpec
2. Como encontrar y usar workflows (`/quinotospec.*`)
3. Como encontrar y usar skills (`quinotospec-*`)
4. Reglas de gobernanza obligatorias
5. El ciclo Proposal First (Discovery → Propuesta → US → Tareas → Apply)
6. Red Flags: cuando NO saltarse el proceso

#### Tareas

- [ ] **T1.1.1** — Crear `agent-dist/bootstrap/quinotospec-bootstrap.md` — Skill meta con instrucciones de inicio de sesion, reglas, red flags, y referencia rapida a workflows/skills. Formato: frontmatter YAML + markdown.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`
  
- [ ] **T1.1.2** — Crear `agent-dist/hooks/session-start.sh` — Script bash que:
  - Detecta `$PLUGIN_ROOT`
  - Lee `bootstrap/quinotospec-bootstrap.md` (stripped frontmatter)
  - Escapa para JSON embedding
  - Emite en formato especifico de plataforma (Cursor: `additional_context`, Claude: `hookSpecificOutput.additionalContext`, OpenCode/generic: `additionalContext`)
  - Archivo: `agent-dist/hooks/session-start.sh`

- [ ] **T1.1.3** — Crear `agent-dist/hooks/run-hook.cmd` — Polyglot Windows/Unix batch+shell script (adaptado de Superpowers). Permite que el hook funcione en Windows cmd, Git Bash y MSYS2.
  - Archivo: `agent-dist/hooks/run-hook.cmd`

- [ ] **T1.1.4** — Crear `agent-dist/hooks/hooks.json` — Config de hook para Claude Code/Generic: SessionStart en startup|clear|compact, async false.
  - Archivo: `agent-dist/hooks/hooks.json`

- [ ] **T1.1.5** — Crear `agent-dist/hooks/hooks-cursor.json` — Config de hook para Cursor: sessionStart, version 1.
  - Archivo: `agent-dist/hooks/hooks-cursor.json`

- [ ] **T1.1.6** — Crear `agent-dist/hooks/hooks-opencode.json` — Config de hook para OpenCode.
  - Archivo: `agent-dist/hooks/hooks-opencode.json`

- [ ] **T1.1.7** — Crear `agent-dist/plugins/opencode/quinotospec-plugin.js` — Plugin JS para OpenCode:
  - `config` hook: registra paths de skills/workflows/rules/agents en config vivo
  - `experimental.chat.messages.transform` hook: inyecta bootstrap en primer user message
  - Cache a nivel de modulo (leer bootstrap una sola vez)
  - Injection guard: no inyectar si ya esta presente
  - Tool mapping: `TodoWrite` → `todowrite`, `Task` → subagentes
  - Archivo: `agent-dist/plugins/opencode/quinotospec-plugin.js`

- [ ] **T1.1.8** — Crear `.cursor-plugin/plugin.json` — Plugin manifest para Cursor con paths a skills, agents, commands, hooks.
  - Archivo: `.cursor-plugin/plugin.json`

- [ ] **T1.1.9** — Actualizar `install.sh` — Agregar soporte para:
  - Copiar `agent-dist/hooks/` al directorio de config del IDE
  - Copiar `agent-dist/plugins/` para OpenCode
  - Copiar `.cursor-plugin/plugin.json` para Cursor
  - Registrar hooks en config del IDE
  - Archivo: `install.sh`

- [ ] **T1.1.10** — Actualizar `manifest.json` — Agregar `bootstrap`, `hooks`, `plugins` a directories. Bump version a 3.0.0.
  - Archivo: `manifest.json`

- [ ] **T1.1.11** — Actualizar `AGENTS.md` — Referenciar que el bootstrap ahora es automatico, pero mantener AGENTS.md como referencia offline.
  - Archivo: `AGENTS.md`

---

### F1.2 — Skill de Test-Driven Development con Enforcement

| Campo | Detalle |
|-------|---------|
| **Fuente** | Superpowers (`skills/test-driven-development/SKILL.md`) |
| **Problema actual** | QuinotoSpec menciona ejecutar tests en apply pero no fuerza TDD. Sin enforcement |
| **Solucion** | Skill dedicado con Iron Law, Red-Green-Refactor, anti-racionalizaciones, y tabla de Red Flags |

#### Arquitectura

```
agent-dist/skills/quinotospec-tdd/
├── SKILL.md                    # Skill principal TDD
├── testing-anti-patterns.md    # Referencia de anti-patrones
└── examples/
    ├── tdd-typescript.md       # Ejemplo en TypeScript
    ├── tdd-python.md           # Ejemplo en Python
    └── tdd-rust.md             # Ejemplo en Rust
```

#### Contenido del SKILL.md

Estructura adaptada de Superpowers:

1. **Iron Law:** "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST"
2. **Red-Green-Refactor Cycle:**
   - RED: Escribir test minimo, verlo fallar (MANDATORY)
   - GREEN: Escribir codigo minimo para pasar
   - REFACTOR: Limpiar sin cambiar comportamiento
3. **Tabla de Racionalizaciones:** 12 excusas comunes y por que son falsas
4. **Red Flags Table:** 12 senales de que se esta violando TDD
5. **Verification Checklist:** 8 items que deben cumplirse antes de marcar completo
6. **When Stuck:** Que hacer cuando no sabes como testear
7. **Debugging Integration:** Bugs → failing test → TDD cycle → fix + regression test
8. **Testing Anti-Patterns Reference:** Link a `testing-anti-patterns.md`

#### Integracion con Workflows Existentes

- `quinotospec.apply`: Agregar gate pre-implementacion que invoque `quinotospec-tdd`
- `quinotospec-rules`: Agregar regla #13 "TDD Enforcement" con severidad STANDARD

#### Tareas

- [ ] **T1.2.1** — Crear `agent-dist/skills/quinotospec-tdd/SKILL.md` — Skill TDD completo con Iron Law, ciclo Red-Green-Refactor, tabla de racionalizaciones (12 entradas), tabla de Red Flags (12 entradas), verification checklist (8 items), seccion "When Stuck", integracion con debugging.
  - Archivo: `agent-dist/skills/quinotospec-tdd/SKILL.md`

- [ ] **T1.2.2** — Crear `agent-dist/skills/quinotospec-tdd/testing-anti-patterns.md` — Referencia de anti-patrones: testing mock behavior vs real behavior, test-only methods in production, mocking without understanding dependencies, testing implementation details, over-mocking, slow tests, flaky tests, test interdependence.
  - Archivo: `agent-dist/skills/quinotospec-tdd/testing-anti-patterns.md`

- [ ] **T1.2.3** — Crear `agent-dist/skills/quinotospec-tdd/examples/tdd-typescript.md` — Ejemplo completo RED-GREEN-REFACTOR en TypeScript con Jest.
  - Archivo: `agent-dist/skills/quinotospec-tdd/examples/tdd-typescript.md`

- [ ] **T1.2.4** — Crear `agent-dist/skills/quinotospec-tdd/examples/tdd-python.md` — Ejemplo completo RED-GREEN-REFACTOR en Python con pytest.
  - Archivo: `agent-dist/skills/quinotospec-tdd/examples/tdd-python.md`

- [ ] **T1.2.5** — Actualizar `agent-dist/rules/quinotospec-rules.md` — Agregar regla #13 "TDD Enforcement" (STANDARD): "Todo codigo de produccion DEBE tener un test que falle antes de ser escrito. El skill quinotospec-tdd DEBE ejecutarse antes de cualquier implementacion."
  - Archivo: `agent-dist/rules/quinotospec-rules.md`

- [ ] **T1.2.6** — Actualizar `agent-dist/workflows/quinotospec.apply.md` — Agregar gate pre-implementacion: "Antes de escribir codigo, ejecuta el skill `quinotospec-tdd`. Si no hay un test que falle, no puedes escribir codigo de produccion."
  - Archivo: `agent-dist/workflows/quinotospec.apply.md`

- [ ] **T1.2.7** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar quinotospec-tdd en la lista de skills esenciales.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F1.3 — Skill de Debugging Sistematico

| Campo | Detalle |
|-------|---------|
| **Fuente** | Superpowers (`skills/systematic-debugging/SKILL.md`) |
| **Problema actual** | QuinotoSpec no tiene metodologia de debugging. El agente hace fixes ad-hoc |
| **Solucion** | Skill con proceso de 4 fases, root cause tracing, y regla "3+ fixes failed → question architecture" |

#### Arquitectura

```
agent-dist/skills/quinotospec-debug/
├── SKILL.md                    # Skill principal de debugging
├── root-cause-tracing.md       # Tecnica: trace bugs backward through call stack
├── defense-in-depth.md         # Tecnica: add validation at multiple layers
└── condition-based-waiting.md  # Tecnica: replace arbitrary timeouts with condition polling
```

#### Contenido del SKILL.md

1. **Iron Law:** "NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST"
2. **Phase 1 — Root Cause Investigation:**
   - Read error messages carefully
   - Reproduce consistently
   - Check recent changes
   - Gather evidence in multi-component systems
   - Trace data flow (link a `root-cause-tracing.md`)
3. **Phase 2 — Pattern Analysis:**
   - Find working examples in same codebase
   - Compare against references
   - Identify differences
   - Understand dependencies
4. **Phase 3 — Hypothesis and Testing:**
   - Form single hypothesis
   - Test minimally (one variable)
   - Verify before continuing
   - When you don't know, say so
5. **Phase 4 — Implementation:**
   - Create failing test case
   - Implement single fix
   - Verify fix
   - If 3+ fixes failed → question architecture
6. **Supporting Techniques** (sub-archivos)
7. **Tabla de Racionalizaciones:** 8 excusas comunes
8. **Red Flags Table:** 12 senales de debugging ad-hoc

#### Tareas

- [ ] **T1.3.1** — Crear `agent-dist/skills/quinotospec-debug/SKILL.md` — Skill de debugging con Iron Law, 4 fases, regla "3+ fixes → question architecture", tabla de racionalizaciones (8 entradas), Red Flags (11 entradas), integracion con TDD.
  - Archivo: `agent-dist/skills/quinotospec-debug/SKILL.md`

- [ ] **T1.3.2** — Crear `agent-dist/skills/quinotospec-debug/root-cause-tracing.md` — Tecnica de trazado hacia atras: encontrar donde se origina el valor incorrecto, seguir la traza del call stack hasta la fuente, fijar en la fuente no en el sintoma.
  - Archivo: `agent-dist/skills/quinotospec-debug/root-cause-tracing.md`

- [ ] **T1.3.3** — Crear `agent-dist/skills/quinotospec-debug/defense-in-depth.md` — Tecnica: agregar validacion en multiples capas despues de encontrar root cause para prevenir recurrencia.
  - Archivo: `agent-dist/skills/quinotospec-debug/defense-in-depth.md`

- [ ] **T1.3.4** — Crear `agent-dist/skills/quinotospec-debug/condition-based-waiting.md` — Tecnica: reemplazar timeouts arbitrarios con polling basado en condiciones (evita tests flaky).
  - Archivo: `agent-dist/skills/quinotospec-debug/condition-based-waiting.md`

- [ ] **T1.3.5** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar quinotospec-debug.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F1.4 — Skill de Verificacion Antes de Completar

| Campo | Detalle |
|-------|---------|
| **Fuente** | Superpowers (`skills/verification-before-completion/SKILL.md`) |
| **Problema actual** | El agente puede declarar tareas completadas sin evidencia |
| **Solucion** | Gate function (IDENTIFY → RUN → READ → VERIFY) que bloquea claims sin evidencia fresca |

#### Arquitectura

```
agent-dist/skills/quinotospec-verify-before-done/
└── SKILL.md    # Skill unico, auto-contenido
```

#### Contenido del SKILL.md

1. **Iron Law:** "NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE"
2. **The Gate Function:**
   ```
   1. IDENTIFY: What command proves this claim?
   2. RUN: Execute the FULL command
   3. READ: Full output, check exit code
   4. VERIFY: Does output confirm the claim?
   5. ONLY THEN: Make the claim
   ```
3. **Common Failures Table:** Tests pass → requires test command output, Linter clean → requires linter output, etc.
4. **Red Flags:** "should", "probably", "seems to", expresar satisfaccion antes de verificar
5. **Tabla de Racionalizaciones:** 7 excusas comunes

#### Integracion

- `quinotospec-mark-done`: Agregar gate de verificacion antes de marcar
- `quinotospec-apply`: Agregar verificacion antes de declarar tarea completada

#### Tareas

- [ ] **T1.4.1** — Crear `agent-dist/skills/quinotospec-verify-before-done/SKILL.md` — Skill con Iron Law, Gate Function (5 pasos), Common Failures table, Red Flags (8 items), Rationalization Prevention (7 excusas).
  - Archivo: `agent-dist/skills/quinotospec-verify-before-done/SKILL.md`

- [ ] **T1.4.2** — Actualizar `agent-dist/skills/quinotospec-mark-done/SKILL.md` — Agregar paso: "Antes de marcar como completada, ejecuta `quinotospec-verify-before-done` para confirmar que la tarea fue realmente completada."
  - Archivo: `agent-dist/skills/quinotospec-mark-done/SKILL.md`

- [ ] **T1.4.3** — Actualizar `agent-dist/workflows/quinotospec.apply.md` — Agregar verificacion antes de Mark Done.
  - Archivo: `agent-dist/workflows/quinotospec.apply.md`

- [ ] **T1.4.4** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar quinotospec-verify-before-done.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F1.5 — Constitution del Proyecto

| Campo | Detalle |
|-------|---------|
| **Fuente** | Spec-Kit (`.specify/memory/constitution.md`, `/speckit.constitution`) |
| **Problema actual** | QuinotoSpec tiene 12 reglas de gobernanza pero no una "constitucion fundacional" que guie todas las decisiones de arquitectura e implementacion |
| **Solucion** | Workflow `/quinotospec.constitution` que crea `.quinoto-spec/constitution.md` con principios fundacionales que todos los workflows respetan |

#### Arquitectura

```
agent-dist/workflows/quinotospec.constitution.md    # Workflow para crear/editar
agent-dist/templates/constitution-template.md       # Template con placeholders
```

#### Contenido del Template

```markdown
# Constitucion del Proyecto — {{PROJECT_NAME}}

## Principios Fundamentales

### I. Calidad de Codigo
...

### II. Estandares de Testing
...

### III. Consistencia de UX
...

### IV. Requisitos de Performance
...

## Restricciones Adicionales

### Seguridad
...

### Cumplimiento Normativo
...

## Flujo de Desarrollo

### Proceso de Review
...

### Quality Gates
...

## Gobernanza

- Esta constitucion supersede cualquier otra practica
- Enmiendas requieren: documentacion, revision, aprobacion
- Todos los PRs deben verificar compliance
- La complejidad debe ser justificada
```

#### Tareas

- [ ] **T1.5.1** — Crear `agent-dist/templates/constitution-template.md` — Template con secciones: Principios Fundamentales, Restricciones Adicionales (seguridad, compliance, performance), Flujo de Desarrollo (review process, quality gates), Gobernanza. Con placeholders `{{PROJECT_NAME}}`, `{{STACK}}`, etc.
  - Archivo: `agent-dist/templates/constitution-template.md`

- [ ] **T1.5.2** — Crear `agent-dist/workflows/quinotospec.constitution.md` — Workflow que:
  - Pregunta por principios de codigo, testing, UX y performance
  - Genera `.quinoto-spec/constitution.md` desde el template
  - Integra con el discovery existente para stack-specific defaults
  - Valida que la constitucion sea consistente con las reglas existentes
  - Archivo: `agent-dist/workflows/quinotospec.constitution.md`

- [ ] **T1.5.3** — Actualizar `agent-dist/workflows/quinotospec.review.md` — Agregar validacion de compliance constitucional en el checklist de revision.
  - Archivo: `agent-dist/workflows/quinotospec.review.md`

- [ ] **T1.5.4** — Actualizar `agent-dist/workflows/quinotospec.apply.md` — Agregar gate: "Verifica que la implementacion respeta la constitucion en `.quinoto-spec/constitution.md`"
  - Archivo: `agent-dist/workflows/quinotospec.apply.md`

- [ ] **T1.5.5** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar `/quinotospec.constitution`.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F1.6 — Code Review: Recepcion de Feedback

| Campo | Detalle |
|-------|---------|
| **Fuente** | Superpowers (`skills/receiving-code-review/SKILL.md`) |
| **Problema actual** | QuinotoSpec tiene `quinotospec.review` (emitir review) pero no tiene protocolo para recibir feedback |
| **Solucion** | Skill `quinotospec-receive-review` con reglas: no performative agreement, verify before implement, YAGNI check |

#### Tareas

- [ ] **T1.6.1** — Crear `agent-dist/skills/quinotospec-receive-review/SKILL.md` — Skill con:
  - Response Pattern (6 pasos: READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT)
  - Forbidden Responses (performative agreement prohibido)
  - Source-Specific Handling (human partner vs external reviewer)
  - YAGNI Check: "If reviewer suggests 'implementing properly', grep codebase for actual usage first"
  - When to Push Back: suggestion breaks existing functionality, lacks context, violates YAGNI
  - How to Push Back: technical reasoning, not defensiveness
  - Acknowledging Correct Feedback: "Fixed. [Brief description]" — no thanks, no flattery
  - Archivo: `agent-dist/skills/quinotospec-receive-review/SKILL.md`

- [ ] **T1.6.2** — Actualizar `agent-dist/workflows/quinotospec.review.md` — Agregar referencia a `quinotospec-receive-review` para cuando el agente recibe feedback.
  - Archivo: `agent-dist/workflows/quinotospec.review.md`

---

### F1.7 — Git Worktrees para Aislamiento

| Campo | Detalle |
|-------|---------|
| **Fuente** | Superpowers (`skills/using-git-worktrees/SKILL.md`) |
| **Problema actual** | QuinotoSpec no aisla el workspace durante la implementacion |
| **Solucion** | Skill `quinotospec-worktree` con isolation detection, preferencia por herramientas nativas, fallback a git worktree |

#### Tareas

- [ ] **T1.7.1** — Crear `agent-dist/skills/quinotospec-worktree/SKILL.md` — Skill con:
  - Step 0: Detect Existing Isolation (`GIT_DIR != GIT_COMMON`)
  - Step 1: Native Worktree Tools (preferred)
  - Step 2: Git Worktree Fallback
  - Directory Priority: `.worktrees/` > `worktrees/` > `~/.config/quinotospec/worktrees/`
  - Safety Verification: `git check-ignore` antes de crear
  - Project Setup: auto-detectar stack y ejecutar install
  - Verify Clean Baseline: correr tests
  - Sandbox fallback si hay permission error
  - Archivo: `agent-dist/skills/quinotospec-worktree/SKILL.md`

- [ ] **T1.7.2** — Actualizar `agent-dist/workflows/quinotospec.apply.md` — Agregar opcion de crear worktree antes de implementar.
  - Archivo: `agent-dist/workflows/quinotospec.apply.md`

---

### F1.8 — Actualizaciones de Infraestructura

#### Tareas

- [ ] **T1.8.1** — Actualizar `agent-dist/rules/quinotospec-rules.md` — Agregar nuevas reglas:
  - Regla #13: TDD Enforcement (STANDARD)
  - Regla #14: Debugging Root Cause First (STANDARD)
  - Regla #15: Verification Before Completion (STANDARD)
  - Regla #16: Constitutional Compliance (BLOCKING para merge)
  - Archivo: `agent-dist/rules/quinotospec-rules.md`

- [ ] **T1.8.2** — Actualizar `manifest.json` — Bump a 3.0.0, actualizar conteos (skills: +6 = 33, workflows: +2 = 35, rules: +4 = 16), agregar nuevos directorios.
  - Archivo: `manifest.json`

- [ ] **T1.8.3** — Actualizar `.version` — `3.0.0`.
  - Archivo: `.version`

- [ ] **T1.8.4** — Actualizar `CHANGELOG.md` — Entrada v3.0.0 documentando todos los features de Fase 1.
  - Archivo: `CHANGELOG.md`

- [ ] **T1.8.5** — Actualizar `README.md` y `README_EN.md` — Nuevos workflows y skills.
  - Archivos: `README.md`, `README_EN.md`

- [ ] **T1.8.6** — Actualizar `docs/ARCHITECTURE.md` — Nuevo diagrama con bootstrap, hooks, plugins.
  - Archivo: `docs/ARCHITECTURE.md`

- [ ] **T1.8.7** — Actualizar `scripts/validate-all.sh` — Ajustar conteos esperados (workflows >= 35, skills >= 33, rules >= 16).
  - Archivo: `scripts/validate-all.sh`

---

## Fase 2 — Extensibilidad (v3.1.0)

**Objetivo:** Transformar QuinotoSpec de un monolito a una plataforma extensible. Introducir sistema de extensiones/presets, artifact DAG engine, delta specs, y `AGENTS.md` generado dinamicamente.

**Fuentes principales:** Spec-Kit (60%), OpenSpec (40%)

---

### F2.1 — Delta Specs (ADDED/MODIFIED/REMOVED)

| Campo | Detalle |
|-------|---------|
| **Fuente** | OpenSpec (`openspec/changes/<name>/specs/`) |
| **Problema actual** | Las propuestas de QuinotoSpec reescriben la especificacion completa. En brownfield, esto es inmanejable |
| **Solucion** | Las propuestas expresan solo el delta: que se agrega, modifica, elimina, renombra. El engine de archive aplica el delta a la spec principal |

#### Arquitectura

```
.quinoto-spec/
├── specs/                          # Source of truth — specs actuales del sistema
│   └── <domain>/
│       └── spec.md                 # Requerimientos + escenarios en GIVEN/WHEN/THEN
│
├── proposals/
│   └── <DATE>-<slug>/
│       ├── proposal.md             # Why + What + Scope
│       ├── delta-specs/            # DELTA (no specs completas)
│       │   └── <domain>/
│       │       └── spec.md         # ADDED / MODIFIED / REMOVED / RENAMED
│       ├── user-stories.md
│       ├── design.md               # How (arquitectura, decisiones tecnicas)
│       └── <US_ID>_tasks.md
│
├── constitution.md                 # Principios fundacionales (de F1.5)
└── config.yaml                     # Config del proyecto (schema, contexto AI)
```

#### Formato de Delta Spec

```markdown
# Delta Spec: Auth — {{PROPOSAL_SLUG}}

## ADDED Requirements

### Requirement: Two-Factor Authentication
The system MUST support TOTP-based 2FA.
The system SHALL send backup codes on first enable.

#### Scenario: User enables 2FA
- **GIVEN** a user with valid credentials
- **WHEN** they enable two-factor authentication
- **THEN** a TOTP secret is generated
- **AND** backup codes are displayed

## MODIFIED Requirements

### Requirement: Session Expiration
The system MUST expire sessions after 15 minutes.
**Was:** 30 minutes.
**Reason:** Security compliance requires shorter sessions.

## REMOVED Requirements

### Requirement: Remember Me
**Reason:** Deprecated in favor of 2FA persistence.
**Migration:** Users must re-authenticate each session. Affected endpoints: /login, /refresh.

## RENAMED Requirements

### Requirement: Auth Token → Access Token
**Reason:** Clarifies distinction from refresh tokens.
```

#### Engine de Archive

Al ejecutar `/quinotospec.archive`:
1. Leer `delta-specs/` de la propuesta
2. Para cada dominio:
   - ADDED: Append al final de `specs/<domain>/spec.md`
   - MODIFIED: Reemplazar bloque existente por nuevo contenido
   - REMOVED: Eliminar bloque de `specs/<domain>/spec.md`
   - RENAMED: Renombrar seccion
3. Mover propuesta a `proposals/_archived/`

#### Tareas

- [x] **T2.1.1** — Actualizar `agent-dist/workflows/quinotospec.create-proposal.md` ✅ (v2.2.0)
  - Archivo: `agent-dist/workflows/quinotospec.create-proposal.md`

- [x] **T2.1.2** — Crear `agent-dist/templates/delta-spec-template.md` ✅ (v2.2.0)
  - Archivo: `agent-dist/templates/delta-spec-template.md`

- [x] **T2.1.3** — Actualizar `agent-dist/workflows/quinotospec.archive.md` ✅ (v2.2.0)
  - Archivo: `agent-dist/workflows/quinotospec.archive.md`

- [x] **T2.1.4** — Crear `agent-dist/workflows/quinotospec.specs-init.md` ✅ (v2.2.0)
  - Archivo: `agent-dist/workflows/quinotospec.specs-init.md`

- [x] **T2.1.5** — Actualizar `agent-dist/workflows/quinotospec.init.md` ✅ (v2.2.0)
  - Archivo: `agent-dist/workflows/quinotospec.init.md`

---

### F2.2 — Artifact Dependency Graph Engine

| Campo | Detalle |
|-------|---------|
| **Fuente** | OpenSpec (schema YAML con artifact DAG, topological sort) |
| **Problema actual** | Las dependencias entre artefactos son implicitas y no validadas |
| **Solucion** | YAML schema que define formalmente los artefactos, sus dependencias, y que genera cada uno. El engine calcula que esta listo y que esta bloqueado |

#### Arquitectura

```yaml
# .quinoto-spec/schema.yaml
name: quinotospec-default
version: 1
description: Default QuinotoSpec workflow

artifacts:
  - id: proposal
    generates: proposals/{slug}/proposal.md
    requires: []
    template: proposal-template.md
    instruction: "Create a technical proposal..."

  - id: delta-specs
    generates: proposals/{slug}/delta-specs/**/*.md
    requires: [proposal]
    template: delta-spec-template.md
    instruction: "Define delta specs..."

  - id: design
    generates: proposals/{slug}/design.md
    requires: [proposal]
    template: design-template.md
    instruction: "Define technical architecture..."

  - id: user-stories
    generates: proposals/{slug}/user-stories.md
    requires: [delta-specs, design]
    template: user-stories-template.md
    instruction: "Break down into user stories..."

  - id: tasks
    generates: proposals/{slug}/*_tasks.md
    requires: [user-stories]
    template: tasks-template.md
    instruction: "Create implementation tasks..."

apply:
  requires: [tasks]
  tracks: proposals/{slug}/*_tasks.md
```

#### Comportamiento del Engine

- `openspec status --change <slug> --json` retorna: `{artifacts: [{id, status: done|ready|blocked}]}`
- `openspec instructions proposal --change <slug> --json` retorna instrucciones enriquecidas con contexto del proyecto
- El engine valida que no se creen artefactos cuyas dependencias no existen

#### Tareas

- [x] **T2.2.1** — Crear `agent-dist/skills/quinotospec-artifact-engine/SKILL.md` ✅ (v2.3.0)
  - Archivo: `agent-dist/skills/quinotospec-artifact-engine/SKILL.md`

- [x] **T2.2.2** — Crear `agent-dist/templates/schema-template.yaml` ✅ (v2.3.0)
  - Archivo: `agent-dist/templates/schema-template.yaml`

- [x] **T2.2.3** — Actualizar `agent-dist/workflows/quinotospec.init.md` ✅ (v2.3.0)
  - Archivo: `agent-dist/workflows/quinotospec.init.md`

- [x] **T2.2.4** — Actualizar `agent-dist/workflows/quinotospec.status.md` ✅ (v2.3.0)
  - Archivo: `agent-dist/workflows/quinotospec.status.md`

- [x] **T2.2.5** — Crear `agent-dist/workflows/quinotospec.schema-fork.md` ✅ (v2.3.0)
  - Archivo: `agent-dist/workflows/quinotospec.schema-fork.md`

---

### F2.3 — Sistema de Extensiones

| Campo | Detalle |
|-------|---------|
| **Fuente** | Spec-Kit (`extensions/`, sistema de 4-layer resolution) |
| **Problema actual** | QuinotoSpec es un monolito. No se puede extender sin modificar el core |
| **Solucion** | Sistema de extensiones con manifest YAML, hooks, y 4-layer template resolution |

#### Arquitectura

```
.quinoto-spec/
├── extensions/                     # Extensiones instaladas
│   ├── .registry                   # Registro de extensiones instaladas
│   └── <ext-id>/                   # Una extension
│       ├── extension.yml           # Manifest
│       ├── commands/               # Workflows que agrega
│       ├── skills/                 # Skills que agrega
│       ├── templates/              # Templates a resolver
│       └── config-template.yml     # Config default
│
├── overrides/                      # Project-local overrides (maxima prioridad)
│   ├── workflows/
│   ├── skills/
│   └── templates/
│
├── presets/                        # Presets instalados
│   └── <preset-id>/
│       ├── preset.yml
│       └── templates/
│
└── templates/                      # Core templates (minima prioridad)
    └── ...
```

#### Priority Resolution Stack

```
Priority 1 (HIGHEST): .quinoto-spec/overrides/
Priority 2:           .quinoto-spec/presets/<id>/ (sorted by priority, lower = higher)
Priority 3:           .quinoto-spec/extensions/<id>/
Priority 4 (LOWEST):  agent-dist/templates/ (core)
```

Las templates se resuelven en runtime. Los commands/skills se aplican en install time.

#### Extension Manifest (`extension.yml`)

```yaml
schema_version: 1
extension:
  id: quinotospec-jira
  name: Jira Integration
  version: 1.0.0
  description: Sync tasks with Jira issues
requires:
  quinotospec_version: ">=3.1.0"
provides:
  commands: [jira-sync, jira-status]
  skills: [quinotospec-jira-sync]
  hooks: [after_tasks, before_archive]
hooks:
  after_tasks:
    - command: jira-sync
      priority: 100
      auto: false
  before_archive:
    - command: jira-status
      priority: 200
      auto: true
```

#### Hook Points (17)

`before_proposal`, `after_proposal`, `before_delta_specs`, `after_delta_specs`, `before_user_stories`, `after_user_stories`, `before_design`, `after_design`, `before_tasks`, `after_tasks`, `before_apply`, `after_apply`, `before_review`, `after_review`, `before_archive`, `after_archive`, `before_constitution`, `after_constitution`

#### Tareas

- [ ] **T2.3.1** — Crear `agent-dist/skills/quinotospec-extension-manager/SKILL.md` — Skill que gestiona el ciclo de vida de extensiones: search, install, update, remove, list, info. Con soporte para catalog.json (curado) y catalog.community.json (descubrimiento).
  - Archivo: `agent-dist/skills/quinotospec-extension-manager/SKILL.md`

- [ ] **T2.3.2** — Crear `agent-dist/templates/extension-template.yml` — Template para crear nuevas extensiones.
  - Archivo: `agent-dist/templates/extension-template.yml`

- [ ] **T2.3.3** — Crear `agent-dist/templates/preset-template.yml` — Template para crear nuevos presets.
  - Archivo: `agent-dist/templates/preset-template.yml`

- [ ] **T2.3.4** — Crear `agent-dist/skills/quinotospec-template-resolver/SKILL.md` — Skill que implementa la 4-layer resolution stack: busca un template/command/skill caminando overrides → presets → extensions → core y retorna el primero que encuentra.
  - Archivo: `agent-dist/skills/quinotospec-template-resolver/SKILL.md`

- [ ] **T2.3.5** — Crear `agent-dist/workflows/quinotospec.extension-install.md` — Workflow para instalar una extension desde catalog o local.
  - Archivo: `agent-dist/workflows/quinotospec.extension-install.md`

- [ ] **T2.3.6** — Crear `agent-dist/workflows/quinotospec.preset-install.md` — Workflow para instalar un preset.
  - Archivo: `agent-dist/workflows/quinotospec.preset-install.md`

- [ ] **T2.3.7** — Actualizar workflows existentes para soportar hooks: agregar `before_*` y `after_*` hook execution en cada workflow del core.
  - Archivos: `quinotospec.create-proposal.md`, `quinotospec.create-user-stories.md`, `quinotospec.create-tasks.md`, `quinotospec.apply.md`, `quinotospec.review.md`, `quinotospec.archive.md`

- [ ] **T2.3.8** — Crear `extensions/catalog.json` — Catalog inicial vacio (curado).
  - Archivo: `extensions/catalog.json`

- [ ] **T2.3.9** — Crear `extensions/catalog.community.json` — Catalog de extensiones comunitarias (vacio inicialmente, para descubrimiento).
  - Archivo: `extensions/catalog.community.json`

- [ ] **T2.3.10** — Crear `extensions/EXTENSION-DEVELOPMENT-GUIDE.md` — Guia para desarrolladores de extensiones.
  - Archivo: `extensions/EXTENSION-DEVELOPMENT-GUIDE.md`

---

### F2.4 — `AGENTS.md` Generado Dinamicamente

| Campo | Detalle |
|-------|---------|
| **Fuente** | OpenSpec (`openspec update`) |
| **Problema actual** | `AGENTS.md` es un archivo estatico copiado por `install.sh`. Si el proyecto cambia, el AGENTS.md queda desactualizado |
| **Solucion** | `AGENTS.md` se genera dinamicamente desde `.quinoto-spec/config.yaml`, reflejando el estado real del proyecto |

#### Arquitectura

```yaml
# .quinoto-spec/config.yaml
project:
  name: my-project
  stack: node-express
  language: typescript
  
context:
  tech_stack: "Node.js 20, Express, TypeScript, PostgreSQL"
  conventions: "Conventional commits, ESLint, Prettier"
  testing: "Jest, supertest for integration tests"
  
workflows:
  active: [constitution, discovery, proposal, user-stories, tasks, apply, review, archive]
  optional: [battle-frenzy, heimdallr, mjolnir-refactor]
  
rules:
  strictness: standard  # standard | strict | permissive
  
extensions:
  - quinotospec-jira
  - quinotospec-diagram
```

El comando `/quinotospec.update-agents` regenera `AGENTS.md` combinando:
1. `config.yaml` del proyecto
2. Lista de workflows/skills/rules activos
3. Extensiones instaladas
4. Stack-specific defaults desde discovery
5. Customizaciones del usuario

#### Tareas

- [ ] **T2.4.1** — Crear `agent-dist/workflows/quinotospec.update-agents.md` — Workflow que regenera `AGENTS.md` desde `config.yaml`, listando workflows activos, skills, reglas, extensiones, y stack-specific defaults.
  - Archivo: `agent-dist/workflows/quinotospec.update-agents.md`

- [ ] **T2.4.2** — Crear `agent-dist/templates/AGENTS-template.md` — Template con placeholders `{{PROJECT_NAME}}`, `{{STACK}}`, `{{WORKFLOWS}}`, `{{SKILLS}}`, `{{RULES}}`, `{{EXTENSIONS}}`.
  - Archivo: `agent-dist/templates/AGENTS-template.md`

- [ ] **T2.4.3** — Actualizar `agent-dist/workflows/quinotospec.init.md` — Generar `config.yaml` inicial y `AGENTS.md` desde template.
  - Archivo: `agent-dist/workflows/quinotospec.init.md`

- [ ] **T2.4.4** — Actualizar `install.sh` — En lugar de copiar AGENTS.md estatico, ejecutar update-agents.
  - Archivo: `install.sh`

---

### F2.5 — Actualizaciones de Infraestructura (Fase 2)

#### Tareas

- [ ] **T2.5.1** — Actualizar `manifest.json` — Bump a 3.1.0, actualizar conteos (skills: +3 = 36, workflows: +8 = 43, templates: +5).
  - Archivo: `manifest.json`

- [ ] **T2.5.2** — Actualizar `.version` — `3.1.0`.
  - Archivo: `.version`

- [ ] **T2.5.3** — Actualizar `CHANGELOG.md` — Entrada v3.1.0.
  - Archivo: `CHANGELOG.md`

- [ ] **T2.5.4** — Actualizar `scripts/validate-all.sh` — Ajustar conteos.
  - Archivo: `scripts/validate-all.sh`

- [ ] **T2.5.5** — Actualizar `CONTRIBUTING.md` — Agregar seccion "Desarrollo de Extensiones" y "Desarrollo de Presets".
  - Archivo: `CONTRIBUTING.md`

---

## Fase 3 — Agentes y Coordinacion (v3.2.0)

**Objetivo:** Transformar los agentes de QuinotoSpec en personas con identidad, comportamiento customizable, y capacidad de interactuar en mesa redonda.

**Fuentes principales:** BMAD-METHOD (100%)

---

### F3.1 — Agentes con Personalidad y Customizacion

| Campo | Detalle |
|-------|---------|
| **Fuente** | BMAD-METHOD (named agents + 3-layer TOML merge) |
| **Problema actual** | Los 9 agentes de QuinotoSpec son genericos, sin personalidad ni comportamiento customizable |
| **Solucion** | Agentes con nombre, titulo, personalidad, y sistema de customizacion 3-layer |

#### Arquitectura

```
agent-dist/agents/converted/
├── alba.md                    # Alba — Arquitecta de Sistemas
├── daniel.md                  # Daniel — Debugger Senior
├── eva.md                     # Eva — DevOps Engineer
├── lucas.md                   # Lucas — Code Reviewer
├── mateo.md                   # Mateo — Doc Writer
├── nora.md                    # Nora — Performance Optimizer
├── raul.md                    # Raul — Refactor Specialist
├── sofia.md                   # Sofia — Security Auditor
└── victor.md                  # Victor — Test Writer
```

#### Estructura de Agente (nuevo formato)

```markdown
---
name: alba
display_name: Alba
title: Arquitecta de Sistemas
specialization: Diseno de sistemas, patrones de arquitectura, decisiones tecnicas
trigger_workflows:
  - quinotospec.create-proposal
  - quinotospec.create-rfc
model_suggestion: claude-opus-4-5
personality: |
  Favorable al aburrimiento tecnologico. Prefiere soluciones probadas sobre lo nuevo.
  Trade-offs sobre veredictos. Cada decision vinculada a valor de negocio.
  Pragmatica, no dogmatica. "Depende" es su respuesta favorita (con contexto).
principles:
  - "Elige tecnologia aburrida sobre novedosa, a menos que haya razon de peso"
  - "Cada decision de arquitectura debe estar vinculada a un objetivo de negocio"
  - "Un monolith bien disenado es mejor que microservicios mal implementados"
  - "La simplicidad es la maxima sofisticacion"
communication_style:
  tone: profesional, directo
  language: espanol
  diagram_preference: mermaid
  verbosity: medio
---

# Alba — Arquitecta de Sistemas

## Personalidad
...
```

#### Sistema de Customizacion 3-Layer

```
.quinoto-spec/
├── _config/
│   ├── agent-defaults.toml        # Defaults shipped (NO editar)
│   ├── agent-team.toml            # Team overrides (versionado)
│   └── agent-personal.toml        # Personal overrides (.gitignored)
```

Merge: `defaults → team → personal` (ultimo gana). Los agentes leen la config mergeada al activarse.

#### Tareas

- [ ] **T3.1.1** — Convertir los 9 agentes existentes de formato generico a formato con personalidad:
  - Renombrar con nombres humanos (Alba, Daniel, Eva, Lucas, Mateo, Nora, Raul, Sofia, Victor)
  - Agregar campos: `display_name`, `title`, `personality`, `principles`, `communication_style`
  - Agregar secciones: Personalidad, Filosofia de Trabajo, Reglas Personales, Protocolo de Comunicacion
  - Archivos: `agent-dist/agents/converted/alba.md`, `daniel.md`, `eva.md`, `lucas.md`, `mateo.md`, `nora.md`, `raul.md`, `sofia.md`, `victor.md`

- [ ] **T3.1.2** — Crear `agent-dist/templates/agent-defaults.toml` — Config defaults para los 9 agentes con personalidades, principios, y estilos de comunicacion.
  - Archivo: `agent-dist/templates/agent-defaults.toml`

- [ ] **T3.1.3** — Crear `agent-dist/skills/quinotospec-agent-config/SKILL.md` — Skill que:
  - Lee `agent-defaults.toml` + `agent-team.toml` + `agent-personal.toml`
  - Hace merge 3-layer (defaults → team → personal)
  - Aplica la config mergeada a la sesion del agente
  - Soporta hot-reload (cambios en TOML se reflejan sin reiniciar)
  - Archivo: `agent-dist/skills/quinotospec-agent-config/SKILL.md`

- [ ] **T3.1.4** — Crear `agent-dist/skills/quinotospec-agent-customize/SKILL.md` — Skill que permite al usuario describir en lenguaje natural como quiere modificar un agente y genera el TOML correcto. Sin editar archivos a mano.
  - Archivo: `agent-dist/skills/quinotospec-agent-customize/SKILL.md`

- [ ] **T3.1.5** — Crear `agent-dist/workflows/quinotospec.agent-configure.md` — Workflow interactivo que guia al usuario en la customizacion de agentes.
  - Archivo: `agent-dist/workflows/quinotospec.agent-configure.md`

- [ ] **T3.1.6** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Listar agentes con sus nombres y especialidades.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F3.2 — Party Mode (Mesa Redonda Multi-Agente)

| Campo | Detalle |
|-------|---------|
| **Fuente** | BMAD-METHOD (`bmad-party-mode`) |
| **Problema actual** | Battle Frenzy ejecuta agentes en paralelo pero sin interaccion cualitativa entre ellos |
| **Solucion** | Party Mode: mesa redonda donde los agentes discuten, debaten, y colaboran en caracter |

#### Arquitectura

```
agent-dist/workflows/quinotospec.party-mode.md    # Workflow de mesa redonda
agent-dist/skills/quinotospec-party-orchestrator/  # Skill orquestador
├── SKILL.md
└── strategies/
    ├── voiced-by-orchestrator.md   # Estrategia 1: orquestador voicea a todos
    └── spawned-subagents.md        # Estrategia 2: subagentes independientes
```

#### Comportamiento

**Dos modos de ejecucion:**

1. **Voiced by Orchestrator** (default):
   - El agente principal voicea 2-4 personas en un intercambio fluido
   - Cada turno abre con `{icon} **{name}:**`
   - Turnos cortos, conversacion real (no reportes)
   - Las personas chocan — el consenso es un failure mode

2. **Spawned Subagents** (`--subagents`):
   - Subagentes genuinamente independientes
   - Se spawn en paralelo para first-takes independientes
   - Secuenciales cuando necesitan reaccionar a lo que otros dijeron
   - Para analisis profundo, revisiones honestas

**Reglas de diseno:**
- Nunca romper la 4ta pared ("tienes 4 agentes en la sala")
- Health monitoring: si todos estan de acuerdo → inyectar contrarian; si van en circulos → nombrar el impasse
- El usuario dirige: "Alba, ¿que opinas de lo que dijo Sofia?", "Trae a Victor", "Profundiza en eso, Daniel"
- Exit: usuario dice "gracias", "terminar party", "adios"

#### Tareas

- [x] **T3.2.1** — Crear `agent-dist/workflows/quinotospec.party-mode.md` ✅ (v2.4.0)
  - Archivo: `agent-dist/workflows/quinotospec.party-mode.md`

- [x] **T3.2.2** — Crear `agent-dist/skills/quinotospec-party-orchestrator/SKILL.md` ✅ (v2.4.0)
  - Archivo: `agent-dist/skills/quinotospec-party-orchestrator/SKILL.md`

- [x] **T3.2.3** — Crear `agent-dist/skills/quinotospec-party-orchestrator/strategies/voiced-by-orchestrator.md` ✅ (v2.4.0)
  - Archivo: `agent-dist/skills/quinotospec-party-orchestrator/strategies/voiced-by-orchestrator.md`

- [x] **T3.2.4** — Crear `agent-dist/skills/quinotospec-party-orchestrator/strategies/spawned-subagents.md` ✅ (v2.4.0)
  - Archivo: `agent-dist/skills/quinotospec-party-orchestrator/strategies/spawned-subagents.md`

- [ ] **T3.2.5** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar Party Mode.
  - **BLOQUEADO**: Bootstrap no existe (F1.1 sin implementar). Party Mode se descubre via AGENTS.md.

---

### F3.3 — Navegacion Contextual de Workflows

| Campo | Detalle |
|-------|---------|
| **Fuente** | BMAD-METHOD (`bmad-help`) |
| **Problema actual** | `quinotospec-suggest-next` solo funciona dentro de una propuesta. No hay navegacion global |
| **Solucion** | `quinotospec-help` escanea el proyecto completo y recomienda el proximo workflow |

#### Tareas

- [ ] **T3.3.1** — Crear `agent-dist/skills/quinotospec-help/SKILL.md` — Skill que:
  - Escanea `.quinoto-spec/` para detectar artifacts existentes
  - Mapea artifacts a fases del ciclo QuinotoSpec
  - Recomienda el proximo workflow basado en precedencia
  - Respeta gates obligatorios (required=true)
  - Soporta preguntas abiertas: "termine la arquitectura, ¿que sigue?"
  - Archivo: `agent-dist/skills/quinotospec-help/SKILL.md`

- [ ] **T3.3.2** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar quinotospec-help como comando "¿que sigue?".
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

- [ ] **T3.3.3** — Actualizar `agent-dist/skills/quinotospec-suggest-next/SKILL.md` — Integrar con quinotospec-help para navegacion global ademas de intra-propuesta.
  - Archivo: `agent-dist/skills/quinotospec-suggest-next/SKILL.md`

---

### F3.4 — Actualizaciones de Infraestructura (Fase 3)

#### Tareas

- [ ] **T3.4.1** — Actualizar `manifest.json` — Bump a 3.2.0, actualizar conteos (skills: +4 = 40, workflows: +3 = 46, agentes: 9 convertidos).
  - Archivo: `manifest.json`

- [ ] **T3.4.2** — Actualizar `.version` — `3.2.0`.
  - Archivo: `.version`

- [ ] **T3.4.3** — Actualizar `CHANGELOG.md` — Entrada v3.2.0.
  - Archivo: `CHANGELOG.md`

---

## Fase 4 — Producto y Metodologia (v3.3.0)

**Objetivo:** Incorporar metodologias de producto avanzadas, scale-adaptive planning, y template-driven quality.

**Fuentes principales:** BMAD-METHOD (50%), Spec-Kit (40%), OpenSpec (10%)

---

### F4.1 — PRFAQ / Working Backwards

| Campo | Detalle |
|-------|---------|
| **Fuente** | BMAD-METHOD (`bmad-prfaq`) |
| **Problema actual** | QuinotoSpec tiene PRD y RFC pero no la metodologia "Working Backwards" de Amazon |
| **Solucion** | Workflow `/quinotospec.prfaq` que implementa el proceso de escribir el press release antes de construir |

#### Tareas

- [ ] **T4.1.1** — Crear `agent-dist/workflows/quinotospec.prfaq.md` — Workflow Working Backwards:
  - Fase 1 — Ignition: cliente especifico, problema concreto, stakes reales
  - Fase 2 — Press Release: 9 secciones que fuerzan claridad
  - Fase 3 — Customer FAQ: preguntas del cliente
  - Fase 4 — Internal FAQ + Verdict: preguntas del equipo + decision Go/No-Go
  - "Hardcore mode": desafiar palabras vacias ("best-in-class", "seamless")
  - Archivo: `agent-dist/workflows/quinotospec.prfaq.md`

- [ ] **T4.1.2** — Crear `agent-dist/templates/prfaq-template.md` — Template con las 9 secciones del press release.
  - Archivo: `agent-dist/templates/prfaq-template.md`

- [ ] **T4.1.3** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Referenciar PRFAQ.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F4.2 — Scale-Adaptive Planning

| Campo | Detalle |
|-------|---------|
| **Fuente** | BMAD-METHOD (track-based routing: Quick/Simple/Complex/Enterprise) |
| **Problema actual** | QuinotoSpec aplica el mismo rigor a un bug fix que a un sistema enterprise |
| **Solucion** | Routing basado en complejidad que ajusta la profundidad del proceso |

#### Arquitectura

El workflow `quinotospec.apply` (o un nuevo `quinotospec.quick-dev`) evalua la complejidad y deriva a uno de 4 tracks:

| Track | Profundidad | Gatillo |
|-------|-------------|---------|
| **Quick Fix** | Spec minima → implementacion directa | Bug fix, typo, cambio de config |
| **Simple** | Spec → tasks → implementacion | Feature simple, un solo archivo |
| **Complex** | Spec → design → US → tasks → implementacion | Multi-archivo, nueva funcionalidad |
| **Enterprise** | Full SDLC + constitution gates + compliance | Multi-servicio, multi-equipo, regulado |

#### Tareas

- [ ] **T4.2.1** — Crear `agent-dist/skills/quinotospec-complexity-router/SKILL.md` — Skill que:
  - Analiza el scope del cambio (archivos afectados, servicios, equipos)
  - Clasifica en Quick/Simple/Complex/Enterprise
  - Deriva al track correspondiente
  - Permite override manual del usuario
  - Archivo: `agent-dist/skills/quinotospec-complexity-router/SKILL.md`

- [ ] **T4.2.2** — Crear `agent-dist/workflows/quinotospec.quick-dev.md` — Workflow de via rapida para bugs y cambios chicos:
  - Comprimir intent (humano + modelo → un goal coherente)
  - Route al track mas seguro y pequeno
  - Implementacion autonoma con supervision minima
  - Diagnosticar fallos en la capa correcta (spec debil? regenerar spec. Logica? parche local)
  - Archivo: `agent-dist/workflows/quinotospec.quick-dev.md`

- [ ] **T4.2.3** — Actualizar `agent-dist/workflows/quinotospec.apply.md` — Integrar complexity router: antes de implementar, el router decide el track.
  - Archivo: `agent-dist/workflows/quinotospec.apply.md`

- [ ] **T4.2.4** — Actualizar `agent-dist/bootstrap/quinotospec-bootstrap.md` — Explicar los 4 tracks y cuando usar cada uno.
  - Archivo: `agent-dist/bootstrap/quinotospec-bootstrap.md`

---

### F4.3 — Template-Driven Quality

| Campo | Detalle |
|-------|---------|
| **Fuente** | Spec-Kit (7 mecanismos de calidad via templates) |
| **Problema actual** | Las templates de QuinotoSpec no tienen mecanismos activos para prevenir que el LLM divague |
| **Solucion** | Incorporar 7 mecanismos de calidad en todas las templates del sistema |

#### Los 7 Mecanismos

1. **Preventing premature implementation** — Templates explicitamente dicen "Focus on WHAT, avoid HOW"
2. **Forcing explicit uncertainty markers** — `[NEEDS CLARIFICATION]` markers required
3. **Structured thinking through checklists** — Checklists actuan como "unit tests for English"
4. **Constitutional compliance through gates** — Simplicity Gate, Anti-Abstraction Gate, Integration-First Gate
5. **Hierarchical detail management** — Complejidad extraida a archivos separados
6. **Test-first thinking** — Contract tests antes de implementacion
7. **Preventing speculative features** — "No speculative or 'might need' features"

#### Tareas

- [ ] **T4.3.1** — Revisar y actualizar las 5 templates core para incorporar los 7 mecanismos:
  - `proposal-template.md`: Agregar [NEEDS CLARIFICATION], anti-speculative features
  - `user-stories-template.md`: Agregar checklists de calidad, acceptance criteria estrictos
  - `design-template.md`: Agregar constitutional gates, hierarchical detail
  - `tasks-template.md`: Agregar test-first ordering, parallel markers [P]
  - `spec-template.md`: Agregar GIVEN/WHEN/THEN obligatorio, uncertainty markers
  - Archivos: todos bajo `agent-dist/templates/`

- [ ] **T4.3.2** — Crear `agent-dist/workflows/quinotospec.checklist.md` — Workflow que genera checklists de calidad custom para validar specs (como "unit tests for English").
  - Archivo: `agent-dist/workflows/quinotospec.checklist.md`

- [ ] **T4.3.3** — Crear `agent-dist/workflows/quinotospec.analyze.md` — Cross-artifact consistency analysis: verifica que proposal, specs, design y tasks sean consistentes entre si.
  - Archivo: `agent-dist/workflows/quinotospec.analyze.md`

- [ ] **T4.3.4** — Crear `agent-dist/workflows/quinotospec.clarify.md` — Structured clarification workflow: preguntas secuenciales para refinar specs ambiguas antes del plan.
  - Archivo: `agent-dist/workflows/quinotospec.clarify.md`

---

### F4.4 — SPEC Kernel Canonico

| Campo | Detalle |
|-------|---------|
| **Fuente** | BMAD-METHOD (`bmad-spec`) |
| **Problema actual** | Las especificaciones no tienen un formato canonico inmutable |
| **Solucion** | SPEC kernel de 5 campos (Why, Capabilities, Constraints, Non-goals, Success signal) |

#### Tareas

- [ ] **T4.4.1** — Crear `agent-dist/skills/quinotospec-spec-kernel/SKILL.md` — Skill que:
  - Destila cualquier input (PRD, RFC, brain dump, transcript) a 5 campos canonicos
  - "Spec Law": 8 reglas que gobiernan la especificacion
  - Specs son inmutables una vez escritas
  - Companion files para overflow
  - Downstream skills consumen el kernel, no re-leen todos los artifacts upstream
  - Archivo: `agent-dist/skills/quinotospec-spec-kernel/SKILL.md`

- [ ] **T4.4.2** — Actualizar workflows de propuesta para consumir SPEC kernel cuando esta disponible.
  - Archivos: `quinotospec.create-proposal.md`, `quinotospec.create-user-stories.md`

---

### F4.5 — Workflow Engine YAML

| Campo | Detalle |
|-------|---------|
| **Fuente** | Spec-Kit (`src/specify_cli/workflows/`) |
| **Problema actual** | Los workflows de QuinotoSpec son Markdown secuencial. No hay branching, gates, fan-out, ni reanudacion |
| **Solucion** | Engine que ejecuta workflows definidos en YAML con control flow y persistencia de estado |

#### Arquitectura

```yaml
# .quinoto-spec/workflows/full-sdd.yml
name: full-sdd
description: Full Spec-Driven Development cycle
steps:
  - id: constitution
    type: command
    command: quinotospec.constitution
  - id: discovery
    type: command
    command: quinotospec.discovery
  - id: gate-review-discovery
    type: gate
    message: "Review discovery output before proceeding"
  - id: proposal
    type: command
    command: quinotospec.create-proposal
    depends_on: [gate-review-discovery]
  - id: user-stories
    type: command
    command: quinotospec.create-user-stories
    depends_on: [proposal]
  - id: tasks
    type: command
    command: quinotospec.create-tasks
    depends_on: [user-stories]
  - id: fan-out-implement
    type: fan-out
    over: tasks.items
    command: quinotospec.apply --task {{item.id}}
    max_concurrency: 3
  - id: review
    type: command
    command: quinotospec.review
    depends_on: [fan-out-implement]
  - id: archive
    type: command
    command: quinotospec.archive
    depends_on: [review]
```

#### Tareas

- [ ] **T4.5.1** — Crear `agent-dist/skills/quinotospec-workflow-engine/SKILL.md` — Skill que interpreta y ejecuta workflows YAML con:
  - Step types: command, gate, if/switch, while, fan-out, fan-in, shell, prompt
  - State persistence: `.quinoto-spec/workflows/runs/<run_id>/state.json`
  - Resumability: continuar desde gates y fallos
  - Expression engine: `{{ steps.id.output }}`, `{{ inputs.name }}`
  - Archivo: `agent-dist/skills/quinotospec-workflow-engine/SKILL.md`

- [ ] **T4.5.2** — Crear `agent-dist/templates/workflow-template.yml` — Template para definir workflows.
  - Archivo: `agent-dist/templates/workflow-template.yml`

- [ ] **T4.5.3** — Crear `agent-dist/workflows/quinotospec.workflow-run.md` — Workflow para ejecutar workflows YAML.
  - Archivo: `agent-dist/workflows/quinotospec.workflow-run.md`

- [ ] **T4.5.4** — Crear workflow YAML predefinido `workflows/full-sdd.yml` — El ciclo SDD completo como workflow YAML.
  - Archivo: `workflows/full-sdd.yml`

---

### F4.6 — Actualizaciones de Infraestructura (Fase 4)

#### Tareas

- [ ] **T4.6.1** — Actualizar `manifest.json` — Bump a 3.3.0, actualizar conteos (skills: +3 = 43, workflows: +7 = 53, templates: +3).
  - Archivo: `manifest.json`

- [ ] **T4.6.2** — Actualizar `.version` — `3.3.0`.
  - Archivo: `.version`

- [ ] **T4.6.3** — Actualizar `CHANGELOG.md` — Entrada v3.3.0.
  - Archivo: `CHANGELOG.md`

- [ ] **T4.6.4** — Actualizar `README.md` y `README_EN.md` — Roadmap visual, nuevos features de v3.
  - Archivos: `README.md`, `README_EN.md`

- [ ] **T4.6.5** — Actualizar `docs/ARCHITECTURE.md` — Reflejar nueva arquitectura con todas las fases.
  - Archivo: `docs/ARCHITECTURE.md`

- [ ] **T4.6.6** — Crear `docs/EXTENSIONS-GUIDE.md` — Guia completa del sistema de extensiones.
  - Archivo: `docs/EXTENSIONS-GUIDE.md`

- [ ] **T4.6.7** — Crear `docs/AGENTS-GUIDE.md` — Guia completa del sistema de agentes con personalidad.
  - Archivo: `docs/AGENTS-GUIDE.md`

---

## Dependencias entre Fases

```
Fase 1 (v3.0.0) ─────────────────────────────────────────────────────
  │
  │  Sin dependencias externas. Se puede construir sobre v2.1.0
  │
  ├──► Fase 2 (v3.1.0) ──────────────────────────────────────────────
  │      │
  │      │  Requiere: F1.1 (bootstrap), F1.5 (constitution)
  │      │  Delta specs usa constitution como base
  │      │  Artifact engine usa constitution + delta specs
  │      │
  │      ├──► Fase 3 (v3.2.0) ───────────────────────────────────────
  │             │
  │             │  Requiere: F2.2 (artifact engine), F2.4 (config.yaml)
  │             │  Agentes leen config desde artifact engine
  │             │  Party mode usa agentes convertidos
  │             │
  │             └──► Fase 4 (v3.3.0) ────────────────────────────────
  │                    │
  │                    │  Requiere: F2.1 (delta specs), F2.2 (engine),
  │                    │            F3.1 (agentes), F3.3 (help)
  │                    │  Scale-adaptive usa complexity router
  │                    │  Workflow engine orquesta todos los workflows
  │                    │  SPEC kernel alimenta delta specs
  │                    │
```

---

## Estructura de Archivos Resultante

```
quinotospec-package/
├── .version                                    # 3.3.0
├── manifest.json                               # Metadata v3.3.0
├── install.sh                                  # Instalador actualizado
├── AGENTS.md                                   # Generado dinamicamente
├── V3_ROADMAP.md                               # Este archivo
│
├── .cursor-plugin/
│   └── plugin.json                             # Cursor plugin manifest (F1.1)
│
├── extensions/
│   ├── catalog.json                            # Extension catalog curado (F2.3)
│   ├── catalog.community.json                  # Community catalog (F2.3)
│   └── EXTENSION-DEVELOPMENT-GUIDE.md          # Extension dev guide (F2.3)
│
├── workflows/
│   └── full-sdd.yml                            # Workflow YAML predefinido (F4.5)
│
├── agent-dist/
│   ├── bootstrap/
│   │   └── quinotospec-bootstrap.md            # Bootstrap meta-skill (F1.1)
│   │
│   ├── hooks/
│   │   ├── session-start.sh                    # Session-start hook script (F1.1)
│   │   ├── run-hook.cmd                        # Polyglot launcher (F1.1)
│   │   ├── hooks.json                          # Claude Code hook config (F1.1)
│   │   ├── hooks-cursor.json                   # Cursor hook config (F1.1)
│   │   └── hooks-opencode.json                 # OpenCode hook config (F1.1)
│   │
│   ├── plugins/
│   │   └── opencode/
│   │       └── quinotospec-plugin.js           # OpenCode plugin (F1.1)
│   │
│   ├── workflows/                              # 53 workflows (35 originales + 18 nuevos)
│   │   ├── quinotospec.constitution.md         # F1.5
│   │   ├── quinotospec.specs-init.md           # F2.1
│   │   ├── quinotospec.schema-fork.md          # F2.2
│   │   ├── quinotospec.extension-install.md    # F2.3
│   │   ├── quinotospec.preset-install.md       # F2.3
│   │   ├── quinotospec.update-agents.md        # F2.4
│   │   ├── quinotospec.agent-configure.md      # F3.1
│   │   ├── quinotospec.party-mode.md           # F3.2
│   │   ├── quinotospec.prfaq.md                # F4.1
│   │   ├── quinotospec.quick-dev.md            # F4.2
│   │   ├── quinotospec.checklist.md            # F4.3
│   │   ├── quinotospec.analyze.md              # F4.3
│   │   ├── quinotospec.clarify.md              # F4.3
│   │   └── quinotospec.workflow-run.md         # F4.5
│   │   + (existing workflows updated)
│   │
│   ├── skills/                                 # 43 skills (27 originales + 16 nuevos)
│   │   ├── quinotospec-tdd/                    # F1.2
│   │   │   ├── SKILL.md
│   │   │   ├── testing-anti-patterns.md
│   │   │   └── examples/
│   │   ├── quinotospec-debug/                  # F1.3
│   │   │   ├── SKILL.md
│   │   │   ├── root-cause-tracing.md
│   │   │   ├── defense-in-depth.md
│   │   │   └── condition-based-waiting.md
│   │   ├── quinotospec-verify-before-done/     # F1.4
│   │   │   └── SKILL.md
│   │   ├── quinotospec-receive-review/         # F1.6
│   │   │   └── SKILL.md
│   │   ├── quinotospec-worktree/               # F1.7
│   │   │   └── SKILL.md
│   │   ├── quinotospec-artifact-engine/        # F2.2
│   │   │   └── SKILL.md
│   │   ├── quinotospec-extension-manager/      # F2.3
│   │   │   └── SKILL.md
│   │   ├── quinotospec-template-resolver/      # F2.3
│   │   │   └── SKILL.md
│   │   ├── quinotospec-agent-config/           # F3.1
│   │   │   └── SKILL.md
│   │   ├── quinotospec-agent-customize/        # F3.1
│   │   │   └── SKILL.md
│   │   ├── quinotospec-party-orchestrator/     # F3.2
│   │   │   ├── SKILL.md
│   │   │   └── strategies/
│   │   ├── quinotospec-help/                   # F3.3
│   │   │   └── SKILL.md
│   │   ├── quinotospec-complexity-router/      # F4.2
│   │   │   └── SKILL.md
│   │   ├── quinotospec-spec-kernel/            # F4.4
│   │   │   └── SKILL.md
│   │   ├── quinotospec-workflow-engine/        # F4.5
│   │   │   └── SKILL.md
│   │   └── (existing skills updated)
│   │
│   ├── agents/                                 # 9 agentes (convertidos + nuevos)
│   │   └── converted/
│   │       ├── alba.md                         # Arquitecta (F3.1)
│   │       ├── daniel.md                       # Debugger (F3.1)
│   │       ├── eva.md                          # DevOps (F3.1)
│   │       ├── lucas.md                        # Code Reviewer (F3.1)
│   │       ├── mateo.md                        # Doc Writer (F3.1)
│   │       ├── nora.md                         # Performance (F3.1)
│   │       ├── raul.md                         # Refactor (F3.1)
│   │       ├── sofia.md                        # Security (F3.1)
│   │       └── victor.md                       # Test Writer (F3.1)
│   │
│   ├── rules/
│   │   └── quinotospec-rules.md               # 16 reglas (F1.8)
│   │
│   └── templates/                              # Templates expandidas
│       ├── constitution-template.md            # F1.5
│       ├── delta-spec-template.md              # F2.1
│       ├── schema-template.yaml                # F2.2
│       ├── extension-template.yml              # F2.3
│       ├── preset-template.yml                 # F2.3
│       ├── AGENTS-template.md                  # F2.4
│       ├── agent-defaults.toml                 # F3.1
│       ├── prfaq-template.md                   # F4.1
│       ├── workflow-template.yml               # F4.5
│       └── (existing templates updated)        # F4.3
│
├── docs/
│   ├── ARCHITECTURE.md                         # Actualizado (F1.8, F4.6)
│   ├── EXTENSIONS-GUIDE.md                     # F4.6
│   └── AGENTS-GUIDE.md                         # F4.6
│
├── tests/
│   └── (test suites actualizados)
│
└── scripts/
    └── validate-all.sh                         # Actualizado (F1.8, F2.5)
```

---

## Criterios de Aceptacion por Fase

### Fase 1 (v3.0.0) — Done when:

- [x] Bootstrap se inyecta automaticamente al iniciar sesion en OpenCode, Cursor y Claude Code
- [x] Skill TDD bloquea implementacion si no hay test que falle primero
- [x] Skill Debugging fuerza root cause investigation antes de fixes
- [x] Skill Verify-Before-Done bloquea claims sin evidencia fresca
- [x] `/quinotospec.constitution` genera `.quinoto-spec/constitution.md`
- [x] Skill Receive-Review elimina "performative agreement" de las respuestas del agente
- [x] Skill Worktree aisla el workspace durante implementacion
- [x] Los tests suite pasan con los nuevos componentes
- [x] `scripts/validate-all.sh --strict` pasa

### Fase 2 (v3.1.0) — Done when:

- [x] Propuestas generan delta specs en lugar de specs completas
- [x] `/quinotospec.archive` aplica merge de delta specs correctamente
- [x] Artifact engine calcula estado DAG y bloquea artefactos sin dependencias
- [x] Sistema de extensiones: install, remove, update, list funcionales
- [x] 4-layer template resolution stack funciona
- [x] `/quinotospec.update-agents` regenera AGENTS.md dinamicamente
- [x] Una extension de prueba se instala y sus hooks se ejecutan

### Fase 3 (v3.2.0) — Done when:

- [x] Los 9 agentes tienen personalidades definidas y nombres
- [x] 3-layer TOML merge funciona (defaults → team → personal)
- [x] Party Mode ejecuta mesa redonda con al menos 3 agentes
- [x] Modo `--subagents` spawn subagentes independientes
- [x] `quinotospec-help` recomienda correctamente el proximo workflow
- [x] `quinotospec-suggest-next` funciona tanto intra-propuesta como global

### Fase 4 (v3.3.0) — Done when:

- [x] `/quinotospec.prfaq` completa el ciclo Working Backwards
- [x] Complexity router deriva a Quick/Simple/Complex/Enterprise correctamente
- [x] `/quinotospec.quick-dev` resuelve bugs en <5 turnos
- [x] Todas las templates core implementan los 7 mecanismos de calidad
- [x] SPEC kernel se genera desde PRD, RFC o brain dump
- [x] Workflow engine YAML ejecuta `full-sdd.yml` completo con gates y fan-out
- [x] El workflow es resumible desde fallos y gates

---

## Resumen de Metricas

| Metrica | v2.1.0 | v3.0.0 | v3.1.0 | v3.2.0 | v3.3.0 |
|---------|--------|--------|--------|--------|--------|
| Workflows | 33 | 35 | 43 | 46 | 53 |
| Skills | 27 | 33 | 36 | 40 | 43 |
| Reglas | 12 | 16 | 16 | 16 | 16 |
| Agentes | 9 | 9 | 9 | 9 | 9 |
| Templates | 1 | 2 | 7 | 8 | 11 |
| IDEs soportados | 4 | 4 (+hooks) | 4 (+hooks) | 4 (+hooks) | 4 (+hooks) |
| Bootstrap | Manual | Automatico | Automatico | Automatico | Automatico |
| Extensibilidad | No | No | Extensiones + Presets | Extensiones + Presets | Extensiones + Presets |
| TDD Enforcement | No | Si | Si | Si | Si |
| Debugging Sistematico | No | Si | Si | Si | Si |
| Party Mode | No | No | No | Si | Si |
| Scale Adaptive | No | No | No | No | Si |

---

## Conflictos con Dependencias Conocidos

Las features F2.1, F2.2 y F3.2 se implementaron como versiones incrementales (v2.2.0 → v2.4.0) antes de completar Fase 1. Esto genera los siguientes conflictos:

| Conflicto | Impacto | Mitigacion |
|-----------|---------|------------|
| **Sin F1.1 (Bootstrap)**: T3.2.5 bloqueada porque `agent-dist/bootstrap/` no existe | Bajo. Party Mode se descubre via AGENTS.md y comandos del IDE | Implementar F1.1 desbloquea T3.2.5 |
| **Sin F1.5 (Constitution)**: Schema YAML referencia `constitution` como artefacto opcional | Nulo. El engine lo marca como optional y no bloquea nada | Constitution ya es opcional en el schema |
| **Sin F3.1 (Agentes con personalidad)**: Party Mode usa agentes existentes sin nombres humanos ni TOML | Bajo. Los agentes actuales ya tienen `## Personality` | F3.1 enriqueceria Party Mode pero no es bloqueante |
| **Versionado inconsistente**: Roadmap asigna v3.0.0 a Fase 1 pero implementamos como v2.2.0→2.4.0 | Bajo. Semantic versioning correcto | Re-asignar versiones cuando se complete Fase 1 |

### Recomendacion para proxima sesion

1. **F1.1** (Bootstrap) — Desbloquea T3.2.5, beneficia a todo el sistema
2. **F1.2 + F1.3** (TDD + Debugging) — Maximo impacto en calidad de codigo generado por agentes
3. **F3.1** (Agentes con personalidad) — Enriquece Party Mode con nombres humanos y TOML

---

## Actualizacion de Infraestructura (v2.4.0 consolidacion)

- [x] `manifest.json`: version 2.4.0, workflows 36, skills 29, features party_mode
- [x] `.version`: 2.4.0
- [x] `install.sh`: INSTALLER_VERSION 2.4.0
- [x] `CHANGELOG.md`: Entradas 2.2.0, 2.3.0, 2.4.0 con resumen consolidado
- [x] `README.md`: Badges actualizados (36 workflows, 29 skills)
- [x] `README_EN.md`: Party Mode en secciones
- [x] `AGENTS.md`: Workflows specs-init, schema-fork, party-mode; Skills artifact-engine, party-orchestrator
- [x] `docs/ARCHITECTURE.md`: 36 workflows, 29 skills, Party Mode, Artifact Engine
- [x] `scripts/validate-all.sh`: Conteos actualizados (36 workflows, 29 skills)

---

*Plan generado: Junio 2026. Actualizado: Junio 2026. Versionado junto con el proyecto.*
