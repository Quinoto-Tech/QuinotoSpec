---
description: Ayudar al desarrollador a crear agentes abstractos especializados basados en el discovery y estructura del proyecto
---

# Command: agent-train

Lee la skill `quinotospec-agent-train` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-agent-train/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-agent-train/SKILL.md`, `.cursor/skills/quinotospec-agent-train/SKILL.md`, `.claude/skills/quinotospec-agent-train/SKILL.md`, `.agent/skills/quinotospec-agent-train/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-agent-train/SKILL.md`, `~/.cursor/skills/quinotospec-agent-train/SKILL.md`, `~/.claude/skills/quinotospec-agent-train/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
