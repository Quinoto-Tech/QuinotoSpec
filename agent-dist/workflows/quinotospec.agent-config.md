---
description: Configuracion 3-layer de agentes — guia la creacion de overrides de equipo y personales sin editar el paquete.
---

# Command: agent-config

Lee la skill `quinotospec-agent-config` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-agent-config/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-agent-config/SKILL.md`, `.cursor/skills/quinotospec-agent-config/SKILL.md`, `.claude/skills/quinotospec-agent-config/SKILL.md`, `.agent/skills/quinotospec-agent-config/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-agent-config/SKILL.md`, `~/.cursor/skills/quinotospec-agent-config/SKILL.md`, `~/.claude/skills/quinotospec-agent-config/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
