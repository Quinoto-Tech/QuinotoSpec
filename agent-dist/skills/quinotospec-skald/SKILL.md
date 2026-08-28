---
name: quinotospec-skald
description: El Poeta de la Corte — docs viva sin duplicacion. Unifica onboard-* y sync README bilingue desde fuente unica.
---

# Skill: Quinotospec Skald — El Poeta de la Corte

> El Skald guarda las sagas para que no se pierdan. Una fuente, muchas voces.

## Problema que resuelve

- 5 skills `onboard-developer/product/support/general/simple` duplican 80% de logica — mantenimiento x5
- `README.md` (770 líneas) y `README_EN.md` (741) 95% duplicado sin sync — drift en cada bump
- `docs/ARCHITECTURE.md` repite conteos que Norns ya sincroniza

## Invocacion

```bash
/quinotospec-skald --role developer   # antes: onboard-developer
/quinotospec-skald --role product     # antes: onboard-product
/quinotospec-skald --role support
/quinotospec-skald --role general
/quinotospec-skald --role simple
/quinotospec-skald --sync-readme      # regenera README_EN desde README.md fuente
```

Roles validos: `developer | product | support | general | simple` — mapea a las 5 skills legacy (ahora wrappers delegan a Skald).

## Comportamiento

### 1. Onboard unificado

Skald lee `discovery/8 files + specs/ + schema.yaml` y genera `.quinoto-spec/onboard/<role>.md` con secciones:

| Rol | Foco |
|-----|------|
| developer | setup, arquitectura, endpoints, deuda, tests |
| product | vision, roadmap, DoR/DoD, metricas |
| support | endpoints observables, failure points, runbooks |
| general | balanceado |
| simple | lenguaje sin jerga, analogias |

Template unico `agent-dist/templates/skald-template.md` con bloques condicionales `{{#role=developer}}...{{/role}}` — no 5 templates.

Compatibilidad: las 5 skills legacy `quinotospec-onboard-*` ahora son shims que invocan `quinotospec-skald --role X` (1 linea).

### 2. README sync (fuente unica)

Fuente: `README.md` (ES) — `README_EN.md` se genera via:

```
README.md (fuente) --Skald--> README_EN.md (derivado)
```

Skald no traduce con LLM (evita alucinacion); solo sincroniza **estructura, tablas, conteos, badges, workflows list** y marca bloques `<!-- EN:needs-translation -->` donde el humano debe traducir. Norns ya sync badges, Skald sync tablas de workflows/skills/rules.

Uso:

```bash
bash agent-dist/skills/quinotospec-skald/sync-readme.sh --check   # solo reporta drift
bash agent-dist/skills/quinotospec-skald/sync-readme.sh           # aplica sync
```

## Estructura

```
agent-dist/skills/quinotospec-skald/
├── SKILL.md
├── sync-readme.sh
└── templates/
    └── skald-template.md  (futuro, hoy inline)
```

## Reglas

- Fuente unica: nunca editar `README_EN.md` directo — editar `README.md` y correr `--sync-readme`
- Legacy shims no se borran (compatibilidad) pero su SKILL.md debe decir "DEPRECATED: usa quinotospec-skald"
