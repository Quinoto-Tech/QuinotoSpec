---
trigger: always_on
---

# Gestión del Changelog
- **SIEMPRE** usa la skill `quinotospec-update-changelog` para registrar cambios después de completar un workflow o tarea importante.

# Gestión de Prefijos e IDs
- Al crear propuestas, tareas o historias de usuario, adhiérete **ESTRICTAMENTE** a los prefijos definidos en `.quinoto-spec/prefix-registry.md`.
- Nunca inventes un prefijo sin registrarlo primero en esa tabla.

# Product Agreement Check (BLOQUEANTE)
- **ANTES** de ejecutar cualquier workflow de creación de propuestas (ej. `quinotospec.create-proposal`):
    - Verifica el archivo `.quinoto-spec/discovery/07-product-and-agreements.md`.
    - SI el archivo contiene solo los títulos/placeholders originales o está vacío → **DETÉN LA EJECUCIÓN**.
    - **Notifica al usuario**: "No puedo crear la propuesta porque no se han definido los Acuerdos de Producto (DoR/DoD) en `.quinoto-spec/discovery/07-product-and-agreements.md`. Por favor complétalo primero."
- No ignores esta regla aunque el usuario insista, a menos que se use un override explícito.

# No Sobreescribir Archivos de Especificación
- Si un archivo de historias (`user-histories.md`) o tareas (`*_tasks.md`) ya existe, **NUNCA sobreescribas**. Realiza siempre un merge inteligente: agrega las entradas nuevas y actualiza las que hayan cambiado.

# Validación de Estado Antes de Archivar
- Antes de archivar cualquier propuesta, historia o tarea, verifica que el `**Estado:**` en `proposal.md` sea `✅ Completada`. Si quedan elementos sin completar, advertir al usuario antes de proceder.

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