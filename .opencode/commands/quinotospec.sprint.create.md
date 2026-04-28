---
description: Crea la estructura de un nuevo sprint con configuración vacía
---

Este workflow crea un nuevo sprint con su configuración inicial.

**Parámetros Requeridos:**
- `SPRINT_ID`: Identificador del sprint (ej. `1`)
- `NOMBRE_SPRINT`: Nombre del sprint (ej. `Integración Rapiboy`)

---

## Paso 1 — Crear estructura de carpetas

1. Verifica si existe `.quinoto-spec/sprints/`. Si no existe, ejecuta `@quinotospec.sprints.init` primero.
2. Crea la carpeta `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/`.
3. Crea la subcarpeta `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/proposals/`.

---

## Paso 2 — Crear configuración del sprint

Verifica si existe `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-config.yml`:

### A. Si el archivo NO existe:
- Créalo con el esquema de referencia.

```yaml
# Detalles del Sprint específico
id_sprint: {{SPRINT_ID}}
nombre_sprint: "{{NOMBRE_SPRINT}}"
duracion_semanas: 2
fecha_inicio: YYYY-MM-DD

# Prioridad de propuestas (slugs en orden de importancia)
prioridad_propuestas:
  - ""
```

- Notifica al usuario: "Se ha creado la estructura del Sprint {{SPRINT_ID}}: '{{NOMBRE_SPRINT}}'. Archivo de configuración: `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-config.yml`. Por favor, completa la información de fechas y prioridad de propuestas."

### B. Si el archivo ya existe:
- Notifica al usuario: "El Sprint {{SPRINT_ID}} ya existe. Archivo: `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-config.yml`"

---

**Próximo paso:** Usar `@quinotospec.sprint.plan` para planificar las tareas del sprint.
