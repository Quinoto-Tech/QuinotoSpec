---
trigger: always_on
---

# Gestión del Changelog
- **SIEMPRE** usa la skill `quinotospec-update-changelog` para registrar cambios después de completar un workflow o tarea importante.

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
    - Si hay errores con severidad BLOCKING → **DETÉN LA EJECUCIÓN** y reporta al usuario.
    - Si hay warnings → Notifica al usuario pero permite continuar con confirmación.
- Ejemplo de error BLOCKING: `08-product-and-agreements.md` vacío, prefijo no registrado.
- Ejemplo de WARNING: Discovery con más de 30 días, branch naming incorrecto.

# Backup Pre-Refactor (BLOQUEANTE)
- **ANTES** de ejecutar `quinotospec.mjolnir-refactor`:
    - Crea un backup completo en `.quinoto-spec/backups/pre-refactor-{YYYYMMDD-HHmmss}/`.
    - El backup debe incluir: propuesta, user stories, tareas, y archivos de código afectados.
    - Confirma con el usuario antes de proceder: "Backup creado en {ruta}. ¿Continuar con el refactor?"
- Si el backup falla → **DETÉN LA EJECUCIÓN**. No hacer refactor sin red de seguridad.
- Después de un refactor exitoso, el backup se mantiene por 7 días antes de limpieza automática.

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