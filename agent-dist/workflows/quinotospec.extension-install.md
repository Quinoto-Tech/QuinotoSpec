---
name: quinotospec.extension-install
description: Instala una extensión local o de catálogo con validación de manifest, staging y registro auditable.
---

# Command: extension-install

Lee la skill `quinotospec-extension-install` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-extension-install/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-extension-install/SKILL.md`, `.cursor/skills/quinotospec-extension-install/SKILL.md`, `.claude/skills/quinotospec-extension-install/SKILL.md`, `.agent/skills/quinotospec-extension-install/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-extension-install/SKILL.md`, `~/.cursor/skills/quinotospec-extension-install/SKILL.md`, `~/.claude/skills/quinotospec-extension-install/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
