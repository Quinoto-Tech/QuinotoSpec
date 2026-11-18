---
date: 2026-11-17
prefix: VPAT-k4m7
slug: proposal-validator-path-resolution
format: v2
type: change
---

## [2026-11-17] - Proposal Generated: Validator Path Resolution

### Resumen
- Se generó la propuesta 'Validator Path Resolution' en `.quinoto-spec/proposals/2026-11-17-validator-path-resolution/` con delta-specs para `installer`, `payload-python` y `payload-documentacion`.
- Origen: bug reportado — tras instalar global, los validadores referenciados como `agent-dist/skills/...` no se encuentran porque el instalador copia el contenido de `agent-dist/` al config dir y 108 docs del payload mantienen rutas relativas del repo fuente.
- Solución propuesta: rewrite `agent-dist/` → raíz de instalación en `.md` staged (post-staging, pre-manifest) + fallback `resolve_package_root()` en `update_agents.py` y `template_resolver.py` + suite de regresión `tests/test-installed-paths.sh`.
- Gate de producto (DoR/DoD) superado como excepción documentada por override explícito del usuario (F-05); pendiente aprobación humana formal previa a Apply.
- Prefijo `VPAT-k4m7` registrado en `prefix-registry.md`; contrato validado con `contract.py validate --root . --strict` (0 errores, 0 warnings).

**Tiempo Ahorrado**: ~4h (IA: ~10min vs Humano: ~4h)
