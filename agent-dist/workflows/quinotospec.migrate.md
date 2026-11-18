---
description: Migrar entre versiones de QuinotoSpec con deteccion de breaking changes y backup automatico
---

# Command: migrate

Lee la skill `quinotospec-migrate` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-migrate/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-migrate/SKILL.md`, `.cursor/skills/quinotospec-migrate/SKILL.md`, `.claude/skills/quinotospec-migrate/SKILL.md`, `.agent/skills/quinotospec-migrate/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-migrate/SKILL.md`, `~/.cursor/skills/quinotospec-migrate/SKILL.md`, `~/.claude/skills/quinotospec-migrate/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
