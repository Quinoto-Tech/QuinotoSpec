---
date: 2026-11-14
prefix: QSPE-a7f3
slug: fix-discovery-08-preservacion
format: v2
type: fix
---

## [2026-11-14] - Fix: discovery pisaba 08-product-and-agreements.md con datos vacios

### Resumen
- **Bug reportado por el usuario**: al correr discovery por segunda vez, `08-product-and-agreements.md` a veces se regeneraba como plantilla vacia, perdiendo el DoR/DoD completado por humanos
- **Causa raiz**: el workflow de discovery instruia generar los 8 archivos, y para el 8 ordenaba "plantilla vacia para ser completada por Humanos", pero sin ningun guard de preservacion. Quedaba a discrecion del modelo si leia y preservaba el contenido existente o escribia la plantilla fresca (comportamiento no determinista, por eso el "a veces")
- Descartadas otras causas: el check `no-overwrite` de `rules_enforce.py` solo protege `user-stories.md` y `*_tasks.md` (no discovery); `refresh-discovery` es inocente (actualiza solo secciones afectadas y su tabla de impacto no mapea nada al 08); el Product Agreement Check detecta el dano a posteriori pero no lo previene
- **Fix**: guard de preservacion (BLOQUEANTE) agregado en la seccion 8 de ambos espejos — `agent-dist/workflows/quinotospec.discovery.md` y `agent-dist/skills/quinotospec-discovery/SKILL.md`: si el archivo ya existe con contenido mas alla de placeholders, NO regenerar; regenerar solo si no existe; regeneracion explicita requiere backup en `.quinoto-spec/discovery/_archived/` y confirmacion
- Pendiente (opcional, requiere TDD): proteger el archivo 08 en el check `no-overwrite` de `rules_enforce.py` para enforcement programatico

**Verificacion**: `bash scripts/validate-all.sh --strict` — 30/30 suites pasando (49 workflows, 95 skills, 0 errores), governance gate passed, link checker 111/111, drift skill<->workflow 0

**Tiempo Ahorrado**: ~2h (IA: ~20min de diagnostico y fix vs Humano: ~2h de debug del comportamiento intermitente y recuperacion de DoR/DoD perdidos)
