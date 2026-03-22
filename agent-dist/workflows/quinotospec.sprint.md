---
description: Propone el sprint óptimo basado en el estado actual del proyecto, prioridades y estimaciones
---

Este workflow analiza el estado del proyecto y genera una propuesta de Sprint Plan para el equipo.

---

## Paso 1 — Configuración del Sprint (YAML)

Este workflow utiliza dos niveles de configuración:

### A. Configuración Base (`.quinoto-spec/sprints/base-config.yml`)

1. Verifica si existe el archivo `.quinoto-spec/sprints/base-config.yml`.
2. **SI EL ARCHIVO NO EXISTE**:
   - Créalo con el esquema de referencia (valores en `null` o vacíos).
   - **DETÉN LA EJECUCIÓN INMEDIATAMENTE**.
   - **Notifica al usuario**: "Se ha creado el archivo de configuración base `.quinoto-spec/sprints/base-config.yml`. Por favor, complétalo con la definición del equipo y sus capacidades antes de intentar ejecutar este workflow de nuevo."
3. **SI EL ARCHIVO EXISTE PERO TIENE VALORES EN `null` O VACÍOS** (ej: `equipo` vacío o `velocidad_promedio_puntos` es `null`):
   - **DETÉN LA EJECUCIÓN INMEDIATAMENTE**.
   - **Notifica al usuario**: "El archivo `.quinoto-spec/sprints/base-config.yml` contiene valores incompletos. Por favor, asegúrate de definir al menos un integrante del equipo y la velocidad promedio antes de continuar."
4. **SI EL ARCHIVO TIENE DATOS VÁLIDOS**: Procede al siguiente paso.

**Esquema de referencia para `base-config.yml`**:
```yaml
# Capacidad del equipo (Base)
equipo:
  - nombre: ""
    rol: ""          # Backend | Frontend | FullStack | DevOps | QA
    disponibilidad: 1.0
    componentes_permitidos: []  # ej: ["api", "ui"]
    componente_owner: ""        # Prioridad de asignación

# Conversión de tallas a puntos
puntos_por_talla:
  XS: 1
  S: 2
  M: 3
  L: 5
  XL: 8

velocidad_promedio_puntos: null
```

### B. Configuración del Sprint (`.quinoto-spec/sprints/sprint-{{ID}}/sprint-config.yml`)
Solicita al usuario el **ID del Sprint** (ej: `1`) y el **Nombre del Sprint** (ej: `Integración Rapiboy`). Verifica si existe la carpeta y el archivo. Si NO existe, créalo:

```yaml
# Detalles del Sprint específico
id_sprint: {{ID}}
nombre_sprint: "{{NOMBRE}}"
duracion_semanas: 2
fecha_inicio: YYYY-MM-DD

# Prioridad de propuestas (slugs en orden de importancia)
prioridad_propuestas:
  - ""
```

---

## Paso 2 — Cálculo de capacidad real

Con base en la unión de `base-config.yml` y el `sprint-config.yml` específico:

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

Genera el archivo `.quinoto-spec/sprints/sprint-{{id_sprint}}/sprint-plan.md` con el siguiente formato:

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

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez generado el sprint plan, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Sprint Plan Generated
- **Resumen**: Se generó el plan de sprint en `.quinoto-spec/sprints/sprint-{{id_sprint}}/sprint-plan.md` con [N] tareas, [N] puntos comprometidos de [N] disponibles. Equipo: [N] integrantes.
