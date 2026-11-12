# Fix: CI rojo en master (macOS + lint-shell) y deuda de portabilidad

- **Fecha**: 2026-11-12 22:49
- **Descripción**: La suite de CI sobre `master` fallaba en `test (macos-latest)` y `lint-shell`. Ambos fallos eran de portabilidad/versión de herramienta, no del producto: un `touch -d` (GNU-only) en un test y hallazgos de shellcheck que además dependían de la versión instalada en el runner.
- **Comportamiento esperado**: `./scripts/validate-all.sh --strict` verde en Linux y macOS; `shellcheck` limpio con una versión determinista; un dev con Mac puede clonar y correr los gates sin tocar nada.
- **Comportamiento actual (antes del fix)**: `test (macos-latest)` terminaba con `1 errors` y `lint-shell` con exit 1. Un dev con Mac reproduciendo localmente veía un error de `touch` que no tenía relación con su cambio.
- **Stack detectado**: paquete de configuración de agentes (Markdown + Bash + Python 3.8+); test runner `tests/run-all-tests.sh` vía `scripts/validate-all.sh`; CI en `.github/workflows/ci.yml`.

## Causa raíz

**1. `test (macos-latest)` — `touch -d` es GNU-only**

`tests/test-help-and-routing.sh` envejecía el discovery con:

```bash
touch -d "90 days ago" "$STALE_PROJECT/.quinoto-spec/discovery/01-stack-profile.md"
```

En BSD/macOS el flag `-d` no existe (`touch: out of range or illegal time specification`), el archivo quedaba con mtime actual y el check `help.py detecta discovery obsoleto (>30 dias)` fallaba por `AssertionError` sobre `data["discovery"]["stale"]`.

**2. `lint-shell` — set de checks dependiente de la versión de shellcheck**

El job usaba el binario preinstalado del runner; el workflow local usaba brew/lo que hubiera. `SC2317` (falso positivo sobre handlers de `trap` en `install.sh`) aparece en unas versiones y no en otras, así que el mismo commit pasaba en una máquina y fallaba en otra. Además había hallazgos reales independientes de la versión (`SC2319`, `SC2015`, `SC2046`, `SC2034`).

**3. Deuda de portabilidad no cubierta por ningún gate**

Otros patrones GNU-only dormidos: `mapfile` en `scripts/validate-all.sh` (bash 4+; macOS trae bash 3.2), `grep -P` en `tests/test-workflows.sh` (PCRE ausente en BSD, el check se salteaba en silencio) y un fallback `sed -i` sin sufijo en `scripts/update-version.sh`.

## Evidencia

**RED — CI (run 42466161321, commit 877559c)**

```
test (macos-latest)  X Run package gates
  touch: out of range or illegal time specification: YYYY-MM-DDThh:mm:SS[.frac][tz]
  AssertionError
  ❌ help.py detecta discovery obsoleto (>30 dias)
  Results: 1 errors, 0 warnings

lint-shell  X Shellcheck all bash scripts
  SC2317 (install.sh), SC2319 (test-help-and-routing.sh, test-skill-workflow-drift.sh),
  SC2015 + SC2046 (test-help-and-routing.sh), SC2034 (test-nordic-skills.sh, test-worktree.sh)
  ##[error]Process completed with exit code 1
```

**RED — local (Linux, shellcheck 0.11.0)**

```
$ for f in install.sh agent-dist/hooks/*.sh scripts/*.sh tests/*.sh .githooks/*; do shellcheck -e SC2329 -x "$f"; done
SC2319 x7 / SC2015 / SC2046 / SC2034 x4  → FAILED=1
```

**GREEN**

```
$ ./scripts/lint-shell.sh
shellcheck 0.11.0 (pinned: 0.11.0)
shellcheck: 39 scripts clean
exit=0

$ bash tests/test-portability.sh
Resultados: 5 checks, 0 errores
✅ Portabilidad GNU/Linux <-> macOS sin patrones bloqueantes
exit=0

$ bash scripts/validate-all.sh --strict
Results: 0 errors, 0 warnings
All validations passed
exit=0

$ bash tests/run-all-tests.sh
Total: 26 suites | ✅ Pas: 26 | ❌ Fail: 0
exit=0

$ bash scripts/package-release.sh 3.4.0 /tmp/opencode/qdist && bash scripts/smoke-release.sh /tmp/opencode/qdist/quinotospec-3.4.0.tar.gz
Release smoke test passed
exit=0
```

**RED del guard nuevo (mutation probe)**: se agregó `tests/temp_probe.sh` con `touch -d` y `tests/test-portability.sh` falló señalando `tests/temp_probe.sh:2`; al removerlo volvió a verde.

## Cambios

- `tests/test-help-and-routing.sh`: helper `touch_days_ago` con `python3 os.utime`; `$?` capturado en variable (SC2319); loop de tracks sin `A && B || C` (SC2015/SC2046).
- `tests/test-workflows.sh`: chequeo de caracteres de control con `python3` en lugar de `grep -P`.
- `tests/test-skill-workflow-drift.sh`, `tests/test-nordic-skills.sh`, `tests/test-worktree.sh`: RCs explícitos y variables usadas en diagnóstico (SC2319/SC2034).
- `scripts/validate-all.sh`: `mapfile` → `while read` (bash 3.2 compatible).
- `scripts/update-version.sh`: `portable_sed` solo con `sed -i.bak` (GNU y BSD).
- `.shellcheck-version` (nuevo, `0.11.0`) + `scripts/lint-shell.sh` (nuevo): fuente única de la versión y del set de archivos a lintear.
- `.github/workflows/ci.yml`: `lint-shell` descarga la versión fijada y corre `scripts/lint-shell.sh`; `.shellcheck-version`, `scripts/lint-shell.sh` y `tests/test-portability.sh` pasan a ser archivos requeridos del job `structure`.
- `tests/test-portability.sh` (nuevo) + registro en `tests/run-all-tests.sh`: falla si reaparecen `touch -d`, `grep -P`, `sed -i` sin sufijo, `mapfile`/`readarray`, `stat -c` o `date -d`.
- `.githooks/pre-commit`: corre shellcheck con la versión fijada cuando hay `.sh` staged.
- `CONTRIBUTING.md`: sección "Gates locales (mismos que CI)" con la restricción de portabilidad.

## Riesgo

BAJO — cambios en tests, tooling de CI y un helper de `sed`. Sin impacto en los artefactos que instala el paquete ni en el contrato de agentes. `install.sh` sigue requiriendo bash 4.0+ (con aviso explícito), pero el resto del tooling ya corre en el bash 3.2 de macOS.

## Pendiente conocido (fuera de este fix)

- `package-smoke` falló en el mismo run por `Unexpected HTTP response: 504` al resolver `actions/setup-python@v5`: es infraestructura de GitHub, no del repo (no requiere cambio).
- Verificación real en macOS: el guard es estático y corre en Linux; la confirmación definitiva es el job `test (macos-latest)` del próximo push.
