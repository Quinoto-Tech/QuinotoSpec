---
description: Genera y gobierna la constitución del proyecto con principios verificables y aprobación explícita
---

# Workflow: Constitution

Crea `.quinoto-spec/constitution.md` como fuente de principios del proyecto. La constitución es opcional para no bloquear proyectos existentes, pero si está activa sus principios son obligatorios para Apply, Review y Archive.

## Parámetros

- `PROJECT_NAME`: nombre del proyecto.
- `STACK`: stack detectado o confirmado por el usuario.
- `STATUS`: `draft` o `active`; solo `active` después de aprobación explícita.
- `AMENDMENT`: texto opcional para modificar una constitución existente.

## Paso 0 — Preflight

1. Lee `agent-dist/rules/quinotospec-rules.md` y las convenciones del proyecto.
2. Lee `.quinoto-spec/discovery/01-stack-profile.md` y, si existe, arquitectura, seguridad y findings.
3. Si ya existe `.quinoto-spec/constitution.md`, no lo sobrescribas: genera un diff y solicita aprobación explícita.
4. Detecta conflictos con TDD, verify-before-done, seguridad, compliance o reglas globales.

## Paso 1 — Definir principios

Solicita o confirma principios para:

- Calidad de código.
- Testing y evidencia.
- UX y accesibilidad.
- Performance y límites operativos.

Permite `N/A — no aplica` con justificación. No inventes cobertura, budgets, WCAG o compliance: usa valores propuestos por el usuario o `N/A`.

## Paso 2 — Generar constitution.md

Usa `agent-dist/templates/constitution-template.md` como base.

- Resuelve todos los placeholders o márcalos explícitamente como pendientes.
- Conserva IDs estables para cada principio cuando sea posible.
- Incluye objetivo, estado, owner, fecha, stack y evidencia de aprobación.
- Define cómo se verifica cada quality gate.
- No incluyas secretos ni valores de producción.

## Paso 3 — Validar

Antes de activar la constitución:

1. Comprueba que no queden placeholders sin resolver.
2. Comprueba que cada principio sea verificable o esté marcado `N/A — no aplica`.
3. Contrasta la constitución con las reglas globales y TDD/verify-before-done.
4. Ejecuta `python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict` cuando exista `.quinoto-spec/`.
5. Registra la decisión humana en `.quinoto-spec/approvals/{{APPROVAL_ID}}.json` solo después de la confirmación explícita del usuario. Valida con `python3 -B agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py --root . --profile target --action constitution --check human-approval --require-approval --approval-id {{APPROVAL_ID}} --approval-subject .quinoto-spec/constitution.md --approval-action constitution --json`; no actives el borrador si el gate falla.
6. Registra conflictos y requiere decisión explícita; no los resuelvas silenciosamente.

## Paso 4 — Aprobación y enmiendas

- Presenta el borrador completo al usuario.
- Cambia `status: active` solo después de aprobación explícita.
- Para enmiendas, compara versiones, solicita aprobación y registra el cambio con `quinotospec-update-changelog`.
- Una constitución nunca deroga reglas legales, de seguridad o globales; solo puede añadir restricciones más estrictas.

## Gates de consumidores

- **Apply**: si existe constitución activa, verifica compliance antes de implementar; si falta, advierte y permite continuar.
- **Review**: incluye compliance constitucional en el checklist y reporta principios, evidencia y excepciones.
- **Archive**: si existe constitución activa, verifica compliance antes de mover artefactos.

## Errores

- Placeholder sin resolver: devuelve el borrador como `draft`.
- Conflicto con regla global: detiene la activación y explica el conflicto.
- Enmienda sin aprobación: no escribe el archivo.
- Constitución ausente: los consumidores Advieren, pero no rompen compatibilidad.

## Output

`.quinoto-spec/constitution.md` en estado `draft` o `active`, más un resumen de principios, gates, conflictos y aprobación requerida.
