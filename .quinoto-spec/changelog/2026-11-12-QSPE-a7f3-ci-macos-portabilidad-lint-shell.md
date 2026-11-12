---
date: 2026-11-12
prefix: QSPE-a7f3
slug: ci-macos-portabilidad-lint-shell
type: fix
---

## [2026-11-12] - CI: estabilizar macOS y shellcheck, y blindar portabilidad

### Resumen
- `test (macos-latest)` fallaba por `touch -d "90 days ago"` (GNU-only) en `tests/test-help-and-routing.sh`; reemplazado por `python3 os.utime` (`touch_days_ago`)
- `lint-shell` fallaba por hallazgos reales (SC2319, SC2015, SC2046, SC2034) y por `SC2317`, un falso positivo que depende de la versión de shellcheck
- Versión de shellcheck fijada en `.shellcheck-version` (0.11.0): CI descarga esa versión exacta y corre `scripts/lint-shell.sh` como fuente única
- Nuevo `tests/test-portability.sh` (registrado en `run-all-tests.sh`) que falla ante `touch -d`, `grep -P`, `sed -i` sin sufijo, `mapfile`/`readarray`, `stat -c` o `date -d`
- `scripts/validate-all.sh` deja de usar `mapfile` (compatible con el bash 3.2 de macOS); `scripts/update-version.sh` usa solo `sed -i.bak`
- `.githooks/pre-commit` corre shellcheck con la versión fijada cuando hay `.sh` staged
- Evidencia completa en `.quinoto-spec/fixes/20261112-2249-ci-macos-portabilidad-lint-shell.md`

**Verificacion**: `./scripts/lint-shell.sh` (39 scripts clean), `bash tests/run-all-tests.sh` (26/26 suites), `bash scripts/validate-all.sh --strict` (0 errores), `package-release` + `smoke-release` OK

**Tiempo Ahorrado**: ~4h (IA: ~50min vs Humano: ~4h de ida y vuelta con el job de macOS)
