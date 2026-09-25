---
description: Crear, verificar y restaurar backups verificables de .quinoto-spec con SHA-256, staging y rollback seguro.
---

# Workflow: Backup

Usa el motor ejecutable `backup.py` para proteger `.quinoto-spec/` antes de refactors, migraciones y operaciones destructivas.

## Propiedades garantizadas

- El store por defecto es `.quinoto-spec-backups/`, fuera de `.quinoto-spec/`.
- Cada backup usa `manifest.json` y `payload/` con SHA-256 por archivo.
- Se excluyen `backups/`, `mimir/`, caches, `.git/`, secretos y symlinks.
- La creación usa staging y rename atómico; no copia el store dentro del source.
- `verify` comprueba tamaño, hash, rutas, conteos y archivos extra.
- `restore` exige `--yes`, crea un backup de seguridad y cambia el destino mediante rename reversible.
- `cleanup` es dry-run por defecto y exige `--yes` para borrar.

## Comandos

```bash
python3 -B agent-dist/skills/quinotospec-backup/backup.py create --root . --type full --json
python3 -B agent-dist/skills/quinotospec-backup/backup.py create --root . --type incremental --json
python3 -B agent-dist/skills/quinotospec-backup/backup.py list --root . --json
python3 -B agent-dist/skills/quinotospec-backup/backup.py verify --root . --backup BACKUP_ID --json
python3 -B agent-dist/skills/quinotospec-backup/backup.py restore --root . --backup BACKUP_ID --yes --json
python3 -B agent-dist/skills/quinotospec-backup/backup.py cleanup --root . --keep 5 --dry-run --json
```

Usa `--store RUTA` para un store externo explícito. El store nunca puede estar dentro de `.quinoto-spec/`.

## Tipos

- `full`: snapshot completo de `.quinoto-spec/`.
- `incremental`: archivos nuevos/modificados y lista de eliminados respecto al último backup.
- `proposals`: solo `proposals/`.
- `discovery`: solo `discovery/`.

Un restore parcial o incremental prepara una copia de trabajo externa y solo aplica el scope indicado.

## Confirmación y errores

- Un restore sin `--yes` termina con error y no modifica el proyecto.
- Un hash, tamaño, manifest o payload inválido termina con error de verificación.
- Un symlink, secreto, path inseguro o store inválido termina con error operativo.
- No uses `rm -rf` ni borres backups manualmente; usa `cleanup` con confirmación.

Después de una operación exitosa, ejecuta `quinotospec-update-changelog` con el tipo, ID, cantidad de archivos y tamaño verificado.
