---
description: Orquestador Enterprise — encadena el SDLC completo con constitution gates, compliance y aprobación humana estructurada.
---

# Command: flow

Lee la skill `quinotospec-flow` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-flow/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-flow/SKILL.md`, `.cursor/skills/quinotospec-flow/SKILL.md`, `.claude/skills/quinotospec-flow/SKILL.md`, `.agent/skills/quinotospec-flow/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-flow/SKILL.md`, `~/.cursor/skills/quinotospec-flow/SKILL.md`, `~/.claude/skills/quinotospec-flow/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
