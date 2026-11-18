---
description: Lanza el dashboard web local read-only de QuinotoSpec (discovery, propuestas, tareas, changelog y constitución) sin modificar archivos. [En desarrollo]
---

# Command: ui

Lee la skill `quinotospec-ui` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-ui/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-ui/SKILL.md`, `.cursor/skills/quinotospec-ui/SKILL.md`, `.claude/skills/quinotospec-ui/SKILL.md`, `.agent/skills/quinotospec-ui/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-ui/SKILL.md`, `~/.cursor/skills/quinotospec-ui/SKILL.md`, `~/.claude/skills/quinotospec-ui/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
