---
name: Quinotospec Blood-Bond Predictor
description: Genera predicciones proactivas basándose en análisis de Blood-Bond
---

# Skill: Quinotospec Blood-Bond Predictor

Genera sugerencias accionables basándose en los patrones detectados por blood-bond-analyzer.

## Input

Lee `.quinoto-spec/blood-bond/analysis.json` generado por blood-bond-analyzer.

## Algoritmo de Predicción

### REGLA 1: Siguiente en Secuencia
```
SI: El usuario completó tareas de prefijo X recientemente
Y: La secuencia X → Y es común en el historial
Y: Hay tareas pendientes de prefijo Y
ENTONCES: Sugerir continuar con Y
```

### REGLA 2: Área Caliente (Hot Path)
```
SI: >40% del trabajo reciente es en área X
Y: Hay tareas pendientes en área X
ENTONCES: Sugerir continuar en X (evitar context switch)
```

### REGLA 3: Desbloqueo
```
SI: US-A está bloqueando US-B (detectado por dependencias)
Y: US-A se completó
ENTONCES: Sugerir US-B inmediatamente
```

### REGLA 4: Estancamiento (Stagnation Alert)
```
SI: Propuesta X no tiene avance en >=14 días
ENTONCES: Alertar y sugerir acción
```

### REGLA 5: Prioridad + Velocidad
```
SI: Hay tareas P1 pendientes
Y: Velocidad actual es alta
ENTONCES: Sugerir continuar con P1

SI: Hay tareas P2 pendientes
Y: Velocidad actual es baja
ENTONCES: Sugerir dividir en tasks más pequeñas
```

## Generación de Sugerencias

### Paso 1 — Calcular Confianza
Para cada sugerencia, calcular confianza basada en:
- Frecuencia del patrón en historial (más repeticiones = más confianza)
- Consistencia del comportamiento
- Tiempo desde última sugerencia similar

Escala: Alta (>75%), Media (50-75%), Baja (<50%)

### Paso 2 — Ordenar Sugerencias
1. Estancamiento alerts (crítico)
2. Desbloqueo signals (alta urgencia)
3. Hot path continuations (alta confianza)
4. Sequence predictions (media confianza)

### Paso 3 — Limitar a 3
Máximo 3 sugerencias para no abrumar.

### Paso 4 — Generar Acciones
Para cada sugerencia, generar:
- Título descriptivo
- Razón de la sugerencia
- Comando sugerido listo para ejecutar
- Confianza (1-3 barras)

## Output

Genera `.quinoto-spec/blood-bond/suggestions.md`:

```markdown
# 🩸 Blood-Bond: Sugerencias Proactivas

**Generado**: YYYY-MM-DD HH:MM
**Última actividad**: hace N días

---

## 🔥 Sugerencias Inmediatas

### 1. [Titulo de la sugerencia] (Confianza: ████░░ Alta)

**Razón**: Explicación de por qué se sugiere esta acción

**Acción sugerida**: 
```
@quinotospec.apply TSK-XXX-001
```

---

## ⚠️ Alertas

### 🚨 Estancamiento Detectado
**Propuesta**: `nombre-de-propuesta`
- Sin avance en **N días**
- N% completada
- **Recomendación**: Completar o archivar

---

## 📊 Tu Perfil de Trabajo

| Métrica | Valor |
|---------|-------|
| Última actividad | hace N días |
| Área principal | XXX |
| Velocidad típica | N tasks/sesión |
| Context switch | Bajo/Medio/Alto |
| Total completado | N tasks |

---

## 🧠 Insights

- **Patrón**: Breve descripción del patrón detectado
- **Recomendación**: Consejo basado en el patrón

---

*💡 Blood-Bond analiza tu historial para predecir qué necesitas接下来.*
*Para re-generar: `@quinotospec.blood-bond --suggest`*
```

## Cold Start

Si `analysis.json` tiene `cold_start: true`:
- Generar sugerencias limitadas (solo básicas)
- Advertir que se necesitan más datos para predicciones precisas

## Flags

| Flag | Descripción |
|------|-------------|
| `--force` | Forzar re-generación |
| `--limit` | Limitar a N sugerencias (default: 3) |
