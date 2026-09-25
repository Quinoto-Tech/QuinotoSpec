---
date: 2026-09-24
prefix: QSPE-a7f3
slug: f2-3-extensions-presets
format: v2
type: change
---

## [2026-09-24] - F2.3: Extensiones y presets

### Resumen
- Se añadió `extension_manager.py` para search/install/update/remove/list/info y ejecución explícita de hooks.
- Se añadió `template_resolver.py` con resolución overrides → presets → extensions → core.
- Se añadieron manifests, workflows, catálogos locales y guía de desarrollo.
- Las extensiones se validan sin symlinks, se registran en `.quinoto-spec/extensions/.registry` y no ejecutan hooks durante install/update.

**Tiempo Ahorrado**: ~4h (IA: ~35min vs Humano: ~4h)
