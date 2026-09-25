---
name: quinotospec-extension-manager
description: Gestiona extensiones y presets locales con manifest versionado, registro auditable, instalación transaccional y hooks explícitos.
---

# Extension Manager

Gestiona el ciclo de vida de extensiones y presets sin ejecutar código remoto ni resolver conflictos silenciosamente.

## Modelo

- Extensiones: `.quinoto-spec/extensions/<id>/extension.yml`.
- Presets: `.quinoto-spec/presets/<id>/preset.yml`.
- Registro auditable: `.quinoto-spec/extensions/.registry`.
- Catálogos locales: `extensions/catalog.json` y `extensions/catalog.community.json`.
- Resolución de templates: `quinotospec-template-resolver` aplica overrides → presets → extensions → core.

## Comandos

```bash
python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . --json search jira

python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . install --kind extension --source ./my-extension

python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . update --kind extension --source ./my-extension

python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . --json list

python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . info --kind extension my-extension

python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . remove --kind extension my-extension --yes
```

`install` y `update` validan el manifest antes de copiar, rechazan symlinks y escriben el registro atómicamente. `remove` exige `--yes` y solo elimina paths registrados.

## Hooks

Los hooks se declaran en `extension.yml` bajo los 17 puntos del contrato. Listarlos es read-only:

```bash
python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . --json hooks --point before_apply
```

Ejecutar hooks automáticos requiere `--run --yes`; los hooks manuales solo se reportan. Los comandos se ejecutan sin `shell`, con timeout y código de salida visible.

## Seguridad

- No instalar fuentes HTTP por defecto; el catálogo debe entregar un path local verificable.
- No modificar el core para registrar una extensión.
- No ejecutar hooks `auto` durante `install` o `update`; hacerlo requiere una invocación explícita.
- Rechazar IDs, paths, manifests y archivos fuente inseguros.
- Registrar el cambio con `quinotospec-update-changelog` después de instalar, actualizar o remover.

## Integración

- `@quinotospec.extension-install` instala una extensión local o de catálogo.
- `@quinotospec.preset-install` instala un preset local o de catálogo.
- Los workflows core consultan `hooks` en sus puntos before/after y solo ejecutan hooks automáticos con confirmación.
- `@quinotospec.update-agents` incluye extensiones activas en el `AGENTS.md` generado.
