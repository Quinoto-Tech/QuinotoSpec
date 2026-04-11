---
name: Quinotospec Blood-Bond Monitor
description: Detecta inactividad y activa Blood-Bond proactivamente
---

# Skill: Quinotospec Blood-Bond Monitor

Monitorea la actividad del proyecto y detecta when el usuario needs a proaktif suggestion.

## Responsabilidad

1. **Detectar inactividad**: Si han pasado >=14 días desde última entrada en changelog
2. **Generar recordatorio pasivo**: Mostrar sugerencias sin interrumpir el flujo
3. **No molestar**: Si hay actividad reciente, no mostrar nada

## Algoritmo de Monitoreo

### Paso 1 — Verificar Changelog
1. Lee `.quinoto-spec/quinoto-spec-changelog.md`
2. Extrae la fecha de la úlima entrada (formato `## [Fecha: YYYY-MM-DD]`)
3. Calcula días desde última actividad

### Paso 2 — Evaluar Inactividad
```
SI: días_desde_ultima_actividad >= 14
ENTONCES: inactivo = true
SI: días_desde_ultima_actividad >= 7 Y días_desde_ultima_actividad < 14
ENTONCES: warning = true
SI: días_desde_ultima_actividad < 7
ENTONCES: activo = true
```

### Paso 3 — Acciones según Estado

#### Estado: Inactivo (>=14 días)
1. Ejecutar `quinotospec-blood-bond-analyzer --force`
2. Ejecutar `quinotospec-blood-bond-predictor --force`
3. Mostrar recordatorio pasivo:

```
🩸 **Blood-Bond: Hey!** Hace {N} días que no hay actividad en el proyecto.

Propuesta más reciente: {nombre}
¿Querés que te sugiera qué hacer接下来?

{display 3 suggestions}
```

#### Estado: Warning (7-13 días)
- No mostrar nada automáticamente
- Solo registrar en logs internos

#### Estado: Activo (<7 días)
- No hacer nada

## Integración con Apply

Esta skill debe invocarse:
1. **Después de `@quinotospec.apply`** - post-completion check
2. **Después de cualquier workflow que modifique estado**

## Output

Si está inactivo, genera `.quinoto-spec/blood-bond/reminder.md` con el mensaje formateado.

## Flags

| Flag | Descripción |
|------|-------------|
| `--check-only` | Solo verificar estado sin mostrar recordatorio |
| `--force` | Forzar recordatorio aunque esté activo |
| `--days` | Configurar umbral de inactividad (default: 14) |

## Ejemplo de Output (check-only)

```json
{
  "status": "inactive",
  "days_since_activity": 18,
  "last_proposal": "legacy-auth-refactor",
  "last_task": "TSK-AUTH-005",
  "should_remind": true
}
```
