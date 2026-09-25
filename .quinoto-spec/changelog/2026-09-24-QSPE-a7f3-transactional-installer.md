---
date: 2026-09-24
prefix: QSPE-a7f3
slug: transactional-installer
format: v2
type: change
---

## [2026-09-24] - Installer transaccional

### Resumen
- `install.sh` trabaja sobre un staging sibling y solo reemplaza el destino después de verificar la instalación candidata.
- `.quinoto-spec/ownership.json` registra hashes de archivos gestionados, `AGENTS.md` y comandos de hooks para actualización y uninstall seguros.
- Un `EXIT trap` restaura la configuración y `AGENTS.md` si falla el commit; el uninstall conserva archivos ajenos y rechaza destinos legacy sin manifest.
- La suite E2E cubre manifest, rollback inyectado, conflictos por modificación local y preservación de configuración.

**Tiempo Ahorrado**: ~5h (IA: ~45min vs Humano: ~5h)
