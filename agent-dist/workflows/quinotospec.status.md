---
description: Genera un Panel de Control (Dashboard) del estado del proyecto
---

Este workflow genera un archivo `PROJECT_STATUS.md` en la raíz del proyecto que resume el progreso global, las métricas de valor y el estado de las iniciativas.

### Instrucciones de Ejecución:

1. **Análisis de Propuestas**:
    - Escanea el directorio `.quinoto-spec/proposals/`.
    - Identifica propuestas activas (🟡), en curso (🟢) y finalizadas/archivadas (✅).
    - Extrae prioridad y complejidad de cada `proposal.md`.

2. **Cálculo de Progreso**:
    - Para cada propuesta, busca archivos de tareas (`*_tasks.md`).
    - Calcula el porcentaje de completitud basado en los checkboxes `[x]` vs `[ ]`.

3. **Métricas de Valor**:
    - Lee `docs/quinoto-spec-changelog.md`.
    - Suma todos los valores de `Human Time` ahorrados para dar un total de "Valor Generado por IA".

4. **Generación del Dashboard**:
    - Crea o actualiza `PROJECT_STATUS.md` con:
        - # 📊 Dashboard de Proyecto: QuinotoSpec
        - ## 📈 Resumen Ejecutivo (Métricas de Valor Ahorrado)
        - ## 🗺️ Mapa de Ruta y Estado de Iniciativas (Tabla de Propuestas)
        - ## 🛠️ Salud de la Metodología (Discovery, Product Agreements)
        - ## 🕐 Actividad Reciente (Últimos 5 cambios del Changelog)

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez generado el dashboard, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Dashboard Updated
- **Resumen**: Se generó/actualizó el archivo `PROJECT_STATUS.md` con las métricas y estado actual del proyecto.
