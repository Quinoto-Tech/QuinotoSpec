---
description: Limpia branches stale, scripts temporales y propuestas inactivas. Modo dry-run por defecto — nunca borra sin confirmación.
---

# Command: cleanup

Lee la skill `quinotospec-cleanup` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-cleanup/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-cleanup/SKILL.md`, `.cursor/skills/quinotospec-cleanup/SKILL.md`, `.claude/skills/quinotospec-cleanup/SKILL.md`, `.agent/skills/quinotospec-cleanup/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-cleanup/SKILL.md`, `~/.cursor/skills/quinotospec-cleanup/SKILL.md`, `~/.claude/skills/quinotospec-cleanup/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
