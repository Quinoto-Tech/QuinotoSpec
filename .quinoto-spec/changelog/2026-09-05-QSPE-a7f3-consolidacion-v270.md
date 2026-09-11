---
date: 2026-09-05
prefix: QSPE-a7f3
slug: consolidacion-v270
type: maintenance
---

## [2026-09-05] - Consolidación v2.7.0 — sync de versión, docs y dogfooding

### Resumen
- Release 2.7.0 formalizado: `update-version.sh 2.7.0` sincronizó install.sh, manifest.json, .version, badges de README ES/EN, ARCHITECTURE.md, V3_ROADMAP.md y validate-all.sh
- CHANGELOG: entrada real de 2.7.0 (7 skills nórdicas), backfill de 2.1.0 Berserker, fix "69→76 skills", sección "Versiones Futuras" reemplazada por referencia única a V3_ROADMAP.md
- V3_ROADMAP unificado: criterios de aceptación corregidos (Fase 1/4 sin implementar), header desde v2.7.0, reglas renumeradas #14–#17, métricas actualizadas a baseline 2.7.0
- AGENTS.md: agregados workflows nórdicos + Heimdallr/Battle Frenzy/Blood-Bond/Mjolnir y tabla Skills Nórdicas
- README ES/EN: drift de comandos corregido, un solo "Actual" (v2.7.0), plan divergente Falange/Hird reemplazado por referencia a V3_ROADMAP
- manifest.json: features nórdicas (norns, huginn_muninn, skald, jormungandr, valkyrie, bifrost, mimir), edition "Warband: Nórdicas", python3 3.8 en min_requirements
- MIGRATION-GUIDE: nombre de skill corregido (`quinotospec-generate-github-branch`)
- Dogfooding inicializado: estructura `.quinoto-spec/` + prefix-registry + changelog v2
- Assets: PNGs movidos a docs/assets/, PDFs des-trackeados del repo
- Tests: agregados test-install-e2e.sh (round-trip sandbox) y test-checkers.sh (Jormungandr, Huginn-Muninn, update-version dry-run)
- CI: matrix ubuntu+macos, shellcheck, release valida tag vs .version/manifest, hooks instalados
- install.sh: flag --yes (no-interactivo) y uninstall seguro con verificación de marcadores

**Tiempo Ahorrado**: ~6h (IA: ~40min vs Humano: ~6h de sync manual cross-doc)
