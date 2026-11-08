---
name: quinotospec-flow
description: Orquestador Enterprise — encadena el SDLC completo con constitution gates, compliance y aprobación humana estructurada.
---

# Skill: Quinotospec Flow — Orquestador Enterprise

> Un meta-workflow, no un pipeline nuevo: decide qué comando va a cada paso, verifica los gates bloqueantes y deja el flujo reanudable.

> **Fuente de verdad de ejecución:** `agent-dist/workflows/quinotospec.flow.md`. Esta skill expone la capacidad de orquestación; cualquier divergencia se resuelve sincronizando este archivo con el workflow.

## Cuando usar

- El `quinotospec-complexity-router` clasificó el cambio como `enterprise` (más de 10 archivos, más de 2 servicios, contexto regulado)
- El usuario fuerza `--override enterprise` aceptando el ceremonial completo

## Cuando NO usar

- Router devuelve `complex` -> `/quinotospec.create-proposal`
- 2-3 archivos -> `/quinotospec.quick-dev`
- 1 archivo -> `/quinotospec.fix`

## Fases (gates bloqueantes entre fases)

| Fase | Comando que despacha | Gate |
|------|---------------------|------|
| 0. Preflight | `/quinotospec.validate --strict` + router + `quinotospec-conflict-detector` | Sin conflictos, track Enterprise |
| 1. Constitución | `/quinotospec.constitution` | Constitución activa y principios vigentes |
| 2. Contexto | `/quinotospec.discovery` (o `refresh-discovery` si mayor a 30 días) | Discovery fresco + acuerdos de producto reales |
| 3. Propuesta | `/quinotospec.create-proposal` (+ `/quinotospec.heimdallr` si es regulado) | Propuesta validada `--strict` |
| 4. Desglose | `/quinotospec.create-user-stories` -> `/quinotospec.create-tasks` | Contrato validado + prefijos registrados |
| 5. Aprobación humana | — | Approval JSON registrado y validado con `approval_validate.py` |
| 6. Ejecución | Loop de `/quinotospec.apply` con TDD + worktree si aplica | Evidencia validada por tarea |
| 7. Compliance | `/quinotospec.metrics` + `/quinotospec.tiwaz-rune` + `/quinotospec.pre-commit` | Reportes generados |
| 8. Cierre | `/quinotospec.review` -> `review-handoff` -> `/quinotospec.archive` | Revisión y aprobación vigente |

## Comportamiento clave

- Cada fase **delega** en el workflow propietario: nunca duplica su lógica.
- Registra `ultimo_paso_completado` en `.quinoto-spec/` desde la fase 3 para permitir reanudación sin repetir desde el Paso 0.
- Los gates `constitution`, `human-approval`, `tdd`, `verify-before-done` y `validate` no se omiten ni con `--force`.
- Falla de gate -> detener, reportar el gate y el comando de corrección; hotfixes para cruzar gates prohibidos (usar `/quinotospec.rollback` si hace falta).

## Scripts y validadores

| Gate | Comando |
|------|---------|
| Router Enterprise | `python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files {N} --services {N} --regulated --json` |
| Contrato de artefactos | `python3 -B agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict` |
| Evidencia por tarea | `python3 -B agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py validate --kind {KIND} --task-id {TASK_ID} --require --json` |
| Aprobación humana | `python3 -B agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py --require-approval --approval-id {APPROVAL_ID} --approval-subject {SUBJECT} --approval-action {ACTION}` |
| Validación de registro de aprobación | `python3 -B agent-dist/skills/quinotospec-rules-enforce/approval_validate.py` |
