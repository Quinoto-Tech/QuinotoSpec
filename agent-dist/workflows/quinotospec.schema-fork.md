---
description: Crea una copia personalizada del schema de artefactos para adaptarlo al flujo del proyecto
---

# Command: schema-fork

Lee la skill `quinotospec-schema-fork` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-schema-fork/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-schema-fork/SKILL.md`, `.cursor/skills/quinotospec-schema-fork/SKILL.md`, `.claude/skills/quinotospec-schema-fork/SKILL.md`, `.agent/skills/quinotospec-schema-fork/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-schema-fork/SKILL.md`, `~/.cursor/skills/quinotospec-schema-fork/SKILL.md`, `~/.claude/skills/quinotospec-schema-fork/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
