---
date: 2026-11-13
prefix: PWRE-9f2c
slug: fixes-post-code-review
type: fix
---

## [2026-11-13] - Fixes post code review (PWRE-9f2c)

### Resumen
- **B-01 (seguridad)**: el camino de error escribia evidencia con el slug sin validar, fuera de `.quinoto-spec/reviews/` (path traversal) y con `../../..` tiraba `Traceback`. Se agrega `safe_slug()` y el write queda en `try/except OSError`, devolviendo JSON con `EXIT_USAGE`
- **B-02**: se implementa `QS_FORCE_MISSING_PLAYWRIGHT=1` (estaba documentado en el proposal y el DoD pero no existia); el doctor fuerza app/MCP ausentes y marca `forced_missing_playwright`
- **B-03**: umbral de Node pasa de 18 a `MIN_NODE_MAJOR = 20`, porque `@playwright/test 1.65` declara `engines: node>=20`. Actualizados prompt, opciones, blockers, `docs/PLAYWRIGHT-REVIEW.md` y proposal
- **W-02/W-03/W-04/W-05/W-07/W-08** resueltos: `npm ci` en vez de `npm install`; evidencia con rutas relativas o `~/` (`sanitize_paths`); log de la UI a archivo + `start_new_session` + `killpg`; `actions/setup-node@v7` cubierto por `test-ci-config.sh`; 13 tests de orquestador (install-app, fallo, exito, timeout, traversal, privacidad) y 6 del doctor; afirmacion del payload corregida
- **W-01/W-09 pendientes**: MCP "generic" reportando `configured: true` (decision de UX) y registro de aprobacion humana del override DoR
- Evidencia regenerada con el dogfooding: `pass`, 9 checks, 2/2 Mermaid, 3 viewports, 0 console errors, sin rutas absolutas

**Verificacion**: contrato OK · `lint-shell` 42 scripts clean · 29/29 suites · `validate-all --strict` 0 errores · `test-review-playwright.sh` 19 checks · orquestador 13/13 · doctor 6/6

**Tiempo Ahorrado**: ~4h (IA: ~50min vs Humano: ~4h entre reproducir el traversal, entender engines de Playwright y escribir los 7 tests faltantes)
