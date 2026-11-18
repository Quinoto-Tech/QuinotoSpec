---
description: crea tareas a partir de user stories o desde un RFC (create-rfc)
---

# Command: create-tasks

Lee la skill `quinotospec-create-tasks` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-create-tasks/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-create-tasks/SKILL.md`, `.cursor/skills/quinotospec-create-tasks/SKILL.md`, `.claude/skills/quinotospec-create-tasks/SKILL.md`, `.agent/skills/quinotospec-create-tasks/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-create-tasks/SKILL.md`, `~/.cursor/skills/quinotospec-create-tasks/SKILL.md`, `~/.claude/skills/quinotospec-create-tasks/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
