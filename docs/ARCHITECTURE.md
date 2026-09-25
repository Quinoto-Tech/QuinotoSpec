# Arquitectura Interna de QuinotoSpec

## Vision General

QuinotoSpec es un sistema de configuracion de agentes basado en tres pilares:

1. **Workflows**: Secuencias de instrucciones que el agente ejecuta
2. **Skills**: Capacidades especializadas reutilizables
3. **Rules**: Restricciones inmutables que gobiernan el comportamiento

**Estado de release:** beta / release candidate (v3.2.0 Hird Edition; Gate 0 + F3.2 bootstrap complete).

**Criterio de madurez:** la presencia de un artefacto en `agent-dist/` no implica que la capacidad sea production-ready. Cada componente debe declarar su estado y sus límites operativos.

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
|  | workflows/  | |  <-- 43 workflows
 |  | skills/     | |  <-- 86 skills (40 core + 46 utilitarias)

 |  | rules/      | |  <-- 18 reglas
 |  | agents/     | |  <-- 9 agentes
  |  | templates/  | |  <-- 13 templates
  |  | bootstrap/  | |  <-- contexto de inicio
  |  | hooks/      | |  <-- hooks por IDE
  |  | plugins/    | |  <-- adaptador OpenCode

 |  +-------------+ |
+--------+---------+
          |
          v
+--------+---------+
|  IDE Target      |  <-- .opencode/, .cursor/, .claude/, .cline/, .agents/, .agent/
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

## Matriz de madurez — Gate 0 + F1.7 (2026-09-24)

Los estados significan lo siguiente:

- **Beta**: utilizable con limitaciones operativas; no debe ser usado como gate de producción sin validación.
- **Experimental**: la capacidad existe parcialmente, pero requiere implementación, pruebas o guardas de seguridad.
- **Prompt-only**: la capacidad depende de instrucciones para el agente y no tiene una implementación determinista equivalente.
- **Demo**: la implementación actual sirve para demostrar el flujo, no para medir o bloquear producción.

| Capacidad | Estado | Tipo | Límite que bloquea estabilidad |
|-----------|--------|------|--------------------------------|
| Proposal First / Context Slicing | Beta | Workflows | Requiere gates ejecutables para el resto de reglas |
| Bootstrap de sesión y hooks | Beta | Bootstrap + shell + plugin | El comportamiento final depende de la versión del IDE y del reinicio |
| Delta specs y `specs/` | Beta | Workflow + templates | El merge y sus validadores aún no son transaccionales |
| Artifact DAG / schema | Beta | YAML + helpers | La cobertura de formatos y dependencias es parcial |
| Changelog v2 | Beta | Archivos append-only | La compatibilidad v1 no está unificada en todos los consumidores |
| Rules y validación | Beta | Dispatcher read-only + evidence validator + instrucciones | Evidencia técnica se valida; decisiones humanas y ejecución real siguen diferidas |
| Backup engine | Beta | Python stdlib + SHA-256 | El restore es transaccional; disaster recovery y cleanup siguen requiriendo operación explícita |
| TDD / debugging / verify | Beta | Skills + evidence validator + reglas | La evidencia es estructurada; la ejecución real y decisiones humanas siguen diferidas |
| Decisiones humanas | Beta | JSON approval validator + dispatcher | La identidad y la ejecución siguen externas; el gate exige registro explícito, fresco y acotado |
| Constitution | Prompt-only | Template + workflow | La activación y el compliance requieren revisión humana |
| Receive Review | Prompt-only | Skill + workflow | La verificación del feedback depende del agente que ejecuta la skill |
| Worktree isolation | Prompt-only | Skill + Apply gate | La disponibilidad de herramientas nativas y las verificaciones Git dependen del agente |
| Mimir | Beta | Helper offline | Requiere pruebas de instalación, concurrencia y runtime path |
| Valkyrie | Beta | Helper offline | La semántica de dependencias y estado aún es incompleta |
| Jormungandr | Beta | Helper offline | El fallback puede declarar un DAG válido sin analizarlo correctamente |
| Party Mode | Experimental | Workflow + orquestador + bootstrap | El comportamiento depende del agente y de sus herramientas |
| Tiwaz Rune | Prompt-only | Metodología + fórmulas | No existe un motor ejecutable completo de medición |
| Huginn & Muninn | Demo | Gate CI | Emite un score de demostración y no calcula entropía real |
| Norns / Skald | Experimental | Scripts | Sincronización atómica y generación de documentación incompletas |
| Bifrost | Experimental | Git externo | Requiere dry-run, confirmación y allowlist de remotos |
| Battle Frenzy / Blood-Bond | Experimental | Orquestación + datos locales | Requiere aislamiento de worktrees y política de privacidad |
| Installer / backup | Beta | Bash transaccional + Python backup engine | Staging, ownership manifest y rollback implementados; disaster recovery multi-repo queda pendiente |

## Capa de contrato

`agent-dist/skills/quinotospec-contract/contract.py` es el adaptador read-only entre Markdown y el modelo normalizado. Todos los consumidores deben consultar este contrato para IDs, estados, relaciones proposal→story→task y changelog v1/v2. Los artefactos legacy se aceptan sin reescritura automática.

El comando de gate es:

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
```

## Gate de aprobación humana

Las decisiones humanas usan un validador separado y read-only:

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py \
  --root . --profile target --action apply --check human-approval \
  --require-approval --approval-id {{APPROVAL_ID}} \
  --approval-subject {{SUBJECT}} --approval-action apply --json
```

El registro vive en `.quinoto-spec/approvals/{{APPROVAL_ID}}.json`; solo `approved` habilita el gate y el validador no prueba identidad.

## Transacción del installer

`install.sh` copia la configuración existente a un staging sibling, instala y verifica allí, escribe `.quinoto-spec/ownership.json` con SHA-256 de cada archivo gestionado y solo entonces reemplaza el destino mediante `mv`. Un `EXIT trap` restaura el destino y `AGENTS.md` si falla cualquier etapa. El uninstall elimina únicamente archivos cuyo hash coincide con el manifest y conserva configuración ajena; instalaciones legacy sin manifest se rechazan para evitar borrado destructivo.

## Extension and preset system

Las extensiones se almacenan en `.quinoto-spec/extensions/`, los presets en `.quinoto-spec/presets/` y el registro en `.quinoto-spec/extensions/.registry`. `extension_manager.py` valida manifests, hace staging y ejecuta hooks solo con `--run --yes`. `template_resolver.py` resuelve en orden overrides → presets → extensions → core. `update_agents.py` genera el `AGENTS.md` del proyecto desde `config.yaml` y el inventario activo.

## Release package gate

`scripts/package-release.sh` construye el artefacto sin caches y genera el archivo `.tar.gz.sha256`; `scripts/smoke-release.sh` extrae el tarball en un target separado y ejecuta install, verify, ownership validation y uninstall. CI prueba Python 3.8/3.11 y release publica el tarball junto a su checksum.

## Línea base de Gate 0 + F2.5 + F3.2

- Inventario actual: 43 workflows, 86 skills, 9 agentes, 18 reglas, 13 templates, bootstrap, hooks y plugin OpenCode.
- Release status: `beta-rc`.
- Alcance: congelado salvo F1.1–F1.7, F2.3–F2.5 y F3.2; F3.1 y F3.3 siguen pendientes.
- Criterio de salida: contrato de artefactos, gates ejecutables, operaciones seguras, CI/release verificables y documentación sincronizada.

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

## Runtime de sesión F1.1

`agent-dist/bootstrap/quinotospec-bootstrap.md` es la instrucción de contexto común. `agent-dist/hooks/session-start.sh` la entrega como JSON para Claude Code y Cursor; `agent-dist/plugins/opencode/quinotospec-plugin.js` la inyecta en el primer mensaje de OpenCode. `install.sh` copia los artefactos al target del IDE y conserva las configuraciones JSON existentes cuando agrega una entrada de hook.

El target de Claude Code es `.claude/` o `~/.claude/`; el de Cursor es `.cursor/` o `~/.cursor/`. Las versiones de IDE que no soportan hooks reciben los archivos como referencia y siguen usando `AGENTS.md`.

## Componentes

### Workflows (43)

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

### Skills (86)

Organizadas por dominio:

**Core (wrappers de workflows, 40):** agent-train, apply, archive, backup, battle-frenzy, blood-bond, changelog-view, cleanup, constitution, create-prd, create-proposal, create-rfc, create-tasks, create-user-stories, dependency-graph, discovery, distribute, export, fix, health, heimdallr, import, init, migrate, mjolnir-refactor, onboard, party-mode, pre-commit, refresh-discovery, release, retrospective, review, schema-fork, specs-init, sprint-create, sprint-plan, sprints-init, stack-discovery, status, tiwaz-rune

**Basicas/utilitarias:** stack-detect, file-creation, generate-github-branch, mark-done, update-changelog, validate, entropy-calculator, contract

**Disciplina de ingenieria:** tdd, debug, verify-before-done, constitution, receive-review, worktree

**Gobernanza:** rules-enforce, syntax-validate, rollback, metrics

**Extensibilidad:** extension-manager, template-resolver

**Busqueda y Analisis:** search, stats, diff, sync, estimate, conflict-detector, suggest-next

**Specs y Artefactos:** artifact-engine

**Blood-Bond:** blood-bond-analyzer, blood-bond-monitor, blood-bond-predictor

**Swarm:** swarm-executor, swarm-task-splitter

**Party Mode:** party-orchestrator

**Onboarding:** onboard-developer, onboard-product, onboard-support, onboard-general, onboard-simple, onboard (consolidado)

**Nordicas (v3.2.0):** norns, huginn-muninn, skald, jormungandr, valkyrie, bifrost, mimir

### Reglas (18)

Las reglas tienen niveles de severidad:

**BLOCKING (detienen ejecucion):**
- #3 Product Agreement Check
- #9 Validacion Pre-Workflow Critico
- #10 Backup Pre-Refactor
- #12 Proteccion de Archivos Archivados
- #16 Verificacion Antes de Completar
- #17 Constitutional Compliance
- #18 Aprobación Humana Estructurada

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
- #14 TDD Enforcement
- #15 Debugging Sistematico

**GLOBAL (post-workflow):**
- #13 Blood-Bond Monitor — tras apply/fix/tiwaz-rune/heimdallr, check inactividad ≥14 días

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
