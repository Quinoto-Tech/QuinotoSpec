---
trigger: always_on
---

# Gestión del Changelog
- **SIEMPRE** usa la skill `quinotospec-update-changelog` para registrar cambios después de completar un workflow o tarea importante.
- El formato canónico es v2 append-only en `.quinoto-spec/changelog/`; v1 se acepta como adaptador legacy.
- Una reversión agrega una entrada `revert`; nunca elimina una entrada existente.

# Gestión de Prefijos e IDs
- Al crear propuestas, tareas o user stories, adhiérete **ESTRICTAMENTE** a los prefijos únicos definidos en `.quinoto-spec/prefix-registry.md` (formato `MNEMONICO-UUID`, ej. `AUTH-a1b2`).
- Nunca inventes un prefijo sin registrarlo primero en esa tabla ni uses formatos que no garanticen la idempotencia.

# Product Agreement Check (BLOQUEANTE)
- **ANTES** de ejecutar cualquier workflow de creación de propuestas (ej. `quinotospec.create-proposal`):
    - Verifica el archivo `.quinoto-spec/discovery/08-product-and-agreements.md`.
    - SI el archivo contiene solo los títulos/placeholders originales o está vacío → **DETÉN LA EJECUCIÓN**.
    - **Notifica al usuario**: "No puedo crear la propuesta porque no se han definido los Acuerdos de Producto (DoR/DoD) en `.quinoto-spec/discovery/08-product-and-agreements.md`. Por favor complétalo primero."
- No ignores esta regla aunque el usuario insista, a menos que se use un override explícito.

# No Sobreescribir Archivos de Especificación
- Si un archivo de stories (`user-stories.md`) o tareas (`*_tasks.md`) ya existe, **NUNCA sobreescribas**. Realiza siempre un merge inteligente: agrega las entradas nuevas y actualiza las que hayan cambiado.

# Validación de Estado Antes de Archivar
- Antes de archivar cualquier propuesta, user story o tarea, verifica que el `**Estado:**` en `proposal.md` sea `✅ Completada`. Si quedan elementos sin completar, advertir al usuario antes de proceder.

# Convención de Archivado
- Usa **siempre** la carpeta `_archived/` para mover elementos archivados (nunca el prefijo `__`).
- Estructura: `.quinoto-spec/proposals/{{SLUG}}/_archived/` para archivos individuales, `.quinoto-spec/proposals/_archived/{{SLUG}}/` para propuestas completas.

# Convención de Nombrado de Branches
- Los branches siempre deben seguir el formato: `feature/{{TASK_ID}}-descripcion-en-kebab-case`.
- Nunca crear un branch sin el `TASK_ID` o `US_ID` al inicio del nombre.

# Aprobación de Configuración Crítica
- **NUNCA** modifiques los siguientes archivos de configuración sin explicitar los cambios al usuario y obtener su aceptación:
    - `.quinoto-spec/sprints/base-config.yml`
    - `.quinoto-spec/sprints/sprint-{{ID}}/sprint-config.yml`
    - `.quinoto-spec/*/mjolnir-refactor.yml`
- Esta regla aplica tanto para la creación inicial (si requiere datos del usuario) como para modificaciones posteriores.

# Validación Pre-Workflow Crítico (BLOQUEANTE)
- **ANTES** de ejecutar workflows de creación o modificación (`create-proposal`, `apply`, `create-tasks`, `create-user-stories`):
    - Ejecuta `quinotospec-validate --full` como precondición.
    - Ejecuta `python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict` para verificar el contrato de artefactos.
    - Si hay errores con severidad BLOCKING → **DETÉN LA EJECUCIÓN** y reporta al usuario.
    - Si hay warnings → Notifica al usuario pero permite continuar con confirmación.
- El contrato requiere IDs canónicos `US-MNEM-suffix-NNN` y `TSK-MNEM-suffix-NNN`, relación explícita task→story y estados normalizados.
- Ejemplo de error BLOCKING: `08-product-and-agreements.md` vacío, prefijo no registrado, task sin story.
- Ejemplo de WARNING: Discovery con más de 30 días, branch naming incorrecto, formato legacy.

# Backup Pre-Refactor (BLOQUEANTE)
- **ANTES** de ejecutar `quinotospec.mjolnir-refactor`:
    - Ejecuta `python3 -B agent-dist/skills/quinotospec-backup/backup.py create --root . --type full --json`.
    - Verifica el resultado con `backup.py verify --backup BACKUP_ID --json`.
    - El store por defecto es `.quinoto-spec-backups/`, fuera de `.quinoto-spec/`; nunca copies o borres el source manualmente.
    - Confirma con el usuario antes de proceder: "Backup verificado {BACKUP_ID}. ¿Continuar con el refactor?"
- Si la creación o verificación falla → **DETÉN LA EJECUCIÓN**. No hacer refactor sin red de seguridad.
- Después de un refactor exitoso, conserva el backup según la política de cleanup; la eliminación requiere confirmación explícita.

# Validación de Sintaxis Pre-Apply
- **ANTES** de ejecutar `quinotospec.apply`:
    - Ejecuta `quinotospec-syntax-validate --type proposal --slug {SLUG}` para validar la propuesta.
    - Si la validación de sintaxis falla → **ADVIETE al usuario** con los errores encontrados.
    - Permite continuar solo si el usuario confirma explícitamente ("¿Continuar a pesar de los errores de sintaxis? [y/N]").
- Esto previene aplicar tareas basadas en propuestas mal formadas que pueden llevar a implementaciones incorrectas.

# Protección de Archivos Archivados (BLOQUEANTE)
- **NUNCA** modifiques, elimines o muevas archivos dentro de carpetas `_archived/` sin:
  1. Confirmación **explícita** del usuario (no implícita).
  2. Justificación documentada en el changelog con `quinotospec-update-changelog`.
- Los archivos archivados son registro histórico inmutable. Alterarlos rompe la trazabilidad.
- Si necesitas recuperar un archivo archivado, **copialo** fuera de `_archived/` en lugar de moverlo.
- Excepción: El workflow `quinotospec.archive` puede mover archivos HACIA `_archived/`, pero nunca modificar los que ya están dentro.

# Blood-Bond Monitor (Global)
- Después de completar CUALQUIER workflow que modifique código o documentación (apply, fix, tiwaz-rune, heimdallr), ejecutar skill `quinotospec-blood-bond-monitor --check-only`:
  - Si `should_remind: true` (inactivo >=14 días), mostrar recordatorio pasivo con suggestions.
  - Si `should_remind: false`, no mostrar nada.
- Esta regla aplica globalmente. Los workflows individuales NO necesitan repetir este bloque.

# TDD Enforcement (STANDARD)
- Esta regla es prompt-level; el enforcement global queda como trabajo de infraestructura posterior.
- **ANTES** de escribir código de producción, ejecuta `quinotospec-tdd` y observa un test RED que falle por la razón esperada.
- El ciclo obligatorio es RED → GREEN → REFACTOR; guarda comando, salida y resultado de cada fase.
- Los cambios de documentación, configuración o migración pueden usar una verificación determinista apropiada, pero deben justificar la excepción.
- Si el test falla por scaffolding o entorno, corrige el scaffolding y repite el RED antes de implementar.

# Debugging Sistematico (STANDARD)
- Esta regla es prompt-level; no sustituye un dispatcher ejecutable.
- Cuando una prueba, ejecución o regresión falle, usa `quinotospec-debug` antes de aplicar un hotfix.
- Reproduce, localiza el primer valor incorrecto, formula una hipótesis falsable y registra el experimento.
- Tras tres hipótesis fallidas, detén los parches locales y revisa la arquitectura o el contrato.

# Verificacion Antes de Completar (BLOQUEANTE)
- Esta regla es prompt-level; el workflow debe detener el claim cuando la evidencia falte.
- **ANTES** de cambiar el estado de una tarea o moverla a `_archived/`, ejecuta `quinotospec-verify-before-done`.
- Exige evidencia fresca de tests, lint, typecheck y criterios de aceptación aplicables.
- `--force` solo puede forzar el archivado; no elimina la evidencia ni permite declarar `completed` sin verificación.
- Si falta una comprobación, deja la tarea en `in_progress` o `blocked` y reporta el bloqueo.

# Constitutional Compliance (BLOQUEANTE)
- Si `.quinoto-spec/constitution.md` existe con estado `active`, Apply, Review y Archive deben verificar cada principio aplicable antes de continuar.
- La constitución solo puede añadir restricciones más estrictas; nunca deroga reglas globales, legales, de seguridad, TDD o verify-before-done.
- Si la constitución está ausente, registra una advertencia de compatibilidad; si está en `draft`, no la trates como gate activo.
- Una violación constitucional bloquea el workflow hasta obtener una enmienda aprobada o una decisión explícita del usuario.

# Aprobación Humana Estructurada (BLOQUEANTE)
- Cuando una regla, configuración crítica, cambio de constitución o movimiento protegido requiera decisión humana, registra un JSON en `.quinoto-spec/approvals/<APPROVAL_ID>.json` antes de habilitar el gate.
- El registro debe incluir `schema_version`, `approval_id`, `decision`, `subject`, `action`, `requested_by`, `decided_by`, `decided_at`, `rationale` y `scope`.
- `decision` solo puede ser `approved`, `rejected` o `deferred`; únicamente `approved` habilita el gate y elDispatcher debe verificar que `subject` y `action` coincidan exactamente con la operación.
- Una aprobación explícita en el chat, una bandera CLI o un texto genérico no sustituyen el registro estructurado cuando se exige este gate.
- El validador es read-only: no demuestra identidad ni ejecuta comandos; una aprobación vencida, ausente, fuera de alcance o no aprobada bloquea la operación.
- Usa `approval_validate.py` y registra el ID, actor, fecha, alcance y justificación; nunca edites una aprobación existente para reutilizarla en otra operación.
