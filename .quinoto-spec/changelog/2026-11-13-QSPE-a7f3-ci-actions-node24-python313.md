---
date: 2026-11-13
prefix: QSPE-a7f3
slug: ci-actions-node24-python313
type: fix
---

## [2026-11-13] - CI: actions en runtime Node 24, cobertura Python 3.13 y guard de higiene

### Resumen
- `actions/checkout` v4 → v7, `actions/setup-python` v5 → v7 y `softprops/action-gh-release` v2 → v3 en los 3 workflows (9 + 3 + 1 referencias), en el snippet de la skill `huginn-muninn` y en el discovery de DevOps
- Runtime Node 20 → Node 24: desaparecen los warnings de deprecacion que aparecian en **todos** los runs
- Job `compatibility`: se agrega Python **3.13** (antes solo 3.8 y 3.11, dejando sin cobertura a lo que corre la mayoria); `package-smoke` pasa a 3.13 (la compatibilidad la cubre `compatibility`)
- Job de macOS: ya no instala `shellcheck` (el lint corre en `lint-shell` con la version fijada): ~20s menos y un punto de falla menos
- Nuevo `tests/test-ci-config.sh` (registrado en el runner): falla si una action queda por debajo del major minimo, si el job de macOS instala shellcheck, si `compatibility` deja de cubrir 3.8 o 3.13, o si un workflow no parsea como YAML (python3+PyYAML o ruby de fallback)
- `.quinoto-spec/discovery/06-devops-ci-security.md`: tabla de jobs actualizada (versiones, 3.13, alcance de `lint-shell`)

**Verificacion**: `tests/test-ci-config.sh` 5 checks 0 errores (probe con `checkout@v4` detectado como `< minimo v7`), `lint-shell` 40 scripts clean, `validate-all --strict` 0 errores, suite completa 27/27

**Tiempo Ahorrado**: ~1h (IA: ~25min vs Humano: ~1h de leer release notes de 3 actions y validar la matriz)
