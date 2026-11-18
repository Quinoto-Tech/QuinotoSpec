# Plan de Tareas (Command-to-Skill Delegation — US-SKDP-m2q8-001)

**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Prefijo:** SKDP-m2q8
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-SKDP-m2q8-001 | Test | Inventario de paridad de los 49 pares | Automatizar el comparativo H2 + referencias `*.py|sh|js` entre cada workflow y su skill pareada; clasificar los 49 pares por similitud, listar el contenido workflow-only de los 10 resumidos y ejecutar el checker actual como evidencia pre-conversión (0 errores). | US-SKDP-m2q8-001 | skill-layer | .quinoto-spec/evidence/TSK-SKDP-m2q8-001/ (script de inventario + reporte) | M | P2 | — | [x] |
| TSK-SKDP-m2q8-002 | Backend | Consolidar skills críticas (flow, constitution, agent-config) | Portar a los SKILL.md todo el contenido funcional de sus workflows (fases/gates del orquestador, gates de constitución, capas TOML), preservando parámetros y referencias a scripts. Verificar con el inventario de TSK-001. | US-SKDP-m2q8-001 | skill-layer | agent-dist/skills/quinotospec-flow/SKILL.md, agent-dist/skills/quinotospec-constitution/SKILL.md, agent-dist/skills/quinotospec-agent-config/SKILL.md | L | P2 | TSK-SKDP-m2q8-001 | [x] |
| TSK-SKDP-m2q8-003 | Backend | Consolidar las 7 skills resumidas restantes | Portar el contenido funcional de review-handoff, help, ui, quick-dev, preset-install, update-agents y extension-install desde sus workflows; verificar paridad H2/scripts con el inventario. | US-SKDP-m2q8-001 | skill-layer | agent-dist/skills/quinotospec-review-handoff/SKILL.md, agent-dist/skills/quinotospec-help/SKILL.md, agent-dist/skills/quinotospec-ui/SKILL.md, agent-dist/skills/quinotospec-quick-dev/SKILL.md, agent-dist/skills/quinotospec-preset-install/SKILL.md, agent-dist/skills/quinotospec-update-agents/SKILL.md, agent-dist/skills/quinotospec-extension-install/SKILL.md | L | P2 | TSK-SKDP-m2q8-001 | [x] |
