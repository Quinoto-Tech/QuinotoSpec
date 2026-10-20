---
date: 2026-10-20
prefix: QSPE-a7f3
slug: improvements-backlog-executed
format: v2
type: feat
---

## [2026-10-20] - Implementación completa del backlog de mejoras (M1–M8)

### Resumen
- Paquete 1: versión `3.3.0` sincronizada en README/README_EN/CHANGELOG/ARCHITECTURE/roadmap/installer, colisión `F3.3` resuelta (`F3.5` para `quinotospec-help`) y `Jormungandr` ejecuta Kahn real sobre `requires:` multilínea e inline.
- Paquete 2: `AGENTS.md` global instalado dentro del directorio de cada IDE (`~/.config/opencode/AGENTS.md`, `~/.cursor/AGENTS.md`, etc.) y plugin OpenCode v2 idempotente, con null-safety y caché por `root`.
- Paquete 3: `run-all-tests.sh` detecta suites huérfanas, `validate-all.sh --allow-no-node` desacopla Node de `--strict`, fixtures conectadas, lock atómico de instalación, `external_config` validado y contrato JSON transversal.
- Paquete 4: `Huginn & Muninn` calcula entropía real, `Norns` detecta drift (`--check`/`--dry-run`/`--to`), `Skald` sincroniza badges y valida paridad; se añadieron `quinotospec-help` (F3.5), `quinotospec-complexity-router` + `/quinotospec.quick-dev` (F4.2) y la configuración 3-layer de agentes (F3.1).
- Inventario sincronizado en 46 workflows y 89 skills; `validate-all.sh --strict` y las 21 suites de `run-all-tests.sh` pasan sin errores.

**Tiempo Ahorrado**: ~24h (IA: ~2h vs Humano: ~24h)
