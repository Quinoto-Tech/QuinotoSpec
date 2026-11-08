---
name: quinotospec-extension-install
description: Instala una extensión local o de catálogo con validación de manifest, staging y registro auditable.
---

# Skill: Quinotospec Extension Install

> Instala una extensión sin modificar el core y sin ejecutar hooks automáticamente.

> **Fuente de verdad de ejecución:** `agent-dist/workflows/quinotospec.extension-install.md`. Esta skill expone la capacidad instaladora; cualquier divergencia se resuelve sincronizando este archivo con el workflow.

## Cuando usar

- Cuando un proyecto necesita capacidades opcionales (checkers, hooks, skills extra) sin modificar el core del paquete
- Reinstallación explícita con `--replace` (preferir `@quinotospec.extension-update`)

## Parámetros

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `SOURCE` | Sí | Path local o `catalog:<id>` |
| `CATALOG` | No | Catálogo cuando `SOURCE` usa `catalog:` |
| `REPLACE` | No | Solo para reinstallación explícita |

## Pasos de Ejecución

1. Verificar que `SOURCE` sea un directorio local sin symlinks.
2. Validar `extension.yml`: schema, ID, versión, `provides`, requisitos y hooks.
3. Ejecutar:

```bash
python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . install --kind extension --source {{SOURCE}} --catalog {{CATALOG}}
```

4. Verificar `.quinoto-spec/extensions/.registry` y la capa winner con `template_resolver.py`.
5. Presentar comandos, skills, templates y hooks instalados; no ejecutar hooks `auto` sin confirmación explícita.
6. Si el proyecto tiene `config.yaml`, añadir la extensión a `extensions.active` solo con confirmación.
7. Registrar el cambio con `quinotospec-update-changelog`.

## Manejo de Errores

- Manifest ausente, inválido, con path inseguro o symlink: detener sin modificar el destino.
- Source remoto: detener; esta versión solo instala paths locales verificables.
- ID ya instalado: usar update o `--replace` explícito.
