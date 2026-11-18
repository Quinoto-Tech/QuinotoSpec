---
description: Muestra el changelog consolidado del proyecto, combinando entradas del formato v2 (changelog/) y v1 (quinoto-spec-changelog.md). Ofrece filtros por fecha, prefijo y tipo.
---

# Command: changelog-view

Lee la skill `quinotospec-changelog-view` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-changelog-view/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-changelog-view/SKILL.md`, `.cursor/skills/quinotospec-changelog-view/SKILL.md`, `.claude/skills/quinotospec-changelog-view/SKILL.md`, `.agent/skills/quinotospec-changelog-view/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-changelog-view/SKILL.md`, `~/.cursor/skills/quinotospec-changelog-view/SKILL.md`, `~/.claude/skills/quinotospec-changelog-view/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
