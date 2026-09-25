---
date: 2026-09-24
prefix: QSPE-a7f3
slug: g0-2c-human-approval
format: v2
type: change
---

## [2026-09-24] - G0.2c: Aprobación Humana Estructurada

### Resumen
- Se añadió `approval_validate.py` para validar registros JSON de decisiones humanas `approved`, `rejected` y `deferred`.
- El gate exige coincidencia exacta de `subject` y `action`, frescura, responsable, alcance y justificación; no demuestra identidad ni ejecuta comandos.
- El dispatcher ahora incluye `human-approval`, puede satisfacer la protección de configuración crítica y mantiene el flag legacy sin sustituir el registro estructurado.
- Constitution, Mjolnir y Apply documentan cómo registrar y validar decisiones humanas explícitas.

**Tiempo Ahorrado**: ~4h (IA: ~30min vs Humano: ~4h)
