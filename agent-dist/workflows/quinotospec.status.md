---
description: Genera un Panel de Control (Dashboard) del estado del proyecto
---

# Command: status

Lee la skill `quinotospec-status` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-status/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-status/SKILL.md`, `.cursor/skills/quinotospec-status/SKILL.md`, `.claude/skills/quinotospec-status/SKILL.md`, `.agent/skills/quinotospec-status/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-status/SKILL.md`, `~/.cursor/skills/quinotospec-status/SKILL.md`, `~/.claude/skills/quinotospec-status/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
