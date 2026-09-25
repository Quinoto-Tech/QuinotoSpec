---
date: 2026-09-24
prefix: QSPE-a7f3
slug: f1-1-bootstrap-sesion
format: v2
type: change
---

## [2026-09-24] - F1.1: bootstrap automático de sesión

### Resumen
- Se añadió `agent-dist/bootstrap/quinotospec-bootstrap.md` con el contexto Proposal First, reglas de ejecución, comandos esenciales y red flags.
- Se implementaron `session-start.sh`, `run-hook.cmd` y configuraciones JSON para Claude Code, Cursor y OpenCode.
- Se añadió el plugin `quinotospec-plugin.js` con registro de paths, cache, guard anti-duplicado e inyección del bootstrap en el primer mensaje.
- `install.sh` ahora instala el runtime, agrega el target Claude Code, preserva hooks existentes y aplana el plugin OpenCode en `plugins/`.
- Se actualizaron manifest, documentación, CI, release y pruebas E2E para validar el runtime de sesión.

**Tiempo Ahorrado**: ~4h (IA: ~35min vs Humano: ~4h)
