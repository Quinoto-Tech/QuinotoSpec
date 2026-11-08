---
date: 2026-11-08
prefix: QSPE-a7f3
slug: ui-multi-proyecto
type: feature
---

## [2026-11-08] - UI: panel central multi-proyecto (Bifrost)

### Resumen
- Agregado soporte multi-root a la UI via `--roots "r1,r2"` (mantiene `--root` para compatibilidad)
- `readers.build_multi_summary` agrega propuestas, tareas, changelog y conteos de N proyectos
- Selector de proyecto en el header (filtra vistas por `?project=`) y nueva página `/projects`
- Columna "Proyecto" en dashboard/propuestas/tareas/changelog cuando se muestran todos los proyectos
- Tests existentes (`tests/test-ui.sh`) siguen pasando (single-root sin cambios)

**Tiempo Ahorrado**: ~2h (IA: ~25min vs Humano: ~2h)