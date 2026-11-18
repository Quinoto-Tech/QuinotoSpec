---
description: Refresca solo los archivos de discovery afectados por cambios recientes en el proyecto, sin regenerar los 8 archivos completos
---

# Command: refresh-discovery

Lee la skill `quinotospec-refresh-discovery` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-refresh-discovery/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-refresh-discovery/SKILL.md`, `.cursor/skills/quinotospec-refresh-discovery/SKILL.md`, `.claude/skills/quinotospec-refresh-discovery/SKILL.md`, `.agent/skills/quinotospec-refresh-discovery/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-refresh-discovery/SKILL.md`, `~/.cursor/skills/quinotospec-refresh-discovery/SKILL.md`, `~/.claude/skills/quinotospec-refresh-discovery/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
