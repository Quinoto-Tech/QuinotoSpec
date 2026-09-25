---
date: 2026-09-25
prefix: QSPE-a7f3
slug: installer-version-manifest-fix
format: v2
type: bugfix
---

## [2026-09-25] - Fix: la versión instalada ahora es consultable

### Resumen
- `install.sh` escribía `installer_version` hardcodeado como `3.1.0` en `.quinoto-spec/ownership.json`; `update-version.sh` nunca actualizaba ese literal, así que toda instalación reportaba una versión falsa.
- `write_ownership_manifest` ahora recibe `INSTALLER_VERSION` y lo persiste correctamente.
- `--version` (con flag de IDE) muestra además la versión instalada, el IDE y `installed_at`; `--verify` imprime la versión instalada.
- Regresión cubierta en `tests/test-install-e2e.sh`: el manifiesto coincide con `INSTALLER_VERSION` y `--version` reporta la versión instalada.

**Tiempo Ahorrado**: ~45min (IA: ~12min vs Humano: ~45min)
