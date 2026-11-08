---
date: 2026-11-08
prefix: QSPE-a7f3
slug: sprint2-gates-huginn-ui
type: feature
---

## [2026-11-08] - Sprint 2: gates ejecutables + Huginn histórico + UI specs/evidence/gates

### Resumen
- Gates: `tdd_validate.py` (delega en `evidence_validate.py`) y `constitution_validate.py` en `quinotospec-rules-enforce/` + wrappers en `quinotospec-tdd/` y `quinotospec-constitution/`; fix regex principios (`**CODE-01:**`).
- Huginn: `check.py --history [--trend]` persiste `.quinoto-spec/metrics/entropy-history.jsonl` con `delta_vs_prev`, tendencia 7/30d.
- UI: `/specs`, `/specs/<domain>`, `/evidence`, `/gates` (readers `read_specs/read_spec_file/read_evidence_all/read_gates` + templates + rutas), NAV actualizada.

**Tiempo Ahorrado**: ~6h (IA: ~45min vs Humano: ~6h)
