---
trigger: always_on
---

# Gestión del Changelog
- **NUNCA** edites `docs/quinoto-spec-changelog.md` manualmente.
- **SIEMPRE** usa la skill `quinotospec-update-changelog` para registrar cambios después de completar un workflow o tarea importante.

# Gestión de Prefijos e IDs
- Al crear propuestas, tareas o historias de usuario, adhiérete **ESTRICTAMENTE** a los prefijos definidos en `.quinoto-spec/prefix-registry.md`.
- Nunca inventes un prefijo sin registrarlo primero en esa tabla.

## 3. Product Agreement Check (BLOQUEANTE)
- **ANTES** de ejecutar cualquier workflow de creación de propuestas (ej. `quinotospec.create-proposal`):
    - Verifica el archivo `.quinoto-spec/discovery/07-product-and-agreements.md`.
    - SI el archivo contiene solo los títulos/placeholders originales o está vacío -> **DETÉN LA EJECUCIÓN**.
    - **Notifica al usuario**: "No puedo crear la propuesta porque no se han definido los Acuerdos de Producto (DoR/DoD) en `.quinoto-spec/discovery/07-product-and-agreements.md`. Por favor complétalo primero."
- No ignores esta regla aunque el usuario insista, a menos que se use un override explícito.