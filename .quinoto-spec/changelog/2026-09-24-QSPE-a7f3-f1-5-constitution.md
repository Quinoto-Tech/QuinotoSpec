---
date: 2026-09-24
prefix: QSPE-a7f3
slug: f1-5-constitution
format: v2
type: change
---

## [2026-09-24] - F1.5: Constitution del proyecto

### Resumen
- Se creó `quinotospec.constitution` y su skill wrapper para generar borradores, validar placeholders y activar principios solo con aprobación explícita.
- Se reforzó `constitution-template.md` con IDs de principios, gates verificables y límites de precedencia.
- Apply, Review y Archive consultan una constitución activa; el schema marca el compliance de archivo como bloqueante.
- Se añadió la regla #17 Constitutional Compliance y se sincronizaron conteos, manifest, documentación, installer y versionado.
- La constitución permanece opcional para compatibilidad; el enforcement sigue siendo prompt-only.

**Tiempo Ahorrado**: ~3h (IA: ~30min vs Humano: ~3h)
