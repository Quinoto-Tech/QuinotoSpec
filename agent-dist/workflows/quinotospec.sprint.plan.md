---
description: Genera el plan de sprint óptimo basado en el estado actual, prioridades y estimaciones
---

# Command: sprint.plan

Lee la skill `quinotospec-sprint-plan` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-sprint-plan/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-sprint-plan/SKILL.md`, `.cursor/skills/quinotospec-sprint-plan/SKILL.md`, `.claude/skills/quinotospec-sprint-plan/SKILL.md`, `.agent/skills/quinotospec-sprint-plan/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-sprint-plan/SKILL.md`, `~/.cursor/skills/quinotospec-sprint-plan/SKILL.md`, `~/.claude/skills/quinotospec-sprint-plan/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
