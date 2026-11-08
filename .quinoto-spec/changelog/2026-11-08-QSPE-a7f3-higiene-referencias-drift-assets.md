---
date: 2026-11-08
prefix: QSPE-a7f3
slug: higiene-referencias-drift-assets
format: v2
type: maintenance
---

## [2026-11-08] - Higiene estructural: referencias muertas, drift skill<->workflow y assets

### Resumen
- Referencias muertas resueltas: creado `agent-dist/workflows/quinotospec.flow.md` (orquestador Enterprise prompt-only, MVP) para el comando `/quinotospec.flow` que el complexity-router y el bootstrap ya recomendaban sin existir
- Skills faltantes creadas para workflows huerfanos: `quinotospec-flow`, `quinotospec-quick-dev`, `quinotospec-extension-install`, `quinotospec-preset-install` (inventario 90 -> 94 skills; workflows 47 -> 48)
- `quinotospec-skald`: referencia a `agent-dist/templates/skald-template.md` corregida (ubicacion futura, nunca referenciar hasta que exista); arbol de estructura sincronizado con la realidad
- Rename inconsistente corregido en `quinotospec-migrate` (SKILL + workflow): `quinotospec-generate-branch` -> `quinotospec-generate-github-branch`, alineado con `docs/MIGRATION-GUIDE.md`
- Typos corregidos en `agent-dist/rules/quinotospec-rules.md`: "ADVIETE" -> "ADVIERTA", "elDispatcher" -> "el dispatcher"
- Drift skill<->workflow consolidado: headings corregidos ("# Workflow:" -> "# Skill:") y secciones faltantes restauradas en `apply`, `archive`, `constitution`, `create-proposal`, `create-tasks`, `create-user-stories`, `import` (Paso 3.5 gate de contrato), `retrospective`, `review`, `review-handoff` (Extension hooks), `status`, `update-agents`, `agent-config`
- Nuevo gate anti-drift: `scripts/check-skill-workflow-drift.py` compara referencias a scripts entre cada par workflow/SKILL.md y falla si la skill perdio capacidades; integrado en `validate-all.sh` (48 pares, 0 errores) + suite `tests/test-skill-workflow-drift.sh`
- Test anti-referencias-muertas en `tests/test-help-and-routing.sh`: el workflow recomendado por cada track del router debe existir en disco
- Assets comprimidos: `docs/assets/` paso de 21MB a 3.1MB (downscale + optimizacion PNG; YGGDRASIL 9.24MB -> 0.56MB, tiwaz 2.29MB -> 0.38MB); `berserker.png` (JPEG mal etiquetado) renombrado a `berserker.jpg`
- `scripts/package-release.sh` excluye del tarball las imagenes de marca no referenciadas (YGGDRASIL, Mimir, possessed, amok, berserker)
- `scripts/check-links.sh` ampliado a `docs/`, `examples/` y `extensions/` (103 links verificados, 0 rotos; antes solo raiz + agent-dist)
- `docs/INSPECTION-3.2.0.md` marcado como documento historico (el paquete esta en 3.3.0)
- `legacy/v3/` (548KB sin trackear, con `__pycache__`, sin referencias) eliminado; respaldo en `/tmp/opencode/legacy-v3-backup-20261108-044318.tar.gz`
- Umbrales de inventario sincronizados en `install.sh` y `scripts/validate-all.sh`; manifest actualizado con excepcion de scope documentada

**Validacion**: `bash scripts/validate-all.sh --strict` -> 0 errores, 0 warnings; `tests/run-all-tests.sh` -> 24/24 suites verdes.

**Tiempo Ahorrado**: ~10h (IA: ~50min vs Humano: ~10h de auditoria y sync manual cross-doc)
