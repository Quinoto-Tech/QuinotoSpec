---
description: Generar documentación de descubrimiento del stack consolidado para proyectos distribuidos en múltiples sub-carpetas
---

# Command: stack-discovery

Lee la skill `quinotospec-stack-discovery` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-stack-discovery/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-stack-discovery/SKILL.md`, `.cursor/skills/quinotospec-stack-discovery/SKILL.md`, `.claude/skills/quinotospec-stack-discovery/SKILL.md`, `.agent/skills/quinotospec-stack-discovery/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-stack-discovery/SKILL.md`, `~/.cursor/skills/quinotospec-stack-discovery/SKILL.md`, `~/.claude/skills/quinotospec-stack-discovery/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
