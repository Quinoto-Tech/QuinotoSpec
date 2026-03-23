---
description: Orchestrates the complete sprint planning workflow
---

Este workflow orquesta el proceso completo de planificación de sprints.

**Parámetros Requeridos:**
- `SPRINT_ID`: Identificador del sprint (ej. `1`)
- `NOMBRE_SPRINT`: Nombre del sprint (ej. `Integración Rapiboy`)

---

## Flujo de Ejecución

### Paso 1 — Inicializar configuración de sprints
Ejecuta `@quinotospec.sprints.init` para verificar/crear la configuración base del equipo.

### Paso 2 — Crear sprint
Ejecuta `@quinotospec.sprint.create` con los parámetros `SPRINT_ID` y `NOMBRE_SPRINT` para crear la estructura y configuración del sprint.

### Paso 3 — Planificar sprint
Ejecuta `@quinotospec.sprint.plan` con el parámetro `SPRINT_ID` para generar el plan de tareas del sprint.

---

## Distribución (Opcional)

Si el sprint incluye propuestas multi-servicio, usar `@quinotospec.distribute` para distribuir las propuestas, historias de usuario y tareas a cada sub-proyecto correspondiente.
