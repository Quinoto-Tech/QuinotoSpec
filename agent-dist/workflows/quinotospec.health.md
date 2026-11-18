---
description: Detecta archivos huérfanos, inconsistencias entre _archived/ y propuestas activas, y problemas de integridad en la estructura .quinoto-spec/. Para dashboard ejecutivo ver @quinotospec.status.
---

# Command: health

Lee la skill `quinotospec-health` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-health/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-health/SKILL.md`, `.cursor/skills/quinotospec-health/SKILL.md`, `.claude/skills/quinotospec-health/SKILL.md`, `.agent/skills/quinotospec-health/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-health/SKILL.md`, `~/.cursor/skills/quinotospec-health/SKILL.md`, `~/.claude/skills/quinotospec-health/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
