---
date: 2026-11-18
prefix: SKDP-m2q8
slug: proposal-command-to-skill-delegation
format: v2
type: change
---

## [2026-11-18] - Proposal Generated: Command-to-Skill Delegation

### Resumen
- Se generó la propuesta 'Command-to-Skill Delegation' en `.quinoto-spec/proposals/2026-11-18-command-to-skill-delegation/` con delta-specs para `command-layer`, `skill-layer` y `drift-checker`.
- Evidencia del problema: 49/49 workflows tienen skill pareada; 39 pares con similitud ≥0.7; pares `init`/`agent-train`/`tiwaz-rune`/`onboard`/`party-mode` con similitud 1.00; 10 pares resumidos (flow 0.18 … extension-install 0.52) que requieren consolidación antes de delegar.
- Solución propuesta: comandos como stubs de delegación por archivo (sin tool `@skill-id`, decisión del usuario), skill como fuente única del prompt, `$ARGUMENTS` preservado, generador `scripts/generate-command-stubs.py`, checker de drift invertido y documentación actualizada.
- Conflictos documentados: PWRE-9f2c (En Curso) toca `review-workflow` — conversión del par `review` al final o exclusión temporal; DoR/DoD vacío (F-05) con override de sesión documentado.
- Prefijo `SKDP-m2q8` registrado; contrato validado con `contract.py validate --root . --strict` (0 errores, 0 warnings); sin caracteres CJK (check de CI).

**Tiempo Ahorrado**: ~5h (IA: ~10min vs Humano: ~5h)
