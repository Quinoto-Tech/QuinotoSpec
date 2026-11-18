---
description: Inicializa la estructura .quinoto-spec/ desde cero sin ejecutar discovery completo. Crea directorios, archivos template y prepara el proyecto para usar QuinotoSpec. Si el proyecto está vacío, ofrece un wizard interactivo para generar un scaffold con el stack tecnológico deseado.
---

# Command: init

Lee la skill `quinotospec-init` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-init/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-init/SKILL.md`, `.cursor/skills/quinotospec-init/SKILL.md`, `.claude/skills/quinotospec-init/SKILL.md`, `.agent/skills/quinotospec-init/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-init/SKILL.md`, `~/.cursor/skills/quinotospec-init/SKILL.md`, `~/.claude/skills/quinotospec-init/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
