---
date: 2026-11-08
prefix: QSPE-a7f3
slug: consolidacion-codigo-i18n-release
format: v2
type: maintenance
---

## [2026-11-08] - Consolidación de código Python, i18n y robustez de release

### Resumen
- **D1 — Lib común**: creado `agent-dist/lib/quinotospec_common.py` con `resolve_root`, `load_module_from_path` y `load_contract_module`; migrados 7 scripts (`bifrost`, `blood-bond`, `-analyzer`, `-monitor`, `-predictor`, `mimir/index`, `valkyrie/rank`) que duplicaban esos bloques literalmente. Net -1.5k líneas de duplicación.
- **D2 — Personas**: `agent-dist/config/agent-defaults.toml` queda como fuente canónica de personalidad; `agent-dist/agents/*.md` sincronizados y test de paridad en `tests/test-agents.py`.
- **D3 — OpenCode v1**: documentado como ruta **legacy** en `manifest.json` y README ES/EN (se mantiene como fallback real para OpenCode 1.x; v2 es la recomendada).
- **D4 — Search/Mimir**: `quinotospec-search` deja de ser prompt-only; nuevo `search.py` que delega el scoring BM25 en `quinotospec-mimir/search.py` y agrega filtros `--type/--prefix/--since/--status/--json/--cite`. Tests end-to-end en `test-nordic-skills.sh`.
- **D5 — Blood-Bond**: documentada la arquitectura de 4 entrypoints sobre código compartido (skill + workflow).
- **E — i18n**: `quinotospec-file-creation` traducido al español; headings en inglés corregidos en `debug/*`, `party-orchestrator/strategies/*`, `artifact-engine`, `worktree`, `metrics` y los 9 agentes. Convención de idioma documentada en `CONTRIBUTING.md`.
- **F1 — Smoke test**: `smoke-release.sh` ahora recorre opencode, cursor, claude, cline y antigravity (install → verify → uninstall) en targets aislados.
- **F2 — Conteos derivados**: `validate-all.sh` lee los conteos desde `manifest.json` y compara contra el disco en igualdad exacta; `install.sh` deriva sus umbrales del manifest. Una sola fuente.
- **F3 — Preflight de release**: `package-release.sh` advierte si el árbol está sucio (`REQUIRE_CLEAN=1` lo vuelve bloqueante) y ejecuta drift + link checker antes de empaquetar (`SKIP_PREFLIGHT=1` para omitir).
- **F4 — Paridad README**: nuevo `scripts/check-readme-parity.py` (H2, tablas, bloques de código, imágenes) integrado en `validate-all.sh`; corregido el drift real detectado (faltaba `Quick Start` en `README_EN.md`, badges e imágenes del header).
- **Instalador**: `agent-dist/lib/` registrado en el ownership manifest (opencode y cursor), corrigiendo que `--uninstall` dejara `.opencode/lib/` atrás. `docs/ARCHITECTURE.md` actualizado (48 workflows, 94 skills, `lib/`).

**Validacion**: `bash scripts/validate-all.sh --strict` -> 0 errores, 0 warnings; `tests/run-all-tests.sh` -> 24/24 suites verdes.

**Tiempo Ahorrado**: ~12h (IA: ~70min vs Humano: ~12h de refactor, traduccion y hardening de CI)

**Version**: sin bump (cambios internos; sigue 3.3.0).
