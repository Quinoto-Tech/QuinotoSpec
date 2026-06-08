---
description: Genera una retrospectiva del proyecto analizando propuestas completadas, métricas de tiempo y patrones de trabajo. Identifica qué funcionó bien y qué mejorar del flujo QuinotoSpec.
---

Objetivo: aprender de las propuestas completadas para mejorar la adopción de la metodología, la precisión de estimaciones y la calidad del proceso.

## Precondiciones

- `.quinoto-spec/proposals/_archived/` debe contener al menos 1 propuesta archivada.
- `.quinoto-spec/quinoto-spec-changelog.md` debe tener entradas.
- Si no hay propuestas archivadas, el workflow muestra un mensaje y sugiere completar una propuesta primero.

---

### Paso 1 — Recolectar datos de propuestas completadas

1. Listar todas las carpetas en `.quinoto-spec/proposals/_archived/`.
2. Para cada propuesta archivada, leer `proposal.md` y extraer:
   - **Título**, **Prioridad**, **Complejidad**
   - **Servicios Afectados**
   - **Estado** (debe ser `✅ Completada` o `🔴 Archivada`)
3. Contar el total de propuestas completadas en el período.

### Paso 2 — Extraer métricas del changelog

1. Leer `.quinoto-spec/quinoto-spec-changelog.md`.
2. Para cada propuesta archivada, buscar sus entradas de changelog.
3. Extraer de cada entrada:
   - `**Tiempo Ahorrado**: ~{Tiempo Humano} (IA: {Tiempo IA} vs Humano: {Tiempo Humano})`
4. Calcular métricas agregadas:

| Métrica | Cálculo |
|---------|---------|
| Tiempo total ahorrado | Suma de todos los `Tiempo Humano` |
| Velocidad promedio | Tareas completadas / días del período |
| Precisión de estimaciones | % de tareas donde estimado ≈ real |
| Propuestas por mes | Conteo absoluto |

### Paso 3 — Identificar patrones

1. **Archivos más modificados**: agrupar por archivo, contar frecuencia.
2. **Servicios más impactados**: agrupar por servicio, contar frecuencia.
3. **Tipos de cambio más frecuentes**: feature vs bugfix vs refactor.
4. **Tareas con rollback**: buscar entradas de changelog que mencionen "rollback" o "revertir".
5. **Tareas con mayor tiempo ahorrado**: top 3 por `Tiempo Humano`.

### Paso 4 — Solicitar input cualitativo (opcional)

Si NO se usa `--quick`, hacer 3 preguntas al usuario:

1. *"¿Qué funcionó bien en este ciclo?"*
2. *"¿Qué mejorarías del flujo de trabajo QuinotoSpec?"*
3. *"¿Qué obstáculos encontraste?"*

### Paso 5 — Generar documento de retrospectiva

Crear `.quinoto-spec/retrospective-{{YYYY-MM-DD}}.md` con la siguiente estructura:

```markdown
# Retrospectiva — {{YYYY-MM-DD}}

## 📊 Métricas del Período

| Métrica | Valor |
|---------|-------|
| Propuestas completadas | {{N}} |
| Tiempo total ahorrado por IA | {{TOTAL}} |
| Velocidad promedio (tareas/semana) | {{VEL}} |
| Precisión de estimaciones | {{PREC}}% |

## ✅ Qué Funcionó Bien

{{INPUT_USUARIO}}

## 🔧 Qué Mejorar

{{INPUT_USUARIO}}

## 🚧 Obstáculos

{{INPUT_USUARIO}}

## 📈 Patrones Detectados

### Archivos más modificados
| Archivo | Frecuencia |
|---------|------------|

### Servicios más impactados
| Servicio | Frecuencia |
|----------|------------|

### Tipos de cambio
| Tipo | Cantidad |
|------|----------|

### Top 3 — Mayor tiempo ahorrado
| Propuesta | Tiempo Humano | Tiempo IA |
|-----------|--------------|-----------|

## 🎯 Action Items

- [ ] Acción 1
- [ ] Acción 2
- [ ] Acción 3
```

### Paso 6 — Sugerir action items

Basado en los patrones detectados, sugerir 3-5 acciones concretas. Ejemplos:
- "El servicio `auth-service` fue modificado en el 60% de las propuestas → considerar refactor preventivo."
- "La estimación fue inexacta en el 40% de los casos → revisar criterios de `quinotospec-estimate`."
- "3 tareas requirieron rollback → reforzar tests pre-merge."

### Paso 7 — Changelog (OBLIGATORIO)

Ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Retrospective Generated: {{YYYY-MM-DD}}
- **Resumen**: Se generó retrospectiva con {{N}} propuestas analizadas. Tiempo total ahorrado: {{TOTAL}}.

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--period 7d` | Últimos 7 días |
| `--period 30d` | Últimos 30 días |
| `--period sprint` | Desde el último sprint creado |
| `--quick` | Solo métricas, sin input cualitativo del usuario |

## Ejemplos

```
@quinotospec.retrospective
@quinotospec.retrospective --period 30d
@quinotospec.retrospective --quick
```
