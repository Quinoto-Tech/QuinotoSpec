# Plan de Tareas (Command-to-Skill Delegation — US-SKDP-m2q8-005)

**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Prefijo:** SKDP-m2q8
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-SKDP-m2q8-011 | Config | Invertir documentación a skill como fuente de verdad | Sustituir en ~40 SKILL.md y en AGENTS.md/docs/ARCHITECTURE/README las frases "workflow es la fuente de verdad; skill a sincronizar" por "el comando delega en esta skill"; documentar el patrón de resolución por archivo del stub. | US-SKDP-m2q8-005 | docs | agent-dist/skills/*/SKILL.md (~40), AGENTS.md, docs/ARCHITECTURE.md, README.md, README_EN.md | M | P2 | TSK-SKDP-m2q8-007, TSK-SKDP-m2q8-008 | [x] |
| TSK-SKDP-m2q8-012 | DevOps | Gates finales y changelog (vigencia de aprobación pre-Apply) | Verificar que la aprobación registrada y validada ANTES de TSK-001 sigue vigente (`.quinoto-spec/approvals/SKDP-m2q8-APPLY.json`, override F-05); ejecutar `validate-all.sh --strict` 0/0 y `run-all-tests.sh` ≥31/31, verificar que `test-installed-paths.sh` sigue en verde, y registrar changelog de cierre. | US-SKDP-m2q8-005 | docs | .quinoto-spec/approvals/, .quinoto-spec/evidence/, .quinoto-spec/changelog/ | S | P2 | TSK-SKDP-m2q8-008, TSK-SKDP-m2q8-010, TSK-SKDP-m2q8-011 | [x] |
