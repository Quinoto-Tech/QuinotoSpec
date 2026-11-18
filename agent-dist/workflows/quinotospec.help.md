---
description: Navegacion contextual global — inspecciona .quinoto-spec/ y guia al usuario con el siguiente comando exacto.
---

# Command: help

Lee la skill `quinotospec-help` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-help/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-help/SKILL.md`, `.cursor/skills/quinotospec-help/SKILL.md`, `.claude/skills/quinotospec-help/SKILL.md`, `.agent/skills/quinotospec-help/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-help/SKILL.md`, `~/.cursor/skills/quinotospec-help/SKILL.md`, `~/.claude/skills/quinotospec-help/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
