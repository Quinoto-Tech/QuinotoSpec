---
name: Quinotospec Metrics
description: Calcula y reporta métricas de compliance y productividad del proyecto QuinotoSpec.
---

# Skill: Quinotospec Metrics

Calcula métricas de compliance del equipo respecto a las reglas de QuinotoSpec. Útil para retrospectives y mejorar la adopción.

## Métricas Calculadas

### 1. Changelog Compliance

- **Métrica**: ¿Cuántas tareas tienen entrada en el changelog?
- **Cálculo**: (Entradas de changelog / Total de tareas completadas) * 100
- **Target**: > 90%

### 2. Prefix Registry Usage

- **Métrica**: ¿Todas las propuestas tienen prefijo registrado?
- **Cálculo**: (Propuestas con prefijo / Total propuestas) * 100
- **Target**: 100%

### 3. Product Agreement Adoption

- **Métrica**: ¿Cuántas propuestas tienen DoR/DoD definidos?
- **Cálculo**: (Propuestas con Product Agreement / Total propuestas) * 100
- **Target**: 100%

### 4. Branch Naming Compliance

- **Métrica**: ¿Cuántos branches siguen la convención?
- **Cálculo**: (Branches correctos / Total branches) * 100
- **Target**: > 95%

### 5. Archive Convention Compliance

- **Métrica**: ¿Los archivos archivados usan `_archived/` no `__`?
- **Cálculo**: Archivos en `_archived/` / Archivos con prefijo `__` * 100
- **Target**: 100%

### 6. Task Completion Rate

- **Métrica**: ¿Cuántas tareas iniciadas se completan?
- **Cálculo**: (Tareas completadas / Tareas iniciadas) * 100
- **Target**: > 80%

### 7. Discovery Freshness

- **Métrica**: ¿Cuántos archivos de discovery tienen < 30 días?
- **Cálculo**: (Discovery recientes / Total discovery files) * 100
- **Target**: > 70%

## Output

Retorna JSON con:

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "metrics": {
    "changelog_compliance": { "value": 85, "target": 90, "status": "warning" },
    "prefix_registry_usage": { "value": 100, "target": 100, "status": "ok" },
    "product_agreement_adoption": { "value": 100, "target": 100, "status": "ok" },
    "branch_naming_compliance": { "value": 92, "target": 95, "status": "warning" },
    "archive_convention_compliance": { "value": 100, "target": 100, "status": "ok" },
    "task_completion_rate": { "value": 78, "target": 80, "status": "warning" },
    "discovery_freshness": { "value": 60, "target": 70, "status": "critical" }
  },
  "overall_score": 87,
  "recommendations": [
    "Actualizar discovery - freshness < 70%",
    "Mejorar task completion rate - está en 78%"
  ]
}
```

## Uso

```
/metrics --period month --format json
/metrics --dashboard
```
