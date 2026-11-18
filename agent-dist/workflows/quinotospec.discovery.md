---
description: Generar documentación de descubrimiento del proyecto en .quinoto-spec/discovery
---

# Command: discovery

Lee la skill `quinotospec-discovery` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-discovery/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-discovery/SKILL.md`, `.cursor/skills/quinotospec-discovery/SKILL.md`, `.claude/skills/quinotospec-discovery/SKILL.md`, `.agent/skills/quinotospec-discovery/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-discovery/SKILL.md`, `~/.cursor/skills/quinotospec-discovery/SKILL.md`, `~/.claude/skills/quinotospec-discovery/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
