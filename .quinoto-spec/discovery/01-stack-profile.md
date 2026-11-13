# 🛠️ Stack Profile: QuinotoSpec

Perfil tecnológico del paquete: lenguajes, frameworks, gestores, runners de test y estándares de código detectados.

Guardar en: `.quinoto-spec/discovery/01-stack-profile.md`

**Discovery Date:** 2026-11-13
**Versión analizada:** 3.4.0 — *Warband: Hird Edition* (`beta-rc`)
**Skill ejecutada:** `quinotospec-stack-detect`

## Resumen

QuinotoSpec **no es una aplicación en ejecución**: es un paquete de configuración y distribución de una metodología de desarrollo para agentes de IA. No hay servidor de negocio, base de datos ni proceso residente. El "runtime" real es el IDE del usuario (OpenCode, Cursor, Claude Code, Cline o Antigravity) que carga los archivos instalados, más los scripts de soporte en Bash y Python.

El repositorio combina cuatro superficies técnicas:

1. **Instalador transaccional** en Bash (`install.sh`).
2. **Payload declarativo** en Markdown/YAML/JSON (`agent-dist/`).
3. **Herramientas de gobernanza y análisis** en Python stdlib (`agent-dist/skills/*/*.py`).
4. **Dashboard local read-only** en Python stdlib + JavaScript (`agent-dist/ui/` y plugins de IDE).

## 🏗️ Core Technologies

| Rol | Tecnología | Versión mínima / observada | Evidencia |
|---|---|---|---|
| Lenguaje principal de automatización | **Bash** | `>= 4.0` | `install.sh` (1.723 líneas), `scripts/*.sh`, `tests/*.sh`, `.githooks/*` |
| Lenguaje de herramientas | **Python** | `>= 3.8`; probado en 3.8, 3.11, 3.13 y 3.15 | 32 scripts en `agent-dist/`, 7 suites `unittest` en `tests/` |
| Lenguaje de integración con IDE | **JavaScript (CJS + ESM)** | Node.js disponible; ESM para OpenCode v2 | `agent-dist/plugins/opencode/quinotospec-plugin.js`, `agent-dist/plugins/opencode-v2/index.js` |
| UI local | **Python `http.server` + HTML/CSS/JS** | stdlib; sin build frontend | `agent-dist/ui/server.py`, `readers.py`, `templates.py` |
| Formato de configuración/documentación | **Markdown + YAML + JSON + TOML** | — | 49 workflows, 95 skills, 9 agentes, 18 reglas, 13 templates |
| Framework de aplicación | **Ninguno** | — | No hay Express, FastAPI, Django, Rails ni ORM en el paquete |
| Gestor de paquetes del paquete | **Ninguno** | — | Distribución por tarball + `install.sh`; sin `pyproject.toml`, `setup.py`, `package.json` raíz ni lockfiles |
| Control de versiones | **Git** | `>= 2.0` | `.githooks/`, `scripts/check-*.py`, release por tag `v*` |
| CI/CD | **GitHub Actions** | — | `.github/workflows/ci.yml`, `release.yml`, `huginn-muninn.yml` |

### Inventario verificado

| Superficie | Cantidad | Fuente de verdad |
|---|---:|---|
| Workflows (slash commands) | **49** | `manifest.json`; `agent-dist/workflows/*.md` |
| Skills | **95** | `manifest.json`; `agent-dist/skills/*/SKILL.md` |
| Agentes | **9** | `agent-dist/agents/*.md` |
| Reglas | **18** | `agent-dist/rules/quinotospec-rules.md` |
| Templates | **13** | `agent-dist/templates/` |
| Scripts Python del payload | **32** | `find agent-dist -name '*.py'` |
| Scripts de automatización | **11** | `scripts/` |
| Suites de test shell | **28** | `tests/run-all-tests.sh` |
| Suites `unittest` Python | **7** | `tests/test-*.py` |
| Workflows de GitHub Actions | **3** | `.github/workflows/` |
| Dependencias obligatorias de terceros | **0** | Solo stdlib de Python y herramientas del sistema |

### Dependencias de terceros

**Cero dependencias Python obligatorias.** Los scripts usan `argparse`, `json`, `re`, `sys`, `pathlib`, `hashlib`, `subprocess`, `datetime`, `shutil`, `tempfile`, `http.server` y `urllib`.

Única dependencia **opcional**:

```python
# agent-dist/skills/quinotospec-extension-manager/extension_manager.py
import yaml  # soft-import con try/except ImportError
```

Si PyYAML no está disponible, existe un parser YAML reducido de respaldo. **El paquete funciona sin PyYAML.**

Dependencias de los proyectos de ejemplo (no del paquete):

| Ejemplo | Gestor | Dependencias principales |
|---|---|---|
| `examples/python-fastapi` | pip | `fastapi>=0.115,<1`, `uvicorn>=0.30,<1`, `pydantic>=2.7,<3`, `pytest>=8,<9`, `httpx>=0.27,<1`, `pytest-cov>=5,<7` |
| `examples/node-express` | npm | `express ^4.18.2`; dev: `jest ^29.7.0`, `supertest ^6.3.3` |
| `examples/rust-axum` | Cargo | `axum 0.7`, `tokio 1`, `serde 1`, `serde_json 1` |

> Los ejemplos **no forman parte del runtime del paquete** y se usan como playground y validación de la metodología.

## 🧪 Quality & Testing

| Rol | Herramienta | Cómo se ejecuta |
|---|---|---|
| Test runner principal | **Harness Bash propio** | `bash tests/run-all-tests.sh` |
| Test runner Python | **`unittest` (stdlib)** | `python3 tests/test-contract.py` o `python3 -m unittest tests.test_backup` |
| Linter shell | **`shellcheck`** con versión fijada | `./scripts/lint-shell.sh` |
| Sintaxis Bash | `bash -n` | Integrado en `scripts/validate-all.sh` |
| JSON | `python3 -m json.tool` | CI `lint-runtime` y `validate-all.sh` |
| JavaScript | `node --check` | CI `lint-runtime` y `validate-all.sh` |
| Enlaces internos | `scripts/check-links.sh --internal-only` | Integrado en `validate-all.sh` |
| Paridad README ES/EN | `scripts/check-readme-parity.py` | Integrado en `validate-all.sh` |
| Comandos citados en docs | `scripts/check-readme-commands.py` | Integrado en `validate-all.sh` |
| Drift skill ↔ workflow | `scripts/check-skill-workflow-drift.py` | Integrado en `validate-all.sh` |
| Cobertura del paquete | **No instrumentada** | No hay `coverage.py` ni `pytest-cov` para `agent-dist/` |
| Cobertura del playground | `pytest-cov` | `cd examples/python-fastapi && pytest --cov=app` |

### Tipos de prueba detectados

| Tipo | Dónde | Ejemplos |
|---|---|---|
| **Unit** | `tests/test-*.py`, scripts con fixtures | `test-contract.py`, `test-backup.py`, `test-approval.py`, `test-extensions.py`, `test-agents.py`, `test-rules-enforce.py` |
| **Integration** | Suites shell contra scripts reales y fixtures | `test-install.sh`, `test-rules-enforce.sh`, `test-evidence.sh`, `test-constitution.sh`, `test-nordic-skills.sh` |
| **E2E** | Instalación real en sandbox `mktemp -d` | `test-install-e2e.sh` (install → verify → ownership → rollback → uninstall) |
| **Smoke de release** | Tarball extraído e instalado | `scripts/smoke-release.sh` |
| **HTTP UI** | `ThreadingHTTPServer` real en puerto efímero | `tests/test-ui.sh` |
| **Portabilidad** | Comprobaciones Linux/macOS y CI matrix | `test-portability.sh`, `ci.yml` |

### Comandos de test

```bash
# Suite completa (28 suites; falla si hay suites huérfanas)
bash tests/run-all-tests.sh

# Gate completo del paquete: tests + gobernanza + links + versión + inventario + DAG
bash scripts/validate-all.sh --strict

# Gate sin Node.js instalado (evita que el warning sea fatal)
bash scripts/validate-all.sh --strict --allow-no-node

# Suite puntual
bash tests/test-ui.sh
bash tests/test-install-e2e.sh

# Test Python puntual
python3 -B tests/test-contract.py
python3 -m unittest tests.test_backup.BackupTests.test_create_verify_list_and_secret_exclusion

# Cobertura del playground (opcional)
cd examples/python-fastapi
pip install -r requirements.txt
pytest --cov=app --cov-report=term
```

**Resultado observado durante este discovery:**

```text
Test Suite: 28/28 suites verdes
validate-all.sh --strict: 0 errores, 0 warnings
Playground FastAPI: 5/5 tests, cobertura 97% (31 statements, 1 sin cubrir en app/routes/users.py)
```

### Cobertura y áreas sin tests medibles

- El paquete **no mide cobertura** de `agent-dist/`. No hay umbral ni reporte.
- El playground mide **97%** con `pytest-cov`; ese número no cubre el paquete.
- Áreas con cobertura débil o indirecta:
  - `agent-dist/blood-bond*` (analyzer, monitor, predictor) sin suite dedicada.
  - `agent-dist/skills/quinotospec-bifrost` tiene cobertura funcional en `test-nordic-skills.sh`, pero no de fallos de red/permisos.
  - Ramas de error del instalador (permisos, symlinks hostiles, disco lleno) solo parcialmente cubiertas.
  - Renderizado completo de todas las páginas de la UI y accesibilidad no están cubiertos.
  - Contrato JSON de salida de cada CLI no se valida contra un schema estable.

## 📝 Coding Standards (Detected)

1. **Bash estricto y defensivo**: `set -euo pipefail`, `trap` de restauración, locks de instalación y comprobaciones explícitas antes de escribir.
2. **Transaccionalidad por staging**: se instala en un directorio hermano, se verifica y recién entonces se reemplaza el destino con `mv`.
3. **Ownership por SHA-256**: `.quinoto-spec/ownership.json` registra cada archivo gestionado; `uninstall` no borra archivos modificados por el usuario.
4. **Rechazo de symlinks** en rutas administradas y allow-list explícita para territorio ajeno.
5. **Portabilidad macOS + Linux**: helpers como `titlecase()` evitan construcciones no soportadas por Bash 3.2 de macOS; CI corre en ambos sistemas.
6. **Cero dependencias en el camino crítico**: PyYAML y Node.js son opcionales; el paquete degrada con warnings, no con errores.
7. **Contrato de artefactos**: IDs canónicos `MNEMONIC-SUFFIX` + `US-…`/`TSK-…`, estados normalizados y parser legacy read-only (`contract.py`).
8. **Gobernanza ejecutable**: `rules_enforce.py`, `evidence_validate.py`, `approval_validate.py`, `tdd_validate.py` y `constitution_validate.py` aplican gates observables.
9. **Changelog append-only**: v2 con un archivo por entrada para evitar conflictos de merge; nunca se edita una entrada existente.
10. **UI read-only**: `readers.py` solo lee; el servidor no escribe en `.quinoto-spec/`.
11. **Configuración por capas**: `agent-defaults.toml` → `agent-team.toml` → `agent-personal.toml`; la última capa gana.
12. **Documentación y código en español técnico**, con convención de nombres `quinotospec-*` y `quinotospec.*`.

## 🔒 Acoplamiento de versión

La versión `3.4.0` está replicada en:

- `manifest.json`
- `install.sh` (`INSTALLER_VERSION`)
- `.version`
- `.cursor-plugin/plugin.json`

Y se verifica además contra:

- badges de `README.md` y `README_EN.md`
- cabecera de `CHANGELOG.md`
- `V3_ROADMAP.md`
- `docs/ARCHITECTURE.md`

El gate `scripts/validate-all.sh` y el workflow `release.yml` fallan si hay drift. Para cambios de versión usar `scripts/update-version.sh`.

## ⚠️ Datos que requieren ejecución o permisos

| Dato faltante | Cómo obtenerlo | Permiso necesario |
|---|---|---|
| Versión exacta del IDE del usuario | `opencode --version`, `cursor --version`, `claude --version` | Ejecutar el binario del IDE |
| Instalación real en cada IDE | `./install.sh --<ide> --global` y reiniciar el IDE | Escritura en `$HOME` y reinicio |
| Cobertura del paquete | Instrumentar `coverage.py` sobre `tests/` y scripts | Añadir dependencia de desarrollo o usar `trace` |
| Auditoría Cargo | `cargo install cargo-audit && cargo audit` en `examples/rust-axum` | Red y toolchain Rust |
| Auditoría npm real del ejemplo | `cd examples/node-express && npm install && npm audit` | Red y creación de `package-lock.json` |
| Comportamiento de hooks en IDEs cerrados | Probar sesión real en Cursor/Claude/Cline | Reinicio y credenciales del IDE |

## 🔗 Referencias

- `manifest.json` — inventario y feature flags
- `install.sh` — instalador transaccional
- `agent-dist/ui/` — dashboard local
- `scripts/validate-all.sh` — gate de validación
- `.github/workflows/ci.yml` — definición de CI
- `docs/ARCHITECTURE.md` — arquitectura y matriz de madurez
- `docs/ARTIFACT-CONTRACT.md` — contrato de artefactos
