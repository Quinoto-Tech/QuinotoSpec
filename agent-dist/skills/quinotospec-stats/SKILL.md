---
name: quinotospec-stats
description: Genera estadisticas y metricas de productividad del proyecto QuinotoSpec, incluyendo tareas completadas, tiempo promedio y tendencias.
---

# Skill: quinotospec-stats

Genera reportes estadisticos sobre el uso de QuinotoSpec en el proyecto. Util para retrospectives, metricas de equipo y seguimiento de productividad.

## Instrucciones de Ejecucion

### Paso 1 - Recopilar Datos
Lee los siguientes archivos para extraer metricas:
1. `.quinoto-spec/quinoto-spec-changelog.md` - Historial de acciones
2. `.quinoto-spec/proposals/*/proposal.md` - Propuestas y sus estados
3. `.quinoto-spec/proposals/*/*_tasks.md` - Tareas y su completion status
4. `.quinoto-spec/proposals/*/user-stories.md` - User stories
5. `.quinoto-spec/prefix-registry.md` - Prefijos registrados

### Paso 2 - Calcular Metricas
Calcula las siguientes metricas:

**Metricas de Propuestas:**
- Total de propuestas (activas, completadas, archivadas)
- Tiempo promedio de completion (desde creacion hasta completada)
- Propuestas por mes (tendencia)

**Metricas de Tareas:**
- Total de tareas (pendientes, en progreso, completadas)
- Tasa de completion (% de tareas completadas vs total)
- Tareas completadas por semana
- Tiempo promedio por tarea

**Metricas de User Stories:**
- Total de user stories
- Stories completadas vs pendientes
- Promedio de tareas por story

**Metricas de Actividad:**
- Acciones registradas en changelog (por tipo)
- Dia/semana con mas actividad
- Racha de actividad actual (dias consecutivos)

### Paso 3 - Generar Reporte
Formatea el reporte segun el modo solicitado:
- **Modo summary**: Vista rapida con metricas clave
- **Modo full**: Reporte completo con todas las metricas
- **Modo json**: Output en JSON para integracion con herramientas externas

## Ejemplos

### Resumen Rapido
```
/quinotospec-stats
```

### Reporte Completo
```
/quinotospec-stats --mode full
```

### Metricas de un Periodo
```
/quinotospec-stats --since 2026-01-01 --until 2026-03-31
```

### Output JSON
```
/quinotospec-stats --output json
```

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--mode` | Modo de reporte (summary, full) | No | summary |
| `--since` | Fecha inicio (YYYY-MM-DD) | No | N/A |
| `--until` | Fecha fin (YYYY-MM-DD) | No | N/A |
| `--output` | Formato (text, json) | No | text |
| `--proposal` | Filtrar por slug de propuesta | No | N/A |

## Formato de Reporte (Summary)

```
╔══════════════════════════════════════════╗
║   QuinotoSpec Stats - Summary            ║
╠══════════════════════════════════════════╣
║  Propuestas:  12 (8 completadas, 4 activas) ║
║  Tareas:      87 (72 completadas, 83%)   ║
║  Stories:     24 (20 completadas)         ║
║  Actividad:   156 acciones en changelog   ║
║  Racha:       5 dias consecutivos         ║
║  Avg/task:    ~15 min                     ║
╚══════════════════════════════════════════╝
```

## Notas Importantes

- Si no hay datos suficientes, reporta metricas como "N/A"
- Las metricas de tiempo se calculan desde timestamps en el changelog
- El modo json es compatible con herramientas de BI externas
- Ejecuta `quinotospec-update-changelog` despues de generar el reporte
