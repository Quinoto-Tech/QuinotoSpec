---
description: Propone el sprint óptimo basado en el estado actual del proyecto, prioridades y estimaciones
---

Este workflow analiza el estado del proyecto y genera una propuesta de Sprint Plan para el equipo.

**Instrucciones:**

1. **Lectura del estado actual**:
    - Lee `PROJECT_STATUS.md` si existe.
    - Escanea `.quinoto-spec/proposals/` para identificar todas las propuestas activas y su porcentaje de completitud.
    - Para cada propuesta activa, lista las historias de usuario pendientes y sus tareas asociadas con prioridad y estimación.

2. **Capacidad del sprint**:
    - Si el usuario no especifica capacidad, asumir un sprint de **2 semanas** con capacidad de **40 puntos** (tallas: XS=1, S=2, M=3, L=5, XL=8).
    - Si el usuario especifica capacidad, usarla.

3. **Selección de ítems para el sprint**:
    - Prioriza en este orden:
        1. Tareas P1 de propuestas en estado 🟢 (En Curso).
        2. Tareas P1 de propuestas en estado 🟡 (Propuesta).
        3. Tareas P2 si queda capacidad.
    - Respeta las **Dependencias** declaradas en los archivos de tareas: no incluir una tarea si su dependencia no está completada o en el mismo sprint.
    - No exceder la capacidad total del sprint.

4. **Generación del Sprint Plan**:
    Genera el archivo `.quinoto-spec/sprint-plan.md` con el siguiente formato:

    ```markdown
    # 🏃 Sprint Plan — [Fecha inicio] al [Fecha fin]

    **Capacidad total:** [N] puntos
    **Puntos comprometidos:** [N] puntos

    ## 📋 Ítems del Sprint

    | ID | Historia | Tarea | Tipo | Estimación | Puntos | Propuesta |
    | --- | --- | --- | --- | --- | --- | --- |
    | TSK-XXX-001 | US-XXX-001 | [Título] | Backend | M | 3 | [slug] |

    ## 🎯 Objetivo del Sprint
    [Descripción en 1-2 oraciones de qué se espera lograr al finalizar el sprint]

    ## ⚠️ Riesgos Identificados
    - [Riesgo 1 y mitigación sugerida]
    ```

5. **Recomendación de objetivo del sprint**:
    - Deriva el objetivo de las historias de usuario seleccionadas: ¿Qué valor entrega el equipo al usuario al finalizar?

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez generado el sprint plan, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Sprint Plan Generated
- **Resumen**: Se generó el plan de sprint en `.quinoto-spec/sprint-plan.md` con [N] tareas y capacidad de [N] puntos.
