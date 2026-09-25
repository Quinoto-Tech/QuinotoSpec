---
name: quinotospec.extension-install
description: Instala una extensión local o de catálogo con validación de manifest, staging y registro auditable.
---

# Workflow: Extension Install

Instala una extensión sin modificar el core y sin ejecutar hooks automáticamente.

## Parámetros

- `SOURCE`: path local o `catalog:<id>`.
- `CATALOG`: catálogo opcional cuando `SOURCE` usa `catalog:`.
- `REPLACE`: solo para una reinstallación explícita; preferí `@quinotospec.extension-update`.

## Pasos

1. Verifica que `SOURCE` sea un directorio local sin symlinks.
2. Valida `extension.yml`: schema, ID, versión, `provides`, requisitos y hooks.
3. Ejecuta:

```bash
python3 agent-dist/skills/quinotospec-extension-manager/extension_manager.py \
  --root . install --kind extension --source {{SOURCE}} --catalog {{CATALOG}}
```

4. Verifica `.quinoto-spec/extensions/.registry` y la capa winner con `template_resolver.py`.
5. Presenta comandos, skills, templates y hooks instalados; no ejecutes `auto` hooks sin confirmación explícita.
6. Si el proyecto tiene `config.yaml`, añade la extensión a `extensions.active` solo con confirmación.
7. Registra el cambio con `quinotospec-update-changelog`.

## Errores

- Manifest ausente, inválido, con path inseguro o symlink: detener sin modificar el destino.
- Source remoto: detener; esta versión solo instala paths locales verificables.
- ID ya instalado: usar update o `--replace` explícito.
