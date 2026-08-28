---
name: quinotospec-huginn-muninn
description: Los Cuervos de Odin — observabilidad continua de entropia y drift. Cron Tiwaz + contract drift alerting sin intervencion manual.
---

# Skill: Quinotospec Huginn & Muninn — Los Cuervos de Odin

> Huginn (Pensamiento) y Muninn (Memoria) vuelan cada amanecer y reportan a Odin. Estos cuervos vuelan por tu codebase.

## Cuando usar

- Cada PR y cada noche (cron) para detectar degradacion de entropia
- Como gate pre-merge: bloquea si `S_final >= 0.76` (critico) o delta `+0.10` vs baseline
- Para generar `tiwaz-rune/INDEX.md` historico sin correr Tiwaz manual

## Invocacion

```bash
/quinotospec-huginn-muninn --pr          # en PR: compara baseline vs head
/quinotospec-huginn-muninn --cron        # en cron: historico diario
/quinotospec-huginn-muninn --service ./services/payments --json
```

## Comportamiento

### 1. Huginn — Pensamiento (artefacto actual)

- Ejecuta `quinotospec-tiwaz-rune --json` (formal + proxy) y `quinotospec-dependency-graph`
- Calcula `S_final = 0.60*H_total + 0.40*S_proxy` y clasifica (0.00-0.20 sano / 0.76+ critico)
- Guarda `.quinoto-spec/tiwaz-rune/YYYYMMDD-hhmm-entropy.json` + `.md`

### 2. Muninn — Memoria (baseline y tendencia)

- Lee ultimo `tiwaz-rune/*.json` como baseline
- Calcula delta `ΔS = S_head - S_base` y tendencia 7/30 dias
- Actualiza `tiwaz-rune/INDEX.md` (tabla fecha, S_final, H_total, S_proxy, top hallazgo)

### 3. Alerta

| Condicion | Severidad | Accion |
|-----------|-----------|--------|
| `S_final >= 0.76` | BLOCKING | Falla CI, sugiere `mjolnir-refactor` |
| `ΔS >= +0.10` | WARNING | Comenta PR con drill-down por dimension |
| `S_final 0.51-0.75` | WARNING | Reporte sin bloqueo |

Formato comentario PR:

```
🪶 Huginn & Muninn — Entropia PR #123
- S_final: 0.62 (+0.08 vs baseline 0.54) — alta
- Top driver: H_grafo +0.12 (nuevo ciclo auth→payments)
- Plan: ver tiwaz-rune/20260828-1200-entropy-report.md
```

## CI Integration

Workflow `.github/workflows/huginn-muninn.yml` (generado por skill si no existe):

```yaml
on: [pull_request, push, schedule: cron: 0 6 * * *]
jobs:
  entropy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/validate-all.sh --internal-only
      - run: bash agent-dist/skills/quinotospec-huginn-muninn/check.sh --json
```

`check.sh` es wrapper bash que invoca `quinotospec-entropy-calculator` sin LLM, solo formulas.

## Reglas

- No bloquea por `0.21-0.50` (mejorable) — solo informa
- Solo 1 INDEX.md, append-only, gitignored? No — versionado para tendencia (como `tiwaz-rune/`)
- Usa `INTERNAL_ONLY` en `validate-all.sh` para evitar curl flaky en CI
