---
description: Importar tareas y user stories desde fuentes externas (GitHub Issues, Jira CSV, CSV, JSON)
---

# Command: import

Lee la skill `quinotospec-import` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-import/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-import/SKILL.md`, `.cursor/skills/quinotospec-import/SKILL.md`, `.claude/skills/quinotospec-import/SKILL.md`, `.agent/skills/quinotospec-import/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-import/SKILL.md`, `~/.cursor/skills/quinotospec-import/SKILL.md`, `~/.claude/skills/quinotospec-import/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
