---
name: quinotospec-preset-install
description: Instala un preset local o de catálogo con prioridad explícita y resolución de templates.
---

# Skill: Quinotospec Preset Install

> Instala un preset bajo `.quinoto-spec/presets/<id>/` y valida que sus templates respeten la pila de resolución.

> **Fuente de verdad de ejecución:** `agent-dist/workflows/quinotospec.preset-install.md`. Esta skill expone la capacidad instaladora de presets; cualquier divergencia se resuelve sincronizando este archivo con el workflow.

## Cuando usar

- Cuando un proyecto quiere adoptar un paquete de templates/convenciones preconfigurado para un dominio (ej. presets de stack)
- Después de instalar una extensión, para activar sus templates con la prioridad correcta

## Parámetros

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `SOURCE` | Sí | Path local o `catalog:<id>` |
| `CATALOG` | No | Catálogo cuando `SOURCE` usa `catalog:` |

## Pasos de Ejecución

1. Validar `preset.yml`: ID, versión, prioridad y paths.
2. Ejecutar:

```bash
python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . install --kind preset --source {{SOURCE}} --catalog {{CATALOG}}
```

3. Verificar el registro y usar `template_resolver.py` para comprobar qué capa gana para cada template.
4. Si existen overrides del proyecto, no sobrescribirlos; el preset queda por debajo de overrides.
5. Registrar el cambio con `quinotospec-update-changelog`.

## Manejo de Errores

- Prioridad inválida, manifest inseguro o symlink: detener.
- Conflicto de ID: usar update o confirmar `--replace`.
- No ejecutar hooks automáticamente durante la instalación.

## Orden de resolución

Orden de prioridad de las capas: `overrides -> presets -> extensions -> core`. El preset nunca gana frente a overrides del proyecto.
