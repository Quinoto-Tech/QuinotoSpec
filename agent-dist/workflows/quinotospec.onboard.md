---
description: Genera un documento de onboarding personalizado por rol para nuevos integrantes del equipo, basado en el discovery y el estado actual del proyecto.
---

# Command: onboard

Lee la skill `quinotospec-onboard` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-onboard/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-onboard/SKILL.md`, `.cursor/skills/quinotospec-onboard/SKILL.md`, `.claude/skills/quinotospec-onboard/SKILL.md`, `.agent/skills/quinotospec-onboard/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-onboard/SKILL.md`, `~/.cursor/skills/quinotospec-onboard/SKILL.md`, `~/.claude/skills/quinotospec-onboard/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
