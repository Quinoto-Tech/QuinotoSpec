# 🛠️ Stack Profile: QuinotoSpec

**Discovery Date:** 2026-09-27

Guardar en: .quinoto-spec/discovery/01-stack-profile.md

> Perfil detectado con la skill `quinotospec-stack-detect`. Este repositorio **no es una aplicación
> en tiempo de ejecución**: es un paquete de configuración y distribución para agentes de IA.
> No existe `package.json`, `pyproject.toml`, `requirements.txt` ni `go.mod` en la raíz.

## 🏗️ Core Technologies

| Rol | Tecnología | Versión mínima | Evidencia |
|---|---|---|---|
| Lenguaje principal | **Bash** | `>= 4.0` | `install.sh` (1278 líneas), `scripts/*.sh`, `tests/*.sh`; `manifest.json:112` (`min_requirements.bash: "4.0"`) |
| Lenguaje secundario | **Python** | `>= 3.8` | 15 scripts en `agent-dist/`, 7 en `tests/`; `manifest.json:115` (`python3: "3.8"`) |
| Lengaje terciario | **JavaScript** | — | **1 solo archivo**: `agent-dist/plugins/opencode/quinotospec-plugin.js` (115 líneas) |
| Configuración/documentación | **Markdown** | — | 158 archivos `.md` (86 `SKILL.md`, 43 workflows, 9 agents, docs) |
| Formato declarativo | **YAML / JSON** | — | 1 `.yaml` (schema DAG), 3 `.yml` (ext/preset/config), 3 `.json` (hooks) |
| Gestor de paquetes | **ninguno** | — | Se distribuye como tarball + `install.sh`. Sin `npm install` / `pip install` |
| Framework | **ninguno** | — | Sin framework web ni ORM; es lógica de shell + stdlib |

### Dependencias de terceros

**Cero dependencias Python obligatorias.** Los 15 scripts usan solo stdlib
(`argparse`, `json`, `re`, `sys`, `pathlib`, `hashlib`, `subprocess`, `datetime`, `shutil`, `tempfile`).

Única dependencia *opcional*:

```
agent-dist/skills/quinotospec-extension-manager/extension_manager.py:148
    import yaml  # type: ignore   → dentro de try/except ImportError
```

Con fallback a un parser YAML reducido hecho a mano (`parse_simple_yaml`, línea 150). **PyYAML no es
necesario** para que el paquete funcione.

**No existe metadata de empaquetado Python** en el repo (sin `pyproject.toml`, `setup.py`,
`requirements.txt`, `Pipfile`, `poetry.lock`). Es intencional: los scripts se invocan por ruta
(`python3 -B agent-dist/skills/.../script.py`). Los únicos `requirements.txt` / `Cargo.toml` del repo
pertenecen a proyectos de ejemplo (`examples/`) o fixtures (`tests/fixtures/`), no al paquete.

## 🧪 Quality & Testing

| Rol | Herramienta | Notas |
|---|---|---|
| Test runner (shell) | **Harness bash propio** | `tests/run-all-tests.sh`. Cada suite mantiene contadores `pass()`/`fail()` y retorna código ≠ 0 |
| Test runner (python) | **`unittest`** (stdlib) | 7 archivos `tests/test-*.py`, cada uno con su shim `.sh` de 4 líneas |
| Linter (shell) | **`shellcheck`** | `shellcheck -e SC2329 -x` en CI (`.github/workflows/ci.yml:57-72`) |
| Linter (bash syntax) | **`bash -n`** | `scripts/validate-all.sh:135-140` |
| Linter (JSON) | **`python3 -m json.tool`** | `scripts/validate-all.sh:141-148`; CI `lint-runtime` |
| Linter (JS) | **`node --check`** | `scripts/validate-all.sh:149-159`; CI `ci.yml:86` |
| Enlace interno de docs | **`scripts/check-links.sh`** | `scripts/validate-all.sh:57-67` |
| Detección de ciclos DAG | `quinotospec-jormungandr/check.py` | Kahn's algorithm sobre el schema YAML |
| Cobertura | **no instrumentada** | No hay `--coverage`, `pytest-cov` ni equivalente |

### Comandos de test

```bash
# Suite completa (20 suites, registro manual en run-all-tests.sh:42-61)
bash tests/run-all-tests.sh

# Gate completo (suite + gobernanza + enlaces + versionado + estructura + DAG)
bash scripts/validate-all.sh --strict

# Una suite puntual
bash tests/test-bootstrap.sh
bash tests/test-install-e2e.sh

# Un test python puntual
python3 tests/test-contract.py
python3 -m unittest tests.test-backup.BackupTests.test_create_verify_list_and_secret_exclusion
```

> ⚠️ **No hay auto-descubrimiento de tests.** `tests/run-all-tests.sh:42-61` contiene una lista
> hardcodeada de 20 suites. Agregar `tests/test-nuevo.sh` no lo ejecuta nadie hasta registrarlo ahí.
> Tampoco existe `Makefile`, `pytest.ini`, `conftest.py` ni `tox.ini`.

## 🚢 Infrastructure & DevOps

| Rol | Tecnología |
|---|---|
| Control de versiones | Git (89 commits, 4 autores; 30 commits en los últimos 90 días) |
| CI/CD | **GitHub Actions** — 3 workflows: `ci.yml`, `release.yml`, `huginn-muninn.yml` |
| Release | Tarball + SHA-256 (`scripts/package-release.sh`), verificado con `scripts/smoke-release.sh` |
| Git hooks | `.githooks/pre-commit` (solo frontmatter de archivos staged) y `.githooks/pre-push` (corre la suite completa) |
| Contenedores | **ninguno** (no hay `Dockerfile` ni `docker-compose.yml`) |
| Secrets en CI | Ninguno requerido |

Matriz de CI (`.github/workflows/ci.yml`): `test` (ubuntu + macos), `compatibility` (Python 3.8 y
3.11), `package-smoke`, `lint-shell`, `lint-runtime`, `lint-docs`, `structure`. El job `test` corre
`validate-all.sh --strict`, es decir **la suite completa bloquea el merge**.

## 📝 Coding Standards (Detected)

1. **Bash 4 estricto con safety rails**: `set -euo pipefail` (`install.sh:6`), handlers `trap` para
   rollback, y casi cada paso envuelto en `if ! ...; then print_error; exit 1; fi`.
2. **Portabilidad macOS + GNU/Linux**: `titlecase()` existe porque bash 3.2 de macOS no soporta
   `${var^}` (`install.sh:55`); CI corre en ambos sistemas operativos.
3. **Cero dependencia de herramientas opcionales en el camino crítico**: PyYAML es soft-import,
   Node solo se usa para `node --check` (y su ausencia genera warning, no error).
4. **Transacciones atómicas con staging hermano + `mv`**: nunca se escribe directamente en el
   destino vivo (`install.sh:98-124`, `1216-1242`).
5. **Ownership por hash SHA-256**: `.quinoto-spec/ownership.json` registra cada archivo instalado con
   su digest; `uninstall` se niega a borrar si el hash cambió (`install.sh:908-944`).
6. **Symlinks = rechazo duro** en cualquier ruta administrada, pero tolerados en territory ajeno
   (`install.sh:179-220`, con allow-list explícita en `:191-207`).
7. **Documentación y código en español técnico**; comentarios explicativos en el código.
8. **Apéndice-only en changelog v2** (un archivo por entrada) para evitar conflictos de merge.
9. **Gates de gobernanza ejecutables, no solo documentados**: `rules_enforce.py` corre en
   `validate-all.sh:41-53` con `--profile package --action preflight --mode strict`.

### Versión y acoplamiento de versión

La versión `3.2.0` está replicada en **4 lugares** y debe coincidir:
`manifest.json:3`, `install.sh:8` (`INSTALLER_VERSION`), `.version`, y
`.cursor-plugin/plugin.json`. `scripts/validate-all.sh:70-86` lo verifica; `release.yml:25-56` lo
re-valida contra el tag de git.

## 🔗 Referencias

- `manifest.json` — inventario y feature flags de máquina
- `install.sh` — instalador transaccional multi-IDE
- `scripts/validate-all.sh` — gate de validación del paquete
- `.github/workflows/ci.yml` — definición de CI
