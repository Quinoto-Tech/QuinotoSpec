---
description: Ejecuta un análisis exhaustivo de amenazas con STRIDE y evaluación de riesgo con DREAD
---

# Command: heimdallr

Lee la skill `quinotospec-heimdallr` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-heimdallr/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-heimdallr/SKILL.md`, `.cursor/skills/quinotospec-heimdallr/SKILL.md`, `.claude/skills/quinotospec-heimdallr/SKILL.md`, `.agent/skills/quinotospec-heimdallr/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-heimdallr/SKILL.md`, `~/.cursor/skills/quinotospec-heimdallr/SKILL.md`, `~/.claude/skills/quinotospec-heimdallr/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
