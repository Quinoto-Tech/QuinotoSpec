---
date: 2026-11-13
prefix: PWRE-9f2c
slug: code-review-playwright-proposal
type: review
---

## [2026-11-13] - Code Review: PWRE-9f2c (Playwright Proposal Review)

### Resumen
- Se revisó la implementación completa de `2026-11-13-playwright-proposal-review` (8 historias, 32 tareas) sobre el working tree (no hay branch: está sin commitear sobre `master`). Resultado: **Requiere cambios**
- **3 BLOCKING**: (1) el rechazo de path traversal escribe la evidencia fuera de `.quinoto-spec/reviews/` con el slug sin sanitizar y, con más `..`, crashea con traceback; (2) `QS_FORCE_MISSING_PLAYWRIGHT` está documentado en el proposal y el DoD pero no existe en el código; (3) el onboarding promete Node 18+ mientras `@playwright/test 1.65` exige Node ≥ 20
- **9 WARN**: MCP "generic" reporta `configured: true` escribiendo un `./mcp.json` que ningún IDE lee; `@playwright/mcp@latest` sin pin y `npm install` en vez de `npm ci`; la evidencia versionable filtra rutas absolutas del equipo; `PIPE` sin drenar y sin kill de grupo; `actions/setup-node@v4` (Node 20) fuera del guard de CI; archivos no declarados + discovery refresh mezclado en el mismo árbol; faltan tests de `install-app`/éxito/fallo/timeout; el harness sí viaja en el payload instalable; override DoR sin `.quinoto-spec/approvals/`
- **3 INFO**: `--check-only` duplicado y parámetro muerto en `build_install_commands`; 8 de 10 checks prometidos (falta enlaces internos y el check de screenshots); a11y no cubre `select` ni botón de tema
- Gates en verde: contrato 0 errores, **29/29 suites**, `validate-all --strict` 0/0, `test-review-playwright.sh` 19 checks, doctor 4/4, orquestador 6/6, dogfooding Playwright `pass` (2/2 Mermaid, 3 viewports, 0 console errors)
- Informe completo: `.quinoto-spec/reviews/2026-11-13-playwright-proposal-review-code-review.md`

**Puntos pendientes:** B-01 sanitizar slug en `write_evidence` y no escribir fuera de `reviews/`; B-02 implementar o quitar `QS_FORCE_MISSING_PLAYWRIGHT`; B-03 umbral Node 20 en doctor/prompt/docs. Luego WARN de pin/reproducibilidad y correr `ui-playwright` en CI.

**Tiempo Ahorrado**: ~3h (IA: ~45min de revisión con evidencia reproducible vs Humano: ~3h de lectura de 1.8k líneas + reproducir el traversal)
