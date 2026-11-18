---
description: Exportar propuestas, tareas y user stories a formatos externos (JSON, CSV, Markdown consolidado)
---

# Command: export

Lee la skill `quinotospec-export` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-export/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-export/SKILL.md`, `.cursor/skills/quinotospec-export/SKILL.md`, `.claude/skills/quinotospec-export/SKILL.md`, `.agent/skills/quinotospec-export/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-export/SKILL.md`, `~/.cursor/skills/quinotospec-export/SKILL.md`, `~/.claude/skills/quinotospec-export/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
