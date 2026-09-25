---
date: 2026-09-25
prefix: QSPE-a7f3
slug: installer-foreign-symlink-fix
format: v2
type: bugfix
---

## [2026-09-25] - Fix: install global fallaba por symlinks ajenos

### Resumen
- `reject_candidate_symlinks` escaneaba todo el directorio de configuración staged y rechazaba symlinks ajenos (p. ej. `node_modules/.bin` de OpenCode), abortando `install.sh --opencode --global`.
- El chequeo ahora se limita a los paths gestionados (rules, skills, agents, templates, bootstrap, hooks, plugins, commands/workflows, quinotospec-plugin, .quinoto-spec, hooks.json, settings.json).
- Se preserva la protección: symlinks en paths gestionados siguen bloqueando la instalación antes del commit.
- Regresión cubierta en `tests/test-install-e2e.sh`: symlinks ajenos se ignoran y se conservan.

**Tiempo Ahorrado**: ~1h (IA: ~15min vs Humano: ~1h)
