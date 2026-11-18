# All Tasks (Command-to-Skill Delegation)

**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Prefijo:** SKDP-m2q8
**Estado:** completed

**Regla de conteo (prevalece sobre el resto del documento):** 49 = universo de pares; **48 = target operativo de este Apply**; el par `review` es el techo condicional que se convierte solo cuando PWRE-9f2c cierre (deuda en `.quinoto-spec/reviews/SKDP-m2q8-review-pair-debt.md`). **Secuencia de aprobación:** `SKDP-m2q8-APPLY.json` se registró y validó con `approval_validate.py` ANTES de TSK-001 y de cualquier edición de producción; TSK-012 únicamente verifica su vigencia.

Consolidado de las tareas de todas las user stories. Fuente por story: `US-SKDP-m2q8-00N_tasks.md`.

| ID | Tipo | Título | Historia Relacionada | Servicio | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|
| TSK-SKDP-m2q8-001 | Test | Inventario de paridad de los 49 pares | US-SKDP-m2q8-001 | skill-layer | M | P2 | — | [x] |
| TSK-SKDP-m2q8-002 | Backend | Consolidar skills críticas (flow, constitution, agent-config) | US-SKDP-m2q8-001 | skill-layer | L | P2 | TSK-SKDP-m2q8-001 | [x] |
| TSK-SKDP-m2q8-003 | Backend | Consolidar las 7 skills resumidas restantes | US-SKDP-m2q8-001 | skill-layer | L | P2 | TSK-SKDP-m2q8-001 | [x] |
| TSK-SKDP-m2q8-004 | Test | RED: test detecta prompt duplicado | US-SKDP-m2q8-002 | command-layer | S | P2 | TSK-SKDP-m2q8-001 | [x] |
| TSK-SKDP-m2q8-005 | Backend | Generador de stubs con resolución multi-IDE | US-SKDP-m2q8-002 | command-layer | M | P2 | TSK-SKDP-m2q8-004 | [x] |
| TSK-SKDP-m2q8-006 | Backend | Renderizar y verificar 48 stubs en repo fuente (sin escribir aún) | US-SKDP-m2q8-002 | command-layer | M | P2 | TSK-SKDP-m2q8-005 | [x] |
| TSK-SKDP-m2q8-007 | Backend | Reemplazar 48 comandos por sus stubs | US-SKDP-m2q8-003 | command-layer | M | P2 | TSK-SKDP-m2q8-002, TSK-SKDP-m2q8-003, TSK-SKDP-m2q8-006 | [x] |
| TSK-SKDP-m2q8-008 | Backend | Migrar el par review tras PWRE + verificación multi-IDE | US-SKDP-m2q8-003 | command-layer | M | P2 | TSK-SKDP-m2q8-007 | [x] |
| TSK-SKDP-m2q8-009 | Backend | Checker invertido: delegación en vez de paridad | US-SKDP-m2q8-004 | drift-checker | M | P2 | TSK-SKDP-m2q8-006 | [x] |
| TSK-SKDP-m2q8-010 | Test | Tests del nuevo contrato + resolución instalada | US-SKDP-m2q8-004 | drift-checker | M | P2 | TSK-SKDP-m2q8-009, TSK-SKDP-m2q8-006 | [x] |
| TSK-SKDP-m2q8-011 | Config | Invertir documentación a skill como fuente de verdad | US-SKDP-m2q8-005 | docs | M | P2 | TSK-SKDP-m2q8-007, TSK-SKDP-m2q8-008 | [x] |
| TSK-SKDP-m2q8-012 | DevOps | Gates finales y changelog (vigencia de aprobación pre-Apply) | US-SKDP-m2q8-005 | docs | S | P2 | TSK-SKDP-m2q8-008, TSK-SKDP-m2q8-010, TSK-SKDP-m2q8-011 | [x] |
