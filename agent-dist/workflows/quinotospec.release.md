---
description: Automatiza el proceso de release: version bump, consolidación de changelog, tagging y publicación
---

# Command: release

Lee la skill `quinotospec-release` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-release/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-release/SKILL.md`, `.cursor/skills/quinotospec-release/SKILL.md`, `.claude/skills/quinotospec-release/SKILL.md`, `.agent/skills/quinotospec-release/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-release/SKILL.md`, `~/.cursor/skills/quinotospec-release/SKILL.md`, `~/.claude/skills/quinotospec-release/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
