---
date: 2026-11-13
prefix: PWRE-9f2c
slug: proposal-playwright-onboarding
format: v2
type: proposal
---

## [2026-11-13] - Proposal Updated: Playwright Dependency Onboarding

### Resumen
- **Propuesta ampliada**: `.quinoto-spec/proposals/2026-11-13-playwright-proposal-review/proposal.md` ahora incluye onboarding cuando la persona no tiene Playwright.
- **Doctor nuevo**: `playwright_doctor.py` detecta Node, `@playwright/test`, Chromium y Playwright MCP; devuelve `app`, `mcp`, `options` y `recommended`.
- **Menú de tres opciones**: instalar Playwright app, configurar Playwright MCP u omitir el review visual. La instalación nunca es automática.
- **Flags nuevos**: `--playwright-backend auto|app|mcp`, `--install-playwright`, `--install-playwright-mcp`, `--no-install-prompt`, `--require-playwright`. `--yes` por sí solo no autoriza instalar.
- **Modo no interactivo**: sin decisión ni flags devuelve `action_required` con exit code distinto de 0; el review estándar solo continúa con `skipped` explícito.
- **Evidencia**: el JSON incorpora bloque `dependency` con app/MCP, backend elegido, acción de instalación y consentimiento.
- **Delta spec actualizada**: `delta-specs/workflow/spec.md` agrega `Playwright Dependency Onboarding` y `Playwright Install Consent`, con escenarios para app, MCP, omitir, no-TTY y `--yes`.
- **Estimación ajustada**: de 6–9 a **8–11 días** por la fase de onboarding y sus tests.

**Verificación**: `contract.py validate --root . --strict` → `Valid: True`, 0 errores, 0 warnings.

**Tiempo Ahorrado**: ~45m (IA: ~10m vs Humano: ~45m de rediseñar onboarding, flags, delta spec y criterios de aceptación)

