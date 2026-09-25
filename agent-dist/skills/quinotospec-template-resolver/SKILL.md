---
name: quinotospec-template-resolver
description: Resuelve templates, commands y skills mediante overrides, presets, extensions y core en orden de prioridad.
---

# Template Resolver

Resuelve un nombre contra cuatro capas y devuelve el primer candidato regular encontrado:

1. `.quinoto-spec/overrides/`
2. `.quinoto-spec/presets/` ordenados por prioridad ascendente
3. `.quinoto-spec/extensions/` ordenados por prioridad ascendente
4. `agent-dist/` del core

## Uso

```bash
python3 agent-dist/skills/quinotospec-template-resolver/template_resolver.py \
  --root . --kind template --name proposal-template.md --json

python3 agent-dist/skills/quinotospec-template-resolver/template_resolver.py \
  --root . --kind command --name quinotospec.apply.md

python3 agent-dist/skills/quinotospec-template-resolver/template_resolver.py \
  --root . --kind skill --name quinotospec-tdd --json
```

## Contrato

- `template` busca `templates/`.
- `command` busca `commands/` y `workflows/`.
- `skill` busca `skills/<name>/SKILL.md` y `skills/<name>.md`.
- Los presets y extensiones se ordenan por `priority`; un número menor tiene mayor prioridad.
- Los candidatos symlink se rechazan.
- La salida indica `layer`, `path` y todos los candidatos revisados.
- El resolver es read-only y no carga código de una extensión.

## Integración

Los consumidores deben usar el resolver en lugar de abrir directamente `agent-dist/templates/`. Una extensión puede añadir un template sin modificar el core; un override de proyecto sigue teniendo la mayor prioridad.
