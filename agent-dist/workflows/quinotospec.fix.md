---
description: Resolver bugs y fixes menores sin necesidad de propuesta formal — rápido, documentado, con tests.
---

# Command: fix

Lee la skill `quinotospec-fix` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-fix/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-fix/SKILL.md`, `.cursor/skills/quinotospec-fix/SKILL.md`, `.claude/skills/quinotospec-fix/SKILL.md`, `.agent/skills/quinotospec-fix/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-fix/SKILL.md`, `~/.cursor/skills/quinotospec-fix/SKILL.md`, `~/.claude/skills/quinotospec-fix/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
