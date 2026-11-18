---
description: Genera una guia de code review para el revisor humano cuando una propuesta esta completada, consolidando propuesta, historias, tareas, evidencia, changelog y cambios en git en un solo archivo
---

# Command: review-handoff

Lee la skill `quinotospec-review-handoff` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-review-handoff/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-review-handoff/SKILL.md`, `.cursor/skills/quinotospec-review-handoff/SKILL.md`, `.claude/skills/quinotospec-review-handoff/SKILL.md`, `.agent/skills/quinotospec-review-handoff/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-review-handoff/SKILL.md`, `~/.cursor/skills/quinotospec-review-handoff/SKILL.md`, `~/.claude/skills/quinotospec-review-handoff/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
