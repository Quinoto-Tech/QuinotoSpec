---
name: quinotospec.update-agents
description: Regenera AGENTS.md desde config.yaml y el inventario activo del proyecto.
---

# Command: update-agents

Lee la skill `quinotospec-update-agents` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-update-agents/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-update-agents/SKILL.md`, `.cursor/skills/quinotospec-update-agents/SKILL.md`, `.claude/skills/quinotospec-update-agents/SKILL.md`, `.agent/skills/quinotospec-update-agents/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-update-agents/SKILL.md`, `~/.cursor/skills/quinotospec-update-agents/SKILL.md`, `~/.claude/skills/quinotospec-update-agents/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
