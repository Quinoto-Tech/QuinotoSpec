---
name: quinotospec-preset-install
description: Instala un preset local o de catálogo con prioridad explícita y resolución de templates.
---

> **Fuente de verdad:** esta skill contiene el prompt canónico; el comando `/quinotospec.preset-install` delega aquí por archivo.

# Skill: Preset Install

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
