---
description: Crear, verificar y restaurar backups verificables de .quinoto-spec con SHA-256, staging y rollback seguro.
---

# Command: backup

Lee la skill `quinotospec-backup` (archivo `SKILL.md`) y ejecuta su contenido como instrucciones, pasando `$ARGUMENTS` como contexto.

Resuelve la ruta en este orden: `agent-dist/skills/quinotospec-backup/SKILL.md` (repo fuente), `.opencode/skills/quinotospec-backup/SKILL.md`, `.cursor/skills/quinotospec-backup/SKILL.md`, `.claude/skills/quinotospec-backup/SKILL.md`, `.agent/skills/quinotospec-backup/SKILL.md` (instalación local), `~/.config/opencode/skills/quinotospec-backup/SKILL.md`, `~/.cursor/skills/quinotospec-backup/SKILL.md`, `~/.claude/skills/quinotospec-backup/SKILL.md` (global).
Si no existe, detén y reporta las rutas intentadas. No resumas ni reescribas la skill: aplícala textualmente.
