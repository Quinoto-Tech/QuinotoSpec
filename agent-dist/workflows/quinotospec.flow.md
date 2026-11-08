---
description: Orquestador Enterprise — encadena el SDLC completo con constitution gates, compliance y aprobación humana estructurada.
---

# Workflow: Flow (Enterprise)

[INSTRUCCIÓN MAESTRA]
Debes orquestar el ciclo completo de desarrollo para un cambio de complejidad **Enterprise**. Este workflow NO duplica lógica de los workflows que encadena: su única función es decidir qué comando va a cada paso, verificar los gates bloqueantes entre fases y registrar `ultimo_paso_completado` en el archivo de la propuesta para permitir reanudación.

**Cuándo usar este workflow:**

- El `quinotospec-complexity-router` clasificó el cambio como `enterprise` (más de 10 archivos, más de 2 servicios, contexto regulado/compliance)
- El usuario fuerza `--override enterprise` aceptando el ceremonial completo
- Multi-team, migraciones mayores o dominios regulados (PCI, HIPAA, GDPR)

**Cuándo NO usar este workflow:**

- El router devuelve `complex` -> usar `/quinotospec.create-proposal` directamente
- Cambios de 2-3 archivos -> `/quinotospec.quick-dev`
- Cambios de 1 archivo -> `/quinotospec.fix`

**Parámetros:**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| Descripción del cambio | Sí | Qué hay que hacer y por qué |
| `--files` `N` | No | Archivos estimados (para re-ejecutar el router) |
| `--services` `N` | No | Servicios afectados |
| `--override enterprise` | No | Fuerza el track Enterprise |

**Invocación:**

```bash
@quinotospec.flow "Migración multi-servicio del módulo de pagos a un contexto PCI"
@quinotospec.flow --files 30 --services 3 --regulated "Refactor del stack de datos"
```

---

## Paso 0 — Preflight y routing

1. Ejecutar el router con los datos del cambio:

   ```bash
   python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files {N} --services {N} --regulated --json
   ```

   Si el track no es `enterprise`, detener y derivar al workflow recomendado.
2. Ejecutar `/quinotospec.validate --strict` para pre-pillar estado inválido del proyecto.
3. Ejecutar `quinotospec-conflict-detector` contra las propuestas activas: si hay solapamiento de archivos, servicios o dominios, detener y resolver el conflicto antes de avanzar.

## Paso 1 — Constitution gate (BLOQUEANTE)

1. Verificar `.quinoto-spec/constitution.md`: si no existe, ejecutar `/quinotospec.constitution` o registrar advertencia y decidir con el usuario.
2. Si está en `active`, cada fase subsiguiente debe verificar sus principios aplicables antes de continuar.
3. Si una decisión requiere cambio de constitución, detener y tramitar la enmienda con aprobación humana explícita.

## Paso 2 — Contexto (Discovery)

1. Verificar frescura de `.quinoto-spec/discovery/`: si los archivos tienen más de 30 días, ejecutar `/quinotospec.refresh-discovery`.
2. Si no existe discovery, ejecutar `/quinotospec.discovery` completo.
3. Verificar `08-product-and-agreements.md`: si solo tiene placeholders o está vacío, detener y pedir al usuario DoR/DoD (regla BLOQUEANTE de Product Agreement Check).

## Paso 3 — Propuesta

1. Ejecutar `/quinotospec.create-proposal`.
2. Si el alcance es security-sensitive o regulado, ejecutar `/quinotospec.heimdallr` (STRIDE/DREAD) y adjuntar el resultado a la propuesta.
3. Validar la propuesta con `/quinotospec-syntax-validate --type proposal --slug {SLUG} --strict`.
4. Registrar `ultimo_paso_completado: propuesta` en el YAML de la propuesta.

## Paso 4 — Desglose

1. Ejecutar `/quinotospec.create-user-stories`.
2. Ejecutar `/quinotospec.create-tasks`.
3. Verificar que cada ID (`US-MNEM-suffix-NNN`, `TSK-MNEM-suffix-NNN`) esté en el registro de prefijos y que la validación del contrato pase:

   ```bash
   python3 -B agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
   ```

4. Registrar `ultimo_paso_completado: tareas`.

## Paso 5 — Aprobación humana (BLOQUEANTE)

1. Antes de aplicar cualquier tarea, registrar `.quinoto-spec/approvals/{APPROVAL_ID}.json` con la decisión humana sobre la propuesta.
2. El registro debe incluir `schema_version`, `approval_id`, `decision`, `subject`, `action`, `requested_by`, `decided_by`, `decided_at`, `rationale` y `scope`.
3. Validar el registro con `rules_enforce.py --require-approval --approval-id {APPROVAL_ID}` y el validador read-only `agent-dist/skills/quinotospec-rules-enforce/approval_validate.py`. Una conversación o bandera CLI no sustituye el registro estructurado.

## Paso 6 — Ejecución (loop por tarea)

Para cada tarea en orden de dependencias:

1. Ejecutar `/quinotospec.apply` con la tarea.
2. Aplicar `quinotospec-tdd`: RED obligatorio antes de código de producción.
3. Si `USE_WORKTREE=true`, usar `quinotospec-worktree` con baseline limpia verificada.
4. Si una prueba falla, cambiar a `quinotospec-debug`; si es un refactor Mjolnir, ejecutar backup verificable (Regla #10) antes de tocar código.
5. Completar con `quinotospec-verify-before-done` y validar la evidencia:

   ```bash
   python3 -B agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py validate --kind {KIND} --task-id {TASK_ID} --require --json
   ```

6. Registrar `ultimo_paso_completado: tarea-{TASK_ID}` en el YAML de tareas.

## Paso 7 — Compliance

1. Ejecutar `/quinotospec.metrics` para compliance del ciclo.
2. Ejecutar `/quinotospec.tiwaz-rune` sobre el servicio tocado; adjuntar el reporte a la propuesta.
3. Ejecutar `/quinotospec.pre-commit` para el check abierto.

## Paso 8 — Cierre

1. Ejecutar `/quinotospec.review` contra los criterios de aceptación de la propuesta.
2. Ejecutar `/quinotospec.review-handoff` para generar la guía del revisor humano.
3. Con revisión aprobada y registro de aprobación vigente, ejecutar `/quinotospec.archive`.
4. Actualizar el changelog con `/quinotospec.update-changelog`.
5. Después de cada paso que modifique código o documentación, ejecutar `quinotospec-blood-bond-monitor --check-only` (regla global).

## Manejo de errores

- Cualquier gate bloqueante falla -> detener el flujo, reportar el gate exacto y el comando de corrección.
- No aplicar hotfixes para cruzar gates; usar `/quinotospec.rollback` si el estado quedó inconsistente.
- Interrupción -> reanudar desde `ultimo_paso_completado`, no repetir desde el Paso 0.

## Reglas

- Nada de lógica duplicada: cada fase delega en el workflow/skill propietario; si el contenido del paso difiere del workflow enlazado, gana el workflow enlazado.
- Los gates `constitution`, `human-approval`, `tdd`, `verify-before-done` y `heimdallr` (si es regulado) no se omite ni con `--force`.
- El registro de `ultimo_paso_completado` en `.quinoto-spec/` es obligatorio desde el Paso 3; sin él el flujo no es reanudable y se considera fallido.
- Los gates `constitution`, `human-approval`, `tdd`, `verify-before-done` y `validate` no se omiten ni con `--force`; `--force` solo puede forzar el archivado según la regla BLOQUEANTE de Verificación Antes de Completar.
