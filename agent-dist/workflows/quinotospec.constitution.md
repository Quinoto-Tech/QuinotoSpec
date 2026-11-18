---
description: Genera y gobierna la constitución del proyecto con principios verificables y aprobación explícita
---

# Command: constitution

Lee la skill `quinotospec-constitution` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-constitution/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-constitution/SKILL.md`, `.cursor/skills/quinotospec-constitution/SKILL.md`, `.claude/skills/quinotospec-constitution/SKILL.md`, `.agent/skills/quinotospec-constitution/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-constitution/SKILL.md`, `~/.cursor/skills/quinotospec-constitution/SKILL.md`, `~/.claude/skills/quinotospec-constitution/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
