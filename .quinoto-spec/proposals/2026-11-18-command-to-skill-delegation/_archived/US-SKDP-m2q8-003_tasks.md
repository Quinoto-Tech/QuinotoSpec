# Plan de Tareas (Command-to-Skill Delegation — US-SKDP-m2q8-003)

**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Prefijo:** SKDP-m2q8
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-SKDP-m2q8-007 | Backend | Reemplazar 48 comandos por sus stubs | Aplicar los stubs generados a todos los pares salvo `review`; conservar frontmatter (`description`, `agent`, `model`) y verificar que 0 comandos conservan el prompt completo. | US-SKDP-m2q8-003 | command-layer | agent-dist/workflows/quinotospec.*.md (48 archivos, excepto review) | M | P2 | TSK-SKDP-m2q8-002, TSK-SKDP-m2q8-003, TSK-SKDP-m2q8-006 | [x] |
| TSK-SKDP-m2q8-008 | Backend | Migrar el par review tras PWRE + verificación multi-IDE | Revalidar el contenido del par `review` contra los cambios de PWRE-9f2c (si sigue En Curso, excluirlo con deuda registrada); convertirlo cuando esté listo. Verificar resolución del stub en instalación local y global con el patrón de `test-installed-paths.sh` (0 refs `agent-dist/`). | US-SKDP-m2q8-003 | command-layer | agent-dist/workflows/quinotospec.review.md, agent-dist/skills/quinotospec-review/SKILL.md, tests/test-installed-paths.sh | M | P2 | TSK-SKDP-m2q8-007 | [x] |
