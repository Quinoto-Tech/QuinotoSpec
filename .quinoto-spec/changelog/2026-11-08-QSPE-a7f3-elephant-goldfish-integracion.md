---
date: 2026-11-08
prefix: QSPE-a7f3
slug: elephant-goldfish-integracion
type: feature
---

## [2026-11-08] - Integrar práctica Elephant-Goldfish en el flujo actual

### Resumen
- `review` (workflow + skill): flag opcional `--goldfish [lentes]` (desactivado por defecto, igual que `--party`) que activa el paso `2b` de **Goldfish review** con subagentes aislados (Comprehension, Design Critic, Zoom Out, Implementation Readiness) y escribe `.quinoto-spec/reviews/{{TASK_ID}}-goldfish.md`; si no hay contexto fresco, detiene solo la capa Goldfish.
- `create-proposal` (workflow + skill): flag opcional `--goldfish` para el **Shootdown multi-lente** (simplicidad/YAGNI, reuso, escalabilidad, fallos, seguridad, coste, reversibilidad) que produce `concepts_brief.md` y veredicto GO/PIVOT/KILL; sin el flag no se ejecuta.
- `apply` (workflow + skill): paso `4c` y **Readiness Gate** (archivos, comando de test, criterios verificables) antes de codificar.
- `health`: nuevo **Paso 5b Drift docs↔código** con severidad INFO/WARN/BLOCKING y `drift-report.md/.json`.
- Sin skills/workflows nuevos: la práctica se suma al flujo existente (49 workflows / 95 skills sin cambios de inventario).

**Tiempo Ahorrado**: ~3h (IA: ~25min vs Humano: ~3h)
