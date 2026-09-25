---
date: 2026-09-24
prefix: QSPE-a7f3
slug: f1-2-ingenieria
format: v2
type: change
---

## [2026-09-24] - F1.2–F1.4: disciplina de ingeniería

### Resumen
- Se añadieron `quinotospec-tdd`, `quinotospec-debug` y `quinotospec-verify-before-done` con sus referencias operativas y ejemplos.
- Apply ahora exige RED antes de producción, debugging ante fallos y verificación fresca antes de continuar.
- Mark Done ejecuta el gate de verificación antes de cambiar estados; `--force` ya no elimina la evidencia requerida.
- Se incorporaron las reglas #14–#16 y se sincronizaron manifest, conteos, documentación, CI y suite de instalación.
- Los gates son prompt-level: el enforcement global ejecutable queda como trabajo posterior.

**Tiempo Ahorrado**: ~5h (IA: ~45min vs Humano: ~5h)
