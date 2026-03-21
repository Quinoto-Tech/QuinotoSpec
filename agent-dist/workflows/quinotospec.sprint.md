---
description: Propone el sprint óptimo basado en el estado actual del proyecto, prioridades y estimaciones
---

Este workflow analiza el estado del proyecto y genera una propuesta de Sprint Plan para el equipo.

---

## Paso 1 — Configuración del Sprint (YAML)

Verifica si existe el archivo `.quinoto-spec/sprint-config.yml`. 

- **Si NO existe**: créalo con el siguiente schema y solicita verificación humana antes de continuar:

```yaml
# Configuración del Sprint
duracion_semanas: 2
fecha_inicio: YYYY-MM-DD  # Fecha de inicio del sprint

# Capacidad del equipo
equipo:
  - nombre: ""
    rol: ""          # Backend | Frontend | FullStack | DevOps | QA
    disponibilidad: 1.0  # Factor de 0.0 a 1.0 (ej: 0.5 = medio tiempo)

# Conversión de tallas a puntos
puntos_por_talla:
  XS: 1
  S: 2
  M: 3
  L: 5
  XL: 8

# Velocidad histórica (opcional, para ajustar capacidad real)
velocidad_promedio_puntos: null  # Si se conoce, sobreescribe el cálculo por tallas
```

> **⚠️ Verificación humana requerida**: El usuario debe revisar y completar el `.quinoto-spec/sprint-config.yml` antes de que el agente continúe al Paso 2.

- **Si YA existe**: leerlo y usar sus valores para los cálculos.

---

## Paso 2 — Cálculo de capacidad real

Con base en el `sprint-config.yml`:

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
    1. Tareas P1 de propuestas en estado 🟢 (En Curso).
    2. Tareas P1 de propuestas en estado 🟡 (Propuesta).
    3. Tareas P2 si queda capacidad.
- Respeta las **Dependencias** declaradas en los archivos de tareas.
- Al asignar tareas, considera el `rol` de cada integrante del equipo declarado en el YAML.
- No exceder la capacidad total calculada en el Paso 2.

---

## Paso 5 — Generación del Sprint Plan

Genera el archivo `.quinoto-spec/sprint-plan.md` con el siguiente formato:

```markdown
# 🏃 Sprint Plan — [Fecha inicio] al [Fecha fin]

**Equipo:** [N] integrantes | **Capacidad total:** [N] puntos | **Puntos comprometidos:** [N] puntos

## 📋 Ítems del Sprint

| ID | Historia | Tarea | Tipo | Estimación | Puntos | Asignado a | Propuesta |
| --- | --- | --- | --- | --- | --- | --- | --- |
| TSK-XXX-001 | US-XXX-001 | [Título] | Backend | M | 3 | [nombre] | [slug] |

## 🎯 Objetivo del Sprint
[Descripción en 1-2 oraciones de qué se espera lograr al finalizar el sprint]

## ⚠️ Riesgos Identificados
- [Riesgo 1 y mitigación sugerida]
```

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez generado el sprint plan, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Sprint Plan Generated
- **Resumen**: Se generó el plan de sprint en `.quinoto-spec/sprint-plan.md` con [N] tareas, [N] puntos comprometidos de [N] disponibles. Equipo: [N] integrantes.
