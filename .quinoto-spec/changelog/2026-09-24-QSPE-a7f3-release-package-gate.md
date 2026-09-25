---
date: 2026-09-24
prefix: QSPE-a7f3
slug: release-package-gate
format: v2
type: change
---

## [2026-09-24] - Release package gate

### Resumen
- `scripts/package-release.sh` genera el tarball sin `__pycache__`/`.pyc` y escribe un checksum SHA-256 verificable.
- `scripts/smoke-release.sh` extrae el artefacto, instala en un target separado, verifica ownership, ejecuta `--verify` y uninstall.
- CI cubre Python 3.8/3.11 y ejecuta el smoke test; release publica tarball y checksum.

**Tiempo Ahorrado**: ~2h (IA: ~20min vs Humano: ~2h)
