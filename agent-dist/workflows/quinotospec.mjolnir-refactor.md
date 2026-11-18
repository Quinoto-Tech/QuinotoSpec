---
description: Flujo para generar una Propuesta de Refactor "Mjolnir" que reescribe módulos enteros bajo demanda.
---

# Command: mjolnir-refactor

Lee la skill `quinotospec-mjolnir-refactor` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-mjolnir-refactor/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-mjolnir-refactor/SKILL.md`, `.cursor/skills/quinotospec-mjolnir-refactor/SKILL.md`, `.claude/skills/quinotospec-mjolnir-refactor/SKILL.md`, `.agent/skills/quinotospec-mjolnir-refactor/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-mjolnir-refactor/SKILL.md`, `~/.cursor/skills/quinotospec-mjolnir-refactor/SKILL.md`, `~/.claude/skills/quinotospec-mjolnir-refactor/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
