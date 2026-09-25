---
name: quinotospec-norns
description: Las Tejedoras del Destino — versionado atomico y changelog semversado sin drift. Sincroniza version en todos los docs, genera entrada v2 y valida sin dejar desfases.
---

# Skill: Quinotospec Norns — Las Tejedoras del Destino

> Las 3 Nornas tejen el destino bajo Yggdrasil. Esta skill teje la version en cada hilo del proyecto sin que quede uno deshilachado.

## Cuando usar

- Antes de cualquier `release`, `bump` o tag
- Cuando `manifest.json` vs `.version` vs `install.sh` vs `README` vs `ARCHITECTURE.md` vs `CHANGELOG.md` driftan
- Como gate pre-`quinotospec.release`

## Invocacion

```bash
/quinotospec-norns --to 3.2.0
/quinotospec-norns --to 3.2.0 --dry-run
/quinotospec-norns --check   # solo reporta drift sin tocar
```

## Comportamiento

### 1. Check (drift detection)

Lee y compara:

| Fuente | Campo | Esperado |
|--------|-------|----------|
| `.version` | contenido | `X.Y.Z` |
| `manifest.json` | `version`, `workflows`, `skills`, `rules` | FS real (`find ... \| wc -l`) |
| `install.sh` | `INSTALLER_VERSION=` | igual a `.version` |
| `README.md` / `README_EN.md` | badges `version-`, `workflows-`, `skills-`, `rules-` | igual a manifest |
| `docs/ARCHITECTURE.md` | diagrama `workflows/skills/rules` + headings `Workflows (N)` | igual a FS |
| `CHANGELOG.md` | `## [X.Y.Z]` existe para version actual | — |
| `V3_ROADMAP.md` | `Version actual:` | igual a `.version` |
| `scripts/validate-all.sh` | `EXPECTED_COUNTS` | igual a FS |
| `agent-dist/templates/schema-template.yaml` | `template:` refs existen | — |

Si hay mismatch → reporta tabla `OK/DRIFT` y sale con codigo 1 en `--check`.

### 2. Bump atomico (`--to X.Y.Z`)

1. Valida semver `X.Y.Z` y que `X.Y.Z > current` (semver compare)
2. Determina edition:
   - `3.x` → `Warband: Hird`
   - `2.7+` → `Yggdrasil — Tiwaz Rune`
   - `2.1-2.6` → `Berserker`
   - `2.0` → `Possessed`
3. Ejecuta `scripts/update-version.sh X.Y.Z` (portable `sed -i.bak`)
4. Post-sync extra (lo que `update-version.sh` no hacia antes):
   - `README.md` / `README_EN.md` badges `version-`, `skills-`, `rules-`, `workflows-` + conteos de reglas del baseline
   - `docs/ARCHITECTURE.md` diagrama + headings
   - `V3_ROADMAP.md` `Version actual:`
   - `scripts/validate-all.sh` `EXPECTED_COUNTS`
   - Verifica `schema-template.yaml` templates existen (no dangling refs)
5. Genera entrada changelog v2 si el proyecto usa `changelog/`:
   - `changelog/YYYY-MM-DD-NORN-bump-X.Y.Z.md` desde `changelog-entry-template.md`
   - Incluye `git diff --stat specs/..` si hay specs
6. Valida: `bash tests/run-all-tests.sh && bash scripts/validate-all.sh --strict` (o `--internal-only` si sin red)
7. Reporta `git status --short` y sugiere `git add -A && git commit -m "chore: bump version to X.Y.Z (Norns)"`

### 3. Dry-run

Con `--dry-run` no escribe, solo imprime diff propuesto (usar `diff -u` por archivo).

## Reglas

- Nunca editar `CHANGELOG.md` manualmente → Norns lo hace atomico
- Nunca dejar drift: si `--check` falla, bloquea `release` (BLOCKING)
- Portable: `sed -i.bak` + `rm *.bak`, `grep -oE` no `-P`, `shopt -s globstar` safe

## Integracion

- `quinotospec.release` debe invocar `quinotospec-norns --to X` antes de taggear
- `validate-all.sh` ya delega conteo a Norns como source of truth
