---
name: Quinotospec Blood-Bond Analyzer
description: Analiza patrones históricos del desarrollador para Blood-Bond
---

# Skill: Quinotospec Blood-Bond Analyzer

Recolecta y procesa datos históricos del proyecto para extraer patrones de trabajo del desarrollador.

## Fuentes de Datos

Lee los siguientes archivos para construir el análisis:

| Fuente | Ubicación |
|--------|-----------|
| Changelog | `.quinoto-spec/quinoto-spec-changelog.md` |
| Prefix Registry | `.quinoto-spec/prefix-registry.md` |
| Proposals | `.quinoto-spec/proposals/*/proposal.md` |
| User Stories | `.quinoto-spec/proposals/*/user-histories.md` |
| Tasks | `.quinoto-spec/proposals/*/*_tasks.md` |
| Discovery | `.quinoto-spec/discovery/00-stack-profile.md` |

## Patrones a Detectar

### 1. PATRON TEMPORAL
- Día de semana más activo
- Hora del día (si disponible)
- Frecuencia de trabajo (diario, semanal, sprint-based)
- Días desde última actividad

### 2. PATRON DE CATEGORÍA
- Top prefixes más usados (AUTH, API, DB, etc.)
- Distribución porcentual de trabajo por área
- Tasa de context switch

### 3. PATRON SECUENCIAL
- Secuencias comunes de prefixes (ej: AUTH → REWA → INTE)
- Dependencias detectadas entre áreas
- Orden natural de implementación

### 4. PATRON DE PROGRESO
- Tareas completadas por sesión (velocidad)
- Propuestas estancadas (>14 días sin avance)
- Historias con trabajo iniciado pero incompleto
- Tiempo promedio de completitud de tarea

### 5. PATRON DE SPRINT
- Duración típica de sprints
- Ritmo de completitud
- Capacidad estimada (tasks por sprint)

## Algoritmo de Análisis

### Paso 1 — Recolección de Changelog
1. Lee `.quinoto-spec/quinoto-spec-changelog.md`
2. Parsea entradas con formato `## [Fecha: YYYY-MM-DD]`
3. Extrae: fecha, título, IDs de tareas mencionadas
4. Calcula días desde última actividad

### Paso 2 — Análisis de Prefix
1. Lee `.quinoto-spec/prefix-registry.md`
2. Cuenta frecuencia de cada prefijo usado
3. Ordena por frecuencia descendente

### Paso 3 — Detección de Secuencias
1. Para cada entrada del changelog, extrae el prefijo del TASK_ID (ej: TSK-AUTH-001 → AUTH)
2. Construye secuencias de 2-3 prefixes consecutivos
3. Detecta si hay patrones repetidos

### Paso 4 — Análisis de Progreso
1. Escanea archivos de tareas para contar:
   - Total tasks
   - Tasks completadas (`[x]`)
   - Tasks pendientes (`[ ]`)
2. Calcula porcentaje de completitud por propuesta
3. Identifica propuestas sin avance reciente

### Paso 5 — Validación de Cold Start
- Si changelog tiene menos de 5 entradas → modo cold start
- Genera `cold_start: true` en output

## Output

Genera `.quinoto-spec/blood-bond/analysis.json`:

```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SSZ",
  "cold_start": false,
  "days_since_last_activity": 3,
  "temporal_pattern": {
    "most_active_day": "martes",
    "typical_session_duration": "2-3 horas",
    "work_frequency": "semanal"
  },
  "category_pattern": {
    "top_prefixes": ["AUTH", "API", "DB"],
    "distribution": { "AUTH": 45, "API": 30, "DB": 15, "OTHER": 10 },
    "context_switch_rate": "bajo"
  },
  "sequential_pattern": {
    "common_sequences": [["AUTH", "REWA"], ["API", "INTE"]],
    "detected_dependencies": { "AUTH": ["REWA"] }
  },
  "progress_pattern": {
    "avg_tasks_per_session": 3,
    "total_tasks": 45,
    "completed_tasks": 30,
    "pending_tasks": 15,
    "completion_rate": 67,
    "stagnant_proposals": ["legacy-auth"],
    "in_progress_us": ["US-AUTH-01"]
  },
  "sprint_pattern": {
    "typical_duration_weeks": 2,
    "capacity_tasks_per_sprint": 15,
    "current_velocity": "alta"
  }
}
```

## Manejo de Errores

- Si `.quinoto-spec/` no existe → crear directorio
- Si changelog está vacío → cold_start: true
- Si no hay prefix registry → usar solo prefijos inferidos de TASK_IDs

## Flags

| Flag | Descripción |
|------|-------------|
| `--force` | Forzar re-análisis incluso si analysis.json existe |
| `--output` | Path custom para output (default: `.quinoto-spec/blood-bond/analysis.json`) |
