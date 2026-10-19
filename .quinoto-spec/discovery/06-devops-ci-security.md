# DevOps, CI y Seguridad: QuinotoSpec

**Discovery Date:** 2026-09-27

Guardar en: .quinoto-spec/discovery/06-devops-ci-security.md

## Entorno de desarrollo

### Requisitos verificados por el instalador

```bash
bash >= 4.0    # install.sh:513-520
git  >= 2.0    # install.sh:523-531
python3 >= 3.8 # install.sh:533-545
```

Opcionales: `node` (solo `node --check` del plugin), `shellcheck` (solo CI).

### Variables de entorno

**El paquete no requiere ninguna variable de entorno.** No hay `.env`, ni `.env.example`, ni
referencias a tokens o claves. El instalador no lee el entorno más allá de `$HOME`.

Variables que el *instalador* define internamente (`install.sh:8-21`), no de entrada:

| Var | Propósito |
|---|---|
| `INSTALLER_VERSION` | `3.2.0`; se escribe en el ownership manifest |
| `DIR` / `PROJECT_ROOT` / `TARGET_ROOT` | source vs destino |
| `TRANSACTION_DIR` | staging hermano (`mktemp -d`) |
| `FINAL_CONFIG_DIR` | directorio real del IDE |
| `TRANSACTION_COMMITTED` | flag de commit; gobierna el rollback |
| `AGENTS_MANAGED` | si el instalador es dueño del `AGENTS.md` |

### Variables deEntorno de test (inyección de fallos)

```bash
QUINOTOSPEC_INSTALL_TEST_MODE=true
QUINOTOSPEC_INSTALL_FAIL_STAGE=after-config   # fuerza un fallo post-commit
```

Ejercita el rollback en `tests/test-install-e2e.sh:193-202`. **Solo para tests**: si se exportan en
producción, rompen la instalación a propósito.

## Pipelines de CI/CD

### `.github/workflows/ci.yml` — quality gate principal

**Triggers**: `push` a `master`/`main`/`release-*`; `pull_request` a `master`/`main`.

| Job | Runner | Qué hace |
|---|---|---|
| `test` | ubuntu + macos (matrix) | `validate-all.sh --strict` (suite completa). En macOS instala `shellcheck` |
| `compatibility` | Python 3.8 y 3.11 | `validate-all.sh --strict` en ambas versiones |
| `package-smoke` | Python 3.8 | `package-release.sh` + `smoke-release.sh` sobre el tarball |
| `lint-shell` | ubuntu | `shellcheck -e SC2329 -x` sobre `install.sh`, `hooks/*.sh`, `scripts/*.sh`, `tests/*.sh`, `.githooks/*` |
| `lint-runtime` | ubuntu | `json.tool` en hooks + `node --check` en el plugin |
| `lint-docs` | ubuntu | `check-links.sh --internal-only` + convenciones de nombres (warnings no fatales) |
| `structure` | ubuntu | `REQUIRED_DIRS` incluye `agent-dist/plugins`; `REQUIRED_FILES` incluye el plugin y `hooks-opencode.json` |

**Bloquea el merge.** `test` y `compatibility` ejecutan la suite completa vía `validate-all.sh --strict`.

### `.github/workflows/release.yml` — publicación

**Trigger**: tags `v*`. Un solo job en `ubuntu-latest`, `permissions: contents: write`.

1. Checkout `fetch-depth: 0` + Python 3.11
2. **Cross-check de versión en 4 lugares** (`:25-56`): tag == `.version` == `manifest.json` ==
   `install.sh:INSTALLER_VERSION` == `.cursor-plugin/plugin.json`, y `CHANGELOG.md` tiene `## [$VERSION]`
3. `release_status: "beta-rc"` ⇒ `prerelease: true`
4. **`validate-all.sh --strict`** (`:69`) — gate duro
5. `package-release.sh` → tarball + `.sha256`
6. `smoke-release.sh` — install/verify/uninstall sobre el tarball extraído
7. `softprops/action-gh-release@v2` con el tarball y su checksum

### `.github/workflows/huginn-muninn.yml` — observabilidad de entropía

**Triggers**: `pull_request` (todas), `push` a `master`/`main`, **cron diario 06:00 UTC**, manual.

- `validate-all.sh --strict 2>&1 | head -n 100 || true` — **explícitamente no bloqueante**
- Corre `huginn-muninn/check.sh --json`
- **Único bloqueo**: falla el job si `S_final >= 0.76`, indicando ejecutar Tiwaz Rune y Mjolnir

## Scripts de automatización

| Script | Propósito |
|---|---|
| `scripts/validate-all.sh` | Gate de 7 validaciones (`--strict`) |
| `scripts/package-release.sh` | Empaqueta tarball + SHA-256 (verifica el checksum al escribirlo) |
| `scripts/smoke-release.sh` | install → verify → manifest → uninstall sobre el tarball |
| `scripts/update-version.sh` | Bump de versión sincronizado en los 4 lugares; `--dry-run` soportado |
| `scripts/check-links.sh` | Enlaces internos rotos; `--internal-only` |
| `scripts/cleanup-temp.sh` | Limpieza de scripts temporales |
| `scripts/install-hooks.sh` | Instala los git hooks (distinto del instalador de IDEs) |

### Cron jobs

Ninguno en el paquete. El único cron es el de `huginn-muninn.yml` (06:00 UTC diario), que es
observabilidad, no parte del runtime.

## Revisión de seguridad

### ✅ Lo que está bien

| Control | Implementación |
|---|---|
| **Ownership por hash** | `uninstall` aborta si un archivo propio fue modificado (`:908-944`) |
| **No borra archivos ajenos** | Solo toca `owned`; prune de directorios con `rmdir` (`:989-997`) |
| **Refuse-to-overwrite** | `check_agents_conflict` (`:222-265`) + `prepare_candidate` (`:123-177`) |
| **Symlinks rechazados en territory gestionado** | Allow-list explícita (`:191-207`); los symlinks ajenos se preservan |
| **Rollback automático** | `trap EXIT` + `restore_transaction` |
| **Fail-closed en gobernanza** | Las reglas BLOCKING detienen el workflow |
| **Exclusión de secretos en backup** | `.env`, `credentials`, `id_rsa`, `id_ed25519` (`backup.py:19`) |
| **Aprobación humana registrada** | `.quinoto-spec/approvals/*.json` con match exacto de subject+action |
| **Documentos de contexto privilegiado** | Las instrucciones se marcan privileged en v2 |
| **Sin superficie de red** | No hay `urllib`/`socket`/`http`; superficie de ataque remota = 0 |

### ⚠️ Superficie de ataque real

| Vector | Evaluación |
|---|---|
| **Ejecución de código vía config del proyecto** | `install.sh` ejecuta `python3 -B update_agents.py` con `--config "$TARGET_ROOT/.quinoto-spec/config.yaml"`. Ese YAML se parsea con el parser reducido o PyYAML. **No se ejecuta código**, pero un config malicioso controla el contenido del `AGENTS.md` generado (que es *instrucción* para el agente ⇒ vector de prompt injection) |
| **Prompt injection vía artefactos** | proposals, stories y `AGENTS.md` son texto que el agente lee. Es el riesgo estructural del dominio, no un bug |
| **Escritura fuera del target** | `update_agents.py:202-206` exige que el output esté bajo `--root` salvo `--allow-external-output`. El instalador **sí** lo pasa (`:1197`) porque escribe a staging |
| **Race / concurrencia** | No hay lock. Dos instalaciones simultáneas al mismo target colisionarían. El staging es `mktemp -d` (único) pero el commit `mv` no es atómico entre los dos pasos (`:1216-1222`) |
| **TOCTOU en verificación de ownership** | Se hashea, luego se borra. Ventana pequeña, impacto bajo |

### 🔴 Hallazgo crítico de seguridad de despliegue

`install.sh` **no consulta la versión del IDE de destino**. Es la causa directa del incidente
documentado en `07-findings-and-recommendations.md`: el instalador escribió un plugin con contrato v1
en un host que ya corría OpenCode v2 (contrato v2), y **no había forma de que el instalador lo supiera
ni lo advirtiese**. Un chequeo de versión en el paso de pre-flight habría convertido un fallo
silencioso en un error accionable.

## Auditoría de dependencias

### Resultado: sin superficie de supply-chain vulnerable

```bash
# No hay package manager. No aplica npm audit / pip-audit / bundle audit.
```

| Ecosistema | Superficie | Hallazgos |
|---|---|---|
| Python (paquete) | **0 dependencias obligatorias** | ✅ Ninguna. Los 15 scripts son stdlib puro |
| Python (opcional) | `PyYAML` — soft import en `extension_manager.py:148` | ⚠️ Ver nota abajo |
| Node | Sin `package.json` en el paquete. El plugin usa solo `node:fs`/`node:path` | ✅ Ninguna |
| Shell | Sin gestor de paquetes. Herramientas del sistema | ⚠️ No auditadas (fuera de alcance) |
| Sistema | Depende de `git` y `python3` del PATH | ⚠️ No auditadas |

> **Nota sobre PyYAML**: es un import opcional dentro de `try/except ImportError` con fallback a un
> parser reducido hecho a mano. **PyYAML no es necesario** para que el paquete funcione. Si se
> instala, es responsabilidad del usuario. No hay `requirements.txt` que lo fije, así que no hay
> versión pineada — este es el único punto de exposición real.

### Fixtures que sí tienen dependencias (no ejecutadas)

`tests/fixtures/python-project/requirements.txt` importa `fastapi`/`pytest`, y
`examples/python-fastapi/requirements.txt` y `examples/rust-axum/Cargo.toml` existen. **Ninguno lo
ejecuta `run-all-tests.sh`** — son material de ejemplo para stack-detect. No deben contarse como
dependencias del paquete.

## Estrategia de backup, versionado y recuperación

### Versionado

Semver (`3.2.0`), replicado en **4 archivos** y validado en `validate-all.sh:70-86` y
`release.yml:25-56`. `manifest.json:6` marca `release_status: "beta-rc"` ⇒ el tag se publica como
**prerelease** automáticamente.

La herramienta de versionado es `scripts/update-version.sh`, con `--dry-run` (testeado en
`test-checkers.sh`), preservando `rules:` y `templates:` (verificado en `test-constitution.sh:68`).

### Backup

```bash
python3 agent-dist/skills/quinotospec-backup/backup.py create --type full
python3 agent-dist/skills/quinotospec-backup/backup.py verify --backup <id>
python3 agent-dist/skills/quinotospec-backup/backup.py restore --backup <id> --yes
```

4 tipos (`full`/`incremental`/`proposals`/`discovery`), manifest SHA-256, restauración fail-safe
(verifica antes de tocar, y hace backup de seguridad del estado actual).

### Recuperación ante desastre

| Escenario | Mecanismo |
|---|---|
| Instalación a medias | Rollback automático por `trap EXIT` |
| Artefactos corruptos | `backup.py verify` detecta, `restore` recupera |
| Release defectuosa | `smoke-release.sh` la detiene antes de publicar |
| Archivos propios alterados | `uninstall --verify` lo detecta y **aborta** en vez de borrar |
| `.quinoto-spec` perdido | Es texto en git; `git checkout` basta. Los backups son para estado no versionado |

## Costura detectada: el gate depende de Node

`validate-all.sh:156-159` degrada a **warning** si falta Node, pero `:191` vuelve **fatal** cualquier
warning bajo `--strict`. Como `ci.yml:26` y `ci.yml:42` usan `--strict`, en la práctica **el gate
exige Node** aunque el paquete declare Node como opcional. Inconsistencia de contrato documentada en
`07-findings-and-recommendations.md`.

## 🔗 Referencias

- `04-endpoints-and-openapi.md` — superficies de CLI
- `07-findings-and-recommendations.md` — auditoría de dependencias y hallazgos
- `.github/workflows/ci.yml` — definición de CI
- `docs/ARCHITECTURE.md` — modelo transaccional
