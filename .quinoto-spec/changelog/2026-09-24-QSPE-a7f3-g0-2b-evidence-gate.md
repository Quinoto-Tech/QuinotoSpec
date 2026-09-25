---
date: 2026-09-24
prefix: QSPE-a7f3
slug: g0-2b-evidence-gate
format: v2
type: change
---

## [2026-09-24] - G0.2b: Evidencia TDD/Debug/Verify

### Resumen
- Se añadió `evidence_validate.py` para validar registros JSON frescos, tipados y con exit codes de TDD, Debug y Verify-Before-Done.
- El dispatcher acepta `--require-evidence`, `--task-id` y `--evidence-dir`; no convierte evidencia ausente en `pass`.
- Apply documenta cómo crear y validar evidencia antes de GREEN/hotfix y antes de Mark Done.
- Las decisiones humanas y la ejecución real de comandos permanecen fuera del validador y se reportan como diferidas.

**Tiempo Ahorrado**: ~4h (IA: ~30min vs Humano: ~4h)
