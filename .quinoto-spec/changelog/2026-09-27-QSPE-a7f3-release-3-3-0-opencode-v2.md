---
date: 2026-09-27
prefix: QSPE-a7f3
slug: release-3-3-0-opencode-v2
format: v2
type: feat
---

## [2026-09-27] - Release 3.3.0 y Soporte Nativo OpenCode v2 (F3.3)

### Resumen
- Soporte nativo para OpenCode v2 (F3.3) mediante el plugin ESM sin dependencias `agent-dist/plugins/opencode-v2/index.js` con hooks `context` y `compaction`.
- Detección automática `detect_opencode_major` y bandera `--opencode-major` en `install.sh` para seleccionar el payload v1 o v2.
- Actualización del frontmatter de los 9 agentes en `agent-dist/agents/*.md` agregando `mode: subagent` y `description`.
- Sincronización de versión `3.3.0` en `manifest.json`, `.version`, `.cursor-plugin/plugin.json`, `install.sh`, `README.md`, `README_EN.md`, `docs/ARCHITECTURE.md`, `V3_ROADMAP.md` y `CHANGELOG.md`.

**Tiempo Ahorrado**: ~4h (IA: ~35min vs Humano: ~4h)
