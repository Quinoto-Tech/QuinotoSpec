---
date: 2026-09-24
prefix: QSPE-a7f3
slug: f2-4-dynamic-agents
format: v2
type: change
---

## [2026-09-24] - F2.4: AGENTS dinámico

### Resumen
- Se añadió `config.yaml` como fuente de configuración del proyecto.
- Se creó `AGENTS-template.md` y `update_agents.py` para generar AGENTS.md atómicamente desde config, inventario y extensiones.
- `init` crea la configuración y el installer genera AGENTS.md durante staging con ownership/rollback.

**Tiempo Ahorrado**: ~3h (IA: ~30min vs Humano: ~3h)
