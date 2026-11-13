---
date: 2026-11-13
prefix: PWRE-9f2c
slug: playwright-review-implemented
format: v2
type: feature
---

## [2026-11-13] - Playwright Review Implemented

### Resumen
- **Review visual opcional**: `@quinotospec.review --playwright` ahora abre la propuesta en la UI local con Playwright/Chromium, valida render, Mermaid, consola, `pageerror`, requests fallidos, overflow responsive y accesibilidad smoke.
- **Doctor y onboarding**: `playwright_doctor.py` detecta Node, `@playwright/test`, Chromium y MCP. Si falta Playwright, `playwright_review.py` ofrece instalar la app, configurar MCP u omitir; nunca instala sin confirmación y `--yes` no autoriza instalaciones.
- **Backends**: `auto`, `app` y `mcp`. El backend app es determinista para CI; el backend MCP delega en las herramientas del IDE y devuelve `action_required` si requiere reinicio.
- **Evidencia**: `.quinoto-spec/reviews/<slug>-playwright.json` + `.md`; screenshots en `.quinoto-spec/reviews/.artifacts/`, ignorado por Git.
- **UI**: render de `proposal.md` en `/proposals/<slug>`, `data-testid` estables, `data-mermaid-state` (`pending`/`rendered`/`error`), tablas con scroll horizontal y corrección de overflow móvil.
- **Harness E2E**: `agent-dist/skills/quinotospec-review/e2e/` con `@playwright/test`, Chromium, `playwright.config.js`, spec y reporter JSON; fixture en `tests/fixtures/quinoto-spec-playwright/`.
- **CI**: job `ui-playwright` condicionado a cambios de UI/review/tests, con cache de npm y Chromium.
- **Instalador**: el payload excluye `node_modules` mediante tar y respeta `node_modules` ajenos; `check-links.sh` y el conteo de skills ignoran `node_modules`.
- **Documentación**: `docs/PLAYWRIGHT-REVIEW.md`, README ES/EN, `docs/ARCHITECTURE.md`, `manifest.json` y `CHANGELOG.md`.

### Archivos principales
- `agent-dist/skills/quinotospec-review/playwright_doctor.py` — nuevo
- `agent-dist/skills/quinotospec-review/playwright_review.py` — nuevo
- `agent-dist/skills/quinotospec-review/mcp_config.py` — nuevo
- `agent-dist/skills/quinotospec-review/e2e/{package.json,package-lock.json,playwright.config.js,proposal-review.spec.js,reporter.js}` — nuevos
- `agent-dist/skills/quinotospec-review/SKILL.md` — modificado
- `agent-dist/workflows/quinotospec.review.md` — modificado
- `agent-dist/ui/readers.py`, `agent-dist/ui/templates.py` — modificados
- `tests/test-playwright-doctor.py`, `tests/test-review-playwright.py`, `tests/test-review-playwright.sh` — nuevos
- `tests/test-ui.sh`, `tests/run-all-tests.sh` — modificados
- `tests/fixtures/quinoto-spec-playwright/` — nuevo
- `.github/workflows/ci.yml` — modificado
- `install.sh`, `scripts/validate-all.sh`, `scripts/check-links.sh` — modificados
- `docs/PLAYWRIGHT-REVIEW.md` — nuevo
- `README.md`, `README_EN.md`, `docs/ARCHITECTURE.md`, `manifest.json`, `CHANGELOG.md`, `.gitignore` — modificados

### Verificación
- `bash tests/run-all-tests.sh` → **29/29 suites verdes**.
- `bash scripts/validate-all.sh --strict` → **0 errores, 0 warnings**.
- `QS_RUN_PLAYWRIGHT=1 bash tests/test-review-playwright.sh` → **20/20 checks**, E2E real sobre el fixture.
- Dogfooding: `playwright_review.py --root . --proposal 2026-11-13-playwright-proposal-review --playwright-backend app` → **pass**, 2/2 bloques Mermaid renderizados, 0 errores de consola, 0 `pageerror`, 0 requests fallidos.
- `contract.py validate --root . --strict` → `Valid: True`.

**Tiempo Ahorrado**: ~8h (IA: ~1h30 vs Humano: ~8h de implementar doctor, onboarding, orquestador, harness E2E, UI, tests, CI y docs)

