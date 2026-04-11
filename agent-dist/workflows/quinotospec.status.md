---
description: Genera un Panel de Control (Dashboard) del estado del proyecto
---

Este workflow genera un archivo `PROJECT_STATUS.md` en la raíz del proyecto que resume el progreso global, las métricas de valor y el estado de las iniciativas.

### Instrucciones de Ejecución:

1. **Análisis de Propuestas**:
    - Escanea el directorio `.quinoto-spec/proposals/` (activas) y `.quinoto-spec/proposals/_archived/` (archivadas).
    - Clasifica propuestas activas: 🟡 Propuesta, 🟢 En Curso, ✅ Completada.
    - Extrae prioridad y complejidad de cada `proposal.md`.
    - Registra el conteo total: activas vs archivadas.
    - Lee `**Discovery Date:**` en `.quinoto-spec/discovery/00-stack-profile.md`. Si han pasado más de 30 días desde esa fecha → marcarlo como alerta en la sección `🚨 Alertas y Bloqueos` con el mensaje: *"⏰ El discovery tiene [N] días de antigüedad. Considera ejecutar `@quinotospec.refresh-discovery`."*

2. **Cálculo de Progreso y Velocidad**:
    - Para cada propuesta activa, busca archivos de tareas (`*_tasks.md`).
    - Calcula el porcentaje de completitud basado en los checkboxes `[x]` vs `[ ]`.
    - Lee `.quinoto-spec/quinoto-spec-changelog.md` para estimar la velocidad del equipo: cuántas tareas se completaron en los últimos 7 días y en los últimos 30 días.

3. **Métricas de Valor**:
    - Lee `.quinoto-spec/quinoto-spec-changelog.md`.
    - Suma todos los valores de `Human Time` ahorrados para dar un total de "Valor Generado por IA". Si el campo no existe en alguna entrada, registrar `N/D` y continuar sin interrumpir el proceso.

4. **Alertas y Bloqueos**:
    - Identifica propuestas activas sin cambios en el changelog en los últimos 14 días.
    - Detecta historias con todas sus tareas pendientes (`[ ]`) sin ningún progreso.
    - Detecta conflictos de propuestas registrados con `⚠️ Conflictos Detectados:`.

5. **Salud de la Metodología**:
    - Verifica la existencia y contenido de los siguientes artefactos:
        - ✅/❌ `.quinoto-spec/discovery/` existe y tiene los 8 archivos esperados.
        - ✅/❌ `07-product-and-agreements.md` tiene contenido más allá de los encabezados.
        - ✅/❌ `.quinoto-spec/prefix-registry.md` está actualizado y sin duplicados.

6. **Próximos Pasos Sugeridos** (Blood-Bond):
    - Invocar skill `quinotospec-blood-bond-analyzer --force`
    - Invocar skill `quinotospec-blood-bond-predictor --force`
    - Leer `.quinoto-spec/blood-bond/suggestions.md` y mostrar las sugerencias en la sección `⏭️ Próximos Pasos Sugeridos`
    - Si `suggestions.md` no existe o proyecto está en cold start (< 5 entradas en changelog): fallback a предложения basadas en prioridad P1 y menor completitud

7. **Generación del Dashboard**:
    - Crea o actualiza `PROJECT_STATUS.md` con las siguientes secciones en orden:
        - `# 📊 Dashboard de Proyecto`
        - `## 📈 Resumen Ejecutivo` (Métricas de Valor Ahorrado + velocidad)
        - `## 🗺️ Mapa de Ruta y Estado de Iniciativas` (Tabla de Propuestas activas + contador de archivadas)
        - `## 🚨 Alertas y Bloqueos` (propuestas estancadas, conflictos detectados)
        - `## 🛠️ Salud de la Metodología` (checks explícitos con ✅/❌)
        - `## 🕐 Actividad Reciente` (Últimos 5 cambios del Changelog)
        - `## ⏭️ Próximos Pasos Sugeridos` (Top 3 acciones recomendadas)

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez generado el dashboard, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Dashboard Updated
- **Resumen**: Se generó/actualizó el archivo `PROJECT_STATUS.md` con las métricas y estado actual del proyecto.
