---
name: quinotospec-valkyrie
description: La Electora de los Caidos — triage inteligente de propuestas. Elige que vive, que muere y que va a Valhalla (archive).
---

# Skill: Quinotospec Valkyrie — La Electora de los Caidos

> Valkyrie elige en el campo de batalla. Esta skill elige en tu backlog.

## Cuando usar

- `quinotospec.status` muestra 3+ propuestas activas y no sabes cual priorizar
- `conflict-detector` reporta solapamiento — Valkyrie decide orden de merge
- Como input a `sprint.plan` para ranking

## Invocacion

```bash
/quinotospec-valkyrie                          # rankea propuestas activas
/quinotospec-valkyrie --suggest-next           # integra suggest-next global
/quinotospec-valkyrie --json                   # output machine-readable
```

## Comportamiento

### Scoring (0-100)

```
score = 0.30*impact + 0.25*urgency + 0.20*risk_inverse + 0.15*debt_relief + 0.10*deps_ready
```

- **impact**: # servicios afectados + # US P1 (de user-stories.md)
- **urgency**: antiguedad + label `priority: P1` en proposal.md
- **risk_inverse**: `1 - DREAD_avg/10` (de Heimdallr si existe, sinon 0.5)
- **debt_relief**: si proposal toca `07-findings` o `tiwaz-rune` hallazgo → +20
- **deps_ready**: `artifact-engine` status `ready` vs `blocked` (DAG)

### Output

Tabla rankeada:

```
# | Propuesta | Score | Impact | ΔS | Conflictos | Next Action
1 | 2026-08-28-auth-jwt (AUTH-a1b2) | 84 | 3 svcs | +0.02 | none | ready → sprint.plan
2 | 2026-08-20-pay-v2 (PAY-c3d4)   | 62 | 2 svcs | +0.08 | solapa PAY-a9 | blocked (needs delta-specs)
3 | 2026-07-01-legacy (LEG-x1)     | 31 | 1 svc  | -    | stale 60d | candidate archive
```

- `Next Action` mapeado: `ready` → `suggest-next`, `blocked` → que falta, `stale` (>60d sin update) → `archive` candidato, `conflict` → `conflict-detector` detail

### Integracion

- Lee `proposals/*/proposal.md` frontmatter + `user-stories.md` + `tiwaz-rune/*.json` + `conflict-detector` output
- No requiere LLM — solo parsing + formula
- `status.md` puede invocar Valkyrie como seccion "Prioridad Valhalla"

## Reglas

- Nunca auto-archiva — solo sugiere con `candidate archive` y requiere confirmacion
- Si hay ciclo Jormungandr, score deps_ready = 0 y alerta BLOCKING
