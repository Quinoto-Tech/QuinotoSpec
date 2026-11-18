---
description: aplicar la tarea correspondiente
---

# Command: apply

Lee la skill `quinotospec-apply` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-apply/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-apply/SKILL.md`, `.cursor/skills/quinotospec-apply/SKILL.md`, `.claude/skills/quinotospec-apply/SKILL.md`, `.agent/skills/quinotospec-apply/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-apply/SKILL.md`, `~/.cursor/skills/quinotospec-apply/SKILL.md`, `~/.claude/skills/quinotospec-apply/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
