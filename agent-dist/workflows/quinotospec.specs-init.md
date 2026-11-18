---
description: Inicializa el directorio specs/ desde discovery o propuestas existentes
---

# Command: specs-init

Lee la skill `quinotospec-specs-init` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-specs-init/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-specs-init/SKILL.md`, `.cursor/skills/quinotospec-specs-init/SKILL.md`, `.claude/skills/quinotospec-specs-init/SKILL.md`, `.agent/skills/quinotospec-specs-init/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-specs-init/SKILL.md`, `~/.cursor/skills/quinotospec-specs-init/SKILL.md`, `~/.claude/skills/quinotospec-specs-init/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
