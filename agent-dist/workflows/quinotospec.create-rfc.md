---
description: Crear un Request for Comments (RFC) en modo conversacional, compatible con create-tasks --from-rfc
---

# Command: create-rfc

Lee la skill `quinotospec-create-rfc` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-create-rfc/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-create-rfc/SKILL.md`, `.cursor/skills/quinotospec-create-rfc/SKILL.md`, `.claude/skills/quinotospec-create-rfc/SKILL.md`, `.agent/skills/quinotospec-create-rfc/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-create-rfc/SKILL.md`, `~/.cursor/skills/quinotospec-create-rfc/SKILL.md`, `~/.claude/skills/quinotospec-create-rfc/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
