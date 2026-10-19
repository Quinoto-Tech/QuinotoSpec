# Resumen Ejecutivo del Proyecto: QuinotoSpec

**Discovery Date:** 2026-09-27

Guardar en: .quinoto-spec/discovery/02-overview.md

## Resumen

**QuinotoSpec** (v3.2.0, *Hird Edition*, estado `beta-rc`) es un **paquete de configuración de
agentes de IA**. No es una aplicación: no tiene servidor, ni base de datos, ni proceso en runtime.

Su función es distribuir una **metodología de desarrollo** llamada *Proposal First* (y el sistema de
artefactos que la sostiene) hacia los directorios de configuración de los IDEs que usan agentes:

| IDE | Directorio global | Directorio de proyecto |
|---|---|---|
| **OpenCode** | `~/.config/opencode/` | `<proyecto>/.opencode/` |
| Cursor | `~/.cursor/` | `<proyecto>/.cursor/` |
| Claude Code | `~/.claude/` | `<proyecto>/.claude/` |
| Cline | `~/.config/cline/` | `<proyecto>/.cline/` |
| Antigravity | `~/.gemini/config/` | `<proyecto>/.agents/` |
| Genérico | `~/.config/agent/` | `<proyecto>/.agent/` |

Lo que instala son **instrucciones, skills, comandos, agentes, reglas y plantillas** que el IDE carga
de forma nativa, más un `AGENTS.md` generado a medida del proyecto.

## Qué problema resuelve

Los agentes de IA arrancan sin contexto. Sin Bootstrap de sesión, el agente ignora el proyecto y
opina sin criterio. La respuesta ingenua ("que el agente lea `AGENTS.md` por su cuenta") es frágil:
`V3_ROADMAP.md:70` lo dice textualmente — *"QuinotoSpec depende de que el agente lea `AGENTS.md` por su
propia cuenta. Si el agente lo ignora, no hay QuinotoSpec."*

QuinotoSpec ataca eso con tres mecanismos:

1. **Bootstrap de sesión** — se inyecta automáticamente el contexto al iniciar cada sesión
   (mecanismo distinto por IDE: plugin JS en OpenCode, hook `sessionStart` en Cursor, hook
   `SessionStart` en Claude Code).
2. **Artefactos estructurados** — propuestas, user stories y tareas con IDs canónicos
   (`US-MNEM-suffix-NNN`), estados validados y DAG de dependencias.
3. **Gobernanza ejecutable** — reglas que se aplican de verdad (no solo prosa): TDD antes de
   producción, evidencia fresca antes de dar por terminado, aprobación humana registrada.

## Estructura del repositorio

```
quinotospec-package/
├── install.sh              # instalador transaccional multi-IDE (1278 líneas) ← entry point
├── manifest.json           # inventario + feature flags de máquina
├── .version                # "3.2.0" (fuente de verdad simple)
├── AGENTS.md               # guía para agentes (hand-maintained, referencia offline)
├── README.md / README_EN.md# docs principales bilingües (es/en), ~40 KB cada uno
├── V3_ROADMAP.md           # 1585 líneas, plan por fases (Gate 0, F1.1, F2.4, F3.2, F4.x)
├── CHANGELOG.md            # changelog v1 (legado, single-file)
│
├── agent-dist/             # ← EL PAYLOAD: lo que se instala en el IDE
│   ├── skills/             #   86 skills (SKILL.md + 12 con scripts propios)
│   ├── workflows/          #   43 workflows → se renombran a commands/ al instalar
│   ├── agents/             #   9 agentes especializados
│   ├── rules/              #   1 archivo, 18 reglas
│   ├── templates/          #   13 plantillas
│   ├── bootstrap/          #   1 payload de contexto de sesión
│   ├── hooks/              #   session-start.sh + 3 manifiestos de hook por IDE
│   └── plugins/            #   1 plugin JS (solo OpenCode)
│
├── scripts/                # 7 scripts: validate-all, package-release, smoke-release, ...
├── tests/                  # 20 suites bash + 7 unittest python + 5 fixtures
├── docs/                   # 8 documentos técnicos + 8 imágenes + 2 posts
├── .quinoto-spec/          # dogfooding: changelog v2, prefix-registry, proposals/
├── .github/workflows/      # 3 workflows
├── .githooks/              # pre-commit (frontmatter), pre-push (suite completa)
└── examples/               # proyectos de ejemplo (FastAPI, Rust, Node)
```

## Comandos básicos

```bash
# Instalación (interactiva por defecto; el path es el target)
./install.sh --opencode --global        # OpenCode → ~/.config/opencode/
./install.sh --cursor --global          # Cursor    → ~/.cursor/
./install.sh --claude --global          # Claude    → ~/.claude/
./install.sh --opencode --yes           # no interactivo, target = cwd

# Verificación / desinstalación
./install.sh --verify --opencode --yes
./install.sh --uninstall --opencode --yes

# Desarrollo
bash tests/run-all-tests.sh             # suite completa
bash scripts/validate-all.sh --strict   # gate de release

# Release
bash scripts/package-release.sh 3.2.0 /tmp/quinotospec-dist
bash scripts/smoke-release.sh /tmp/quinotospec-dist/quinotospec-3.2.0.tar.gz
```

## Prerrequisitos de entorno

| Requisito | Mínimo | Verificado por |
|---|---|---|
| `bash` | 4.0 | `install.sh:513-520` |
| `git` | 2.0 | `install.sh:523-531` |
| `python3` | 3.8 | `install.sh:533-545` |
| `node` | cualquiera | Opcional. Solo `node --check` del plugin |
| `shellcheck` | — | Solo en CI (`ci.yml:57-72`); el runner ya lo trae |

**No hay variables de entorno requeridas.** No hay `.env`, ni claves, ni tokens. El paquete no hace
llamadas de red.

## Superficie del paquete

| Métrica | Valor |
|---|---|
| Líneas en `agent-dist` + `scripts` + `tests` | ~28 900 |
| Skills | 86 (los 86 tienen `SKILL.md`; solo 12 traen scripts/referencias) |
| Workflows (slash commands) | 43 |
| Agentes | 9 |
| Reglas | 18 |
| Templates | 13 |
| Scripts Python | 15 (agent-dist) + 7 (tests) |
| Dependencias de terceros | **0 obligatorias** |
| Comandos de CLI públicos | 1 instalador + 15 CLIs de script |

## Riesgos y puntos críticos

| # | Riesgo | Severidad | Detalle |
|---|---|---|---|
| 1 | **Plugin de OpenCode incompatible con OpenCode v2** | 🔴 Alta | El runtime v2.0.16 exige `default` = objeto `{id, effect|setup}`; el plugin exporta el contrato v1. Falla en **cada arranque** del servidor. Ver `07-findings-and-recommendations.md` |
| 2 | **`AGENTS.md` global se escribe en la ruta que OpenCode no lee** | 🔴 Alta | Con `--opencode --global`, el archivo queda en `~/.config/AGENTS.md`; OpenCode v2 solo carga `~/.config/opencode/AGENTS.md`. Verificado empíricamente |
| 3 | Superficie de tests acoplada al plugin | 🟠 Media | 5 asserts en 3 suites + 2 checks de `validate-all.sh` + 2 jobs de CI fallan si el plugin desaparece |
| 4 | Tests sin auto-descubrimiento | 🟠 Media | Suite hardcodeada; un test nuevo no se ejecuta sin editar el registro |
| 5 | `__pycache__/*.pyc` versionados | 🟡 Baja | 13 `.pyc` (cpython-314) presentes en el árbol de skills |
| 6 | Fixtures muertos | 🟡 Baja | `tests/fixtures/{node-project,python-project,empty-project}` no los usa ningún test |
| 7 | `external_config` nunca se lee | 🟡 Baja | Se escribe en el manifest (`:337-351`) y nadie lo consume; uninstall usa `hook_commands` |
| 8 | `--strict` requiere Node | 🟡 Baja | Sin Node, el warning de `validate-all.sh:158` vuelve fatal el gate por `:191` |

## Conclusión

El paquete está **maduro en gobernanza y testing** (ownership por hash, transacciones con rollback,
20 suites, CI en 2 SO × 2 versiones de Python) y ** frágil en su integración con el host**. El
contrato del plugin de OpenCode quedó desactualizado respecto al runtime, y el mecanismo de
instrucciones global apunta a una ruta que el IDE no lee. Ambos son fallos del *adaptador al host*,
no de la metodología — que es la parte que funciona bien.

## 🔗 Referencias

- `01-stack-profile.md` — detalle del stack y comandos de test
- `03-architecture.md` — capas y flujo de instalación
- `07-findings-and-recommendations.md` — deuda técnica priorizada
