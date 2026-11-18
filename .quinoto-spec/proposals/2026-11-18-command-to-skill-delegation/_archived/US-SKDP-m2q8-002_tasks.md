# Plan de Tareas (Command-to-Skill Delegation — US-SKDP-m2q8-002)

**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Prefijo:** SKDP-m2q8
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-SKDP-m2q8-004 | Test | RED: test detecta prompt duplicado | Escribir la aserción que FALLA hoy: un workflow con el prompt completo de su skill debe ser detectado como duplicado. Registrar RED en `.quinoto-spec/evidence/TSK-SKDP-m2q8-004/` con evidencia validada. | US-SKDP-m2q8-002 | command-layer | tests/test-skill-workflow-drift.sh, .quinoto-spec/evidence/TSK-SKDP-m2q8-004/ | S | P2 | TSK-SKDP-m2q8-001 | [x] |
| TSK-SKDP-m2q8-005 | Backend | Generador de stubs con resolución multi-IDE | Crear `scripts/generate-command-stubs.py`: plantilla única con `<skill-id>` y `$ARGUMENTS`, resolución por archivo (source → `.opencode/.cursor/.claude/.agent/skills` → global), fallo explícito con rutas intentadas, modo `--check` que detecta desviaciones. | US-SKDP-m2q8-002 | command-layer | scripts/generate-command-stubs.py | M | P2 | TSK-SKDP-m2q8-004 | [x] |
| TSK-SKDP-m2q8-006 | Backend | Renderizar y verificar 48 stubs en repo fuente (sin escribir aún) | Renderizar los 48 stubs del inventario (excluido `review`); verificar que difieren solo en `<skill-id>`/`description` y que desde el repo fuente el stub resuelve `agent-dist/skills/.../SKILL.md`. La ESCRITURA en los workflows ocurre en TSK-007. | US-SKDP-m2q8-002 | command-layer | scripts/generate-command-stubs.py, evidencia de render (sin modificar workflows aún) | M | P2 | TSK-SKDP-m2q8-005 | [x] |
