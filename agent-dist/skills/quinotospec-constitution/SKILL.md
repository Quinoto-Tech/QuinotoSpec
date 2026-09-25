---
name: quinotospec-constitution
description: Generar o enmendar la constitución del proyecto con principios verificables, gates y aprobación explícita.
---

# Skill: QuinotoSpec Constitution

Usa esta skill cuando el usuario solicite definir, activar o enmendar `.quinoto-spec/constitution.md`.

## Contrato

- La constitución es opcional para compatibilidad.
- Si existe con estado `active`, sus principios bloquean Apply, Review y Archive cuando hay violación.
- No puede derogar reglas globales, legales, de seguridad o TDD/verify-before-done.
- No inventes cifras: usa valores confirmados o `N/A — no aplica`.
- No sobrescribas una constitución existente sin diff y aprobación explícita.

## Flujo

1. Lee discovery, reglas globales y constitución existente.
2. Pregunta por calidad, testing, UX y performance; registra defaults del stack.
3. Genera el borrador desde `agent-dist/templates/constitution-template.md`.
4. Resuelve placeholders y valida que cada principio tenga evidencia o `N/A`.
5. Presenta el borrador y solicita aprobación antes de `active`.
6. Registra la decisión explícita en `.quinoto-spec/approvals/{{APPROVAL_ID}}.json` y valida `human-approval` con `rules_enforce.py --require-approval --approval-id {{APPROVAL_ID}} --approval-subject .quinoto-spec/constitution.md --approval-action constitution`.
7. Registra enmiendas con `quinotospec-update-changelog`.

## Checks

- [ ] No quedan placeholders.
- [ ] No hay conflictos con reglas globales.
- [ ] Los quality gates indican cómo verificarlos.
- [ ] TDD y verify-before-done siguen siendo obligatorios.
- [ ] La aprobación del usuario está registrada.
- [ ] El estado final es `draft` o `active` de forma explícita.

## Integración

Los consumidores deben consultar esta constitution antes de actuar:

- `quinotospec-apply`
- `quinotospec-review`
- `quinotospec-archive`

La ausencia del archivo produce una advertencia de compatibilidad, no un bloqueo.
