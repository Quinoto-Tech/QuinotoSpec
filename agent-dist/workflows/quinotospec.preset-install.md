---
name: quinotospec.preset-install
description: Instala un preset local o de catálogo con prioridad explícita y resolución de templates.
---

# Workflow: Preset Install

Instala un preset bajo `.quinoto-spec/presets/<id>/` y valida que sus templates respeten la pila de resolución.

## Pasos

1. Valida `preset.yml`, ID, versión, prioridad y paths.
2. Ejecuta:

```bash
python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . install --kind preset --source {{SOURCE}} --catalog {{CATALOG}}
```

3. Verifica el registro y usa `template_resolver.py` para comprobar qué capa gana para cada template.
4. Si existen overrides del proyecto, no los sobrescribas; el preset queda por debajo de overrides.
5. Registra el cambio con `quinotospec-update-changelog`.

## Errores

- Prioridad inválida, manifest inseguro o symlink: detener.
- Conflicto de ID: usar update o confirmar `--replace`.
- No ejecutes hooks automáticamente durante la instalación.
