# Tasks — Elephant-Goldfish Adoption

| ID | Título | Historia | Archivos | Dependencias | Estado |
|----|--------|----------|----------|--------------|--------|
| TSK-EGMS-4f2a-001 | Implementar `readiness_validate.py` (rutas, comandos, criterios) | US-EGMS-4f2a-003 | agent-dist/skills/quinotospec-rules-enforce/readiness_validate.py | — | ⬜ Pendiente |
| TSK-EGMS-4f2a-002 | Integrar readiness en Apply y rules_enforce | US-EGMS-4f2a-003 | agent-dist/workflows/quinotospec.apply.md, agent-dist/skills/quinotospec-apply/SKILL.md, agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py | TSK-EGMS-4f2a-001 | ⬜ Pendiente |
| TSK-EGMS-4f2a-003 | Crear skill/workflow `quinotospec-goldfish-review` | US-EGMS-4f2a-001 | agent-dist/skills/quinotospec-goldfish-review/SKILL.md, agent-dist/workflows/quinotospec.goldfish-review.md | — | ⬜ Pendiente |
| TSK-EGMS-4f2a-004 | Implementar orquestador de subagentes y `review-findings.md` | US-EGMS-4f2a-001 | agent-dist/skills/quinotospec-goldfish-review/goldfish.py | TSK-EGMS-4f2a-003 | ⬜ Pendiente |
| TSK-EGMS-4f2a-005 | Crear skill/workflow `quinotospec-brainstorm` (7 lentes) | US-EGMS-4f2a-002 | agent-dist/skills/quinotospec-brainstorm/SKILL.md, agent-dist/workflows/quinotospec.brainstorm.md | — | ⬜ Pendiente |
| TSK-EGMS-4f2a-006 | Implementar `drift-report` (specs/docs vs código) | US-EGMS-4f2a-004 | agent-dist/skills/quinotospec-drift-report/SKILL.md, agent-dist/skills/quinotospec-drift-report/drift.py, agent-dist/workflows/quinotospec.drift-report.md | — | ⬜ Pendiente |
| TSK-EGMS-4f2a-007 | Añadir UI `/drift` (readers + template + ruta) | US-EGMS-4f2a-005 | agent-dist/ui/readers.py, agent-dist/ui/templates.py, agent-dist/ui/server.py | TSK-EGMS-4f2a-006 | ⬜ Pendiente |
| TSK-EGMS-4f2a-008 | Tests: `test-readiness.sh`, `test-goldfish.sh`, `test-drift.sh` | US-EGMS-4f2a-001 | tests/ | TSK-001, TSK-004, TSK-006 | ⬜ Pendiente |
| TSK-EGMS-4f2a-009 | Actualizar manifest, AGENTS.md, README y changelog | US-EGMS-4f2a-005 | manifest.json, AGENTS.md, README.md, README_EN.md | TSK-001..008 | ⬜ Pendiente |
