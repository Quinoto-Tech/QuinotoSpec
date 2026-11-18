---
description: Ejecución paralela de múltiples agentes para tareas masivas
---

# Command: battle-frenzy

Lee la skill `quinotospec-battle-frenzy` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-battle-frenzy/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-battle-frenzy/SKILL.md`, `.cursor/skills/quinotospec-battle-frenzy/SKILL.md`, `.claude/skills/quinotospec-battle-frenzy/SKILL.md`, `.agent/skills/quinotospec-battle-frenzy/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-battle-frenzy/SKILL.md`, `~/.cursor/skills/quinotospec-battle-frenzy/SKILL.md`, `~/.claude/skills/quinotospec-battle-frenzy/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
