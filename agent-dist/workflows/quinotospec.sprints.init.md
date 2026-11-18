---
description: Inicializa la estructura de configuración de sprints del proyecto
---

# Command: sprints.init

Lee la skill `quinotospec-sprints-init` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-sprints-init/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-sprints-init/SKILL.md`, `.cursor/skills/quinotospec-sprints-init/SKILL.md`, `.claude/skills/quinotospec-sprints-init/SKILL.md`, `.agent/skills/quinotospec-sprints-init/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-sprints-init/SKILL.md`, `~/.cursor/skills/quinotospec-sprints-init/SKILL.md`, `~/.claude/skills/quinotospec-sprints-init/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
