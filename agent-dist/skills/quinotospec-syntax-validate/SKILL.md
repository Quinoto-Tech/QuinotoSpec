---
name: quinotospec-syntax-validate
description: Valida proposals, user stories, tasks y changelog mediante el contrato común, con compatibilidad legacy.
---

# Skill: Quinotospec Syntax Validate

Usa el contrato común antes de aplicar, archivar, distribuir o importar artefactos.

## Comando canónico

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
```

Para inspeccionar el modelo normalizado:

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json
```

## Qué valida

- Proposal: ID, prefijo, fecha, estado, prioridad, complejidad y servicios.
- User stories: tabla canónica, IDs `US-MNEM-suffix-NNN`, criterios, prioridad, estimación y servicio.
- Tasks: tabla canónica de 11 columnas, IDs `TSK-MNEM-suffix-NNN`, relación explícita con una story, dependencias y estado `[ ]`/`[x]`.
- Changelog: v2 preferred, v1 accepted, frontmatter/heading, resumen y `Tiempo Ahorrado`/`Time Saved`.
- Constitution: si existe, placeholders resueltos, estado explícito y principios verificables.
- Integridad: IDs duplicados, prefijos no registrados, stories huérfanas y tareas sin story.

## Compatibilidad

El parser acepta tablas antiguas, bloques `## US-...`/`## TSK-...`, `**Estado**: completada`, IDs cortos y `all_tasks.md` como índice derivado. Los formatos legacy generan warnings; no se reescriben automáticamente.

## Uso por tipo

```bash
/quinotospec-syntax-validate --type proposal --slug {{SLUG}}
/quinotospec-syntax-validate --type user-stories --slug {{SLUG}}
/quinotospec-syntax-validate --type tasks --slug {{SLUG}}
/quinotospec-syntax-validate --type changelog
/quinotospec-syntax-validate --type all --strict
```

## Flags

- `--type`: limita la revisión a `proposal`, `user-stories`, `tasks`, `changelog` o `all`.
- `--slug`: selecciona una propuesta concreta.
- `--strict`: falla también con warnings.
- `--json`: salida estable para CI.
- `--fix`: solo permite correcciones de estructura seguras; no migra legacy automáticamente.

## Integración

Esta skill es precondición de:

- `@quinotospec.apply`
- `@quinotospec.archive`
- `@quinotospec.distribute`
- `@quinotospec.create-tasks`

Un error bloquea el workflow. Un warning requiere confirmación explícita en modo estricto.

## Salida

```json
{
  "valid": true,
  "blocking": false,
  "errors": [],
  "warnings": []
}
```
