---
description: Generar user stories basadas en una propuesta existente
---

# Command: create-user-stories

Lee la skill `quinotospec-create-user-stories` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-create-user-stories/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-create-user-stories/SKILL.md`, `.cursor/skills/quinotospec-create-user-stories/SKILL.md`, `.claude/skills/quinotospec-create-user-stories/SKILL.md`, `.agent/skills/quinotospec-create-user-stories/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-create-user-stories/SKILL.md`, `~/.cursor/skills/quinotospec-create-user-stories/SKILL.md`, `~/.claude/skills/quinotospec-create-user-stories/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
