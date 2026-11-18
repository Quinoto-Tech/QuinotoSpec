---
description: Check rápido pre-commit que ejecuta tests del stack + validación de sintaxis + enforcement de reglas
---

# Command: pre-commit

Lee la skill `quinotospec-pre-commit` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-pre-commit/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-pre-commit/SKILL.md`, `.cursor/skills/quinotospec-pre-commit/SKILL.md`, `.claude/skills/quinotospec-pre-commit/SKILL.md`, `.agent/skills/quinotospec-pre-commit/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-pre-commit/SKILL.md`, `~/.cursor/skills/quinotospec-pre-commit/SKILL.md`, `~/.claude/skills/quinotospec-pre-commit/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
