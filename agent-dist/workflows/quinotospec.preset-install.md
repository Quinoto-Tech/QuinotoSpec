---
name: quinotospec.preset-install
description: Instala un preset local o de catálogo con prioridad explícita y resolución de templates.
---

# Command: preset-install

Lee la skill `quinotospec-preset-install` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-preset-install/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-preset-install/SKILL.md`, `.cursor/skills/quinotospec-preset-install/SKILL.md`, `.claude/skills/quinotospec-preset-install/SKILL.md`, `.agent/skills/quinotospec-preset-install/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-preset-install/SKILL.md`, `~/.cursor/skills/quinotospec-preset-install/SKILL.md`, `~/.claude/skills/quinotospec-preset-install/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
