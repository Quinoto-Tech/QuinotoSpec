---
description: Genera el plan de sprint óptimo basado en el estado actual, prioridades y estimaciones
---

Este workflow analiza el estado del proyecto y genera una propuesta de Sprint Plan para el equipo.

**Parámetros Requeridos:**
- `SPRINT_ID`: Identificador del sprint (ej. `1`)

---

## Paso 1 — Validar configuración

1. Verifica que exista `.quinoto-spec/sprints/base-config.yml`. Si no existe → ejecuta `@quinotospec.sprints.init`.
2. Verifica que exista `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-config.yml`. Si no existe → ejecuta `@quinotospec.sprint.create`.
3. Lee ambos archivos de configuración.

---

## Paso 2 — Cálculo de capacidad real

Con base en la unión de `base-config.yml` y `sprint-config.yml`:

1. Calcula la capacidad total del sprint:
   - Si `velocidad_promedio_puntos` tiene valor → usarlo directamente.
   - Si no → calcular: `sum(disponibilidad de cada miembro) × días hábiles del sprint × factor de carga` (asumir ~5 puntos/día por desarrollador a tiempo completo).
2. Reporta: *"Capacidad calculada: [N] puntos para [N] semanas con [N] integrantes."*

---

## Paso 3 — Lectura del estado actual

- Lee `PROJECT_STATUS.md` si existe.
- Escanea `.quinoto-spec/proposals/` para identificar todas las propuestas activas y su porcentaje de completitud.
- Para cada propuesta activa, lista las historias de usuario pendientes y sus tareas con prioridad y estimación.

---

## Paso 4 — Selección de ítems para el sprint

- Prioriza en este orden:
    1. Tareas de propuestas listadas en `prioridad_propuestas` (en el orden especificado).
    2. Tareas P1 de propuestas en estado 🟢 (En Curso) no listadas arriba.
    3. Tareas P1 de propuestas en estado 🟡 (Propuesta) no listadas arriba.
    4. Tareas P2 si queda capacidad.
- Respeta las **Dependencias** declaradas en los archivos de tareas.
- Al asignar tareas, considera el `rol`, `componentes_permitidos` y `componente_owner` de cada integrante del equipo.
- No exceder la capacidad total calculada en el Paso 2.

---

## Paso 5 — Generación del Sprint Plan

Genera el archivo `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-plan.md` con el siguiente formato:

```markdown
# 🏃 Sprint Plan — {{id_sprint}}: {{nombre_sprint}} ([Fecha inicio] al [Fecha fin])

**Equipo:** [N] integrantes | **Capacidad total:** [N] puntos | **Puntos comprometidos:** [N] puntos

## 📋 Ítems del Sprint

| ID | Historia | Tarea | Tipo | Componente | Estimación | Puntos | Asignado a | Propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| TSK-XXX-001 | US-XXX-001 | [Título] | Backend | [nombre_componente] | M | 3 | [nombre] | [slug] |

## 🎯 Objetivo del Sprint
[Descripción en 1-2 oraciones de qué se espera lograr al finalizar el sprint]

## ⚠️ Riesgos Identificados
- [Riesgo 1 y mitigación sugerida]
```

---

## Paso 6 — Actualizar Changelog

Una vez generado el sprint plan, DEBES ejecutar la skill `quinotospec-update-changelog`.

- **Título de la Acción**: Sprint Plan Generated
- **Resumen**: Se generó el plan de sprint en `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-plan.md` con [N] tareas, [N] puntos comprometidos de [N] disponibles. Equipo: [N] integrantes.

---

**Próximo paso (opcional):** Si hay propuestas multi-servicio, usar `@quinotospec.distribute` para distribuirlas a los sub-proyectos correspondientes.
