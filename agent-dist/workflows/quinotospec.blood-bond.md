---
description: Analiza patrones de trabajo y predice siguientes acciones proactivamente
---

# Blood-Bond: Sistema de Predicción Proactiva

Blood-Bond analiza tu historial de trabajo y predice qué necesitas hacer接下来, sugiriendo proactivamente cuando detecta inactividad.

---

## Concepto

Blood-Bond forma un "vínculo de sangre" con tu patrón de trabajo:
- Aprende tus secuencias de trabajo (AUTH → REWA → INTE)
- Detecta tu velocidad y ritmo
- Predice qué viene después
- Te avisa proactivamente cuando llevas mucho sin actividad

---

## Comandos

| Comando | Descripción |
|---------|-------------|
| `@quinotospec.blood-bond` | Análisis completo + sugerencias |
| `@quinotospec.blood-bond --suggest` | Solo generar sugerencias |
| `@quinotospec.blood-bond --profile` | Solo mostrar tu perfil de trabajo |
| `@quinotospec.blood-bond --alerts` | Solo alertas de estancamiento |

---

## Flujo de Ejecución (--suggest)

### Paso 1 — Invocar Analyzer
Ejecutar skill `quinotospec-blood-bond-analyzer`:
- Lee changelog, prefix registry, proposals, tasks
- Genera `.quinoto-spec/blood-bond/analysis.json`

### Paso 2 — Invocar Predictor
Ejecutar skill `quinotospec-blood-bond-predictor`:
- Toma `analysis.json`
- Aplica reglas de predicción
- Genera `.quinoto-spec/blood-bond/suggestions.md`

### Paso 3 — Mostrar Resultados
Lee `suggestions.md` y presenta las sugerencias al usuario:

```
🩸 **Blood-Bond: Predicciones**

🔥 **Continuar con AUTH** (85% confianza)
Hace 60% de tu trabajo en AUTH. Tenés 3 tasks pendientes.
→ `@quinotospec.apply TSK-AUTH-003`

🔥 **Preparar REWA** (70% confianza)  
Secuencia típica: AUTH → REWA
→ Preparar contexto para reward system

⚠️ **Estancamiento**: `legacy-auth` sin avance en 18 días
```

### Paso 4 — Acciones Listas
Para cada sugerencia, ofrecer el comando listo:
- "Ejecutar: `@quinotospec.apply TSK-AUTH-003`"
- "Ejecutar: `@quinotospec.create-proposal reward-system`"

---

## Flujo de Ejecución (--profile)

Muestra solo estadísticas del perfil:
- Día más activo
- Área principal
- Velocidad típica
- Context switch rate
- Total completado

---

## Flujo de Ejecución (--alerts)

Solo muestra alertas de estancamiento:
- Propuestas sin avance en >=14 días
- Historias bloqueadas
- Tareas huérfanas

---

## Auto-Activación (Proactividad)

Blood-Bond se activa automáticamente cuando detecta inactividad:

1. **Trigger**: Cualquier comando `@quinotospec` ejecutado después de >=14 días de inactividad
2. **Acción**: Genera suggestions y muestra recordatorio pasivo
3. **Objetivo**: Recordar sin interrumpir

---

## Archivos Generados

```
.quinoto-spec/blood-bond/
├── analysis.json     # Datos crudos del análisis
├── suggestions.md    # Predicciones formateadas
└── reminder.md       # Mensaje de recordatorio (si inactivo)
```

---

## Cold Start

Si el proyecto tiene menos de 5 entradas en el changelog:
- Blood-Bond funciona en modo limitado
- Sugerencias básicas nada más
- Mensaje: "Necesito más historial para predicciones precisas"

---

## Ejemplo de Sesión

```
👤: @quinotospec.blood-bond
🤖: 🩸 **Blood-Bond: Análisis Completo**

📊 **Tu Perfil**
- Última actividad: hace 3 días
- Área principal: AUTH (60%)
- Velocidad: 3 tasks/sesión

🔥 **Sugerencias**
1. Continuar con AUTH — `@quinotospec.apply TSK-AUTH-003`
2. Preparar REWA para después
3. Revisar `billing-migration` (P1 sin progreso)

⚠️ **Alertas**: Ninguna (proyecto activo)

👤: @quinotospec.blood-bond --alerts
🤖: 🩸 **Blood-Bond: Alertas**

⚠️ `legacy-auth-refactor` sin avance en 18 días
   40% completada — ¿Bloqueada o abandonada?

💡 Sugerencia: `@quinotospec.apply TSK-AUTH-007` para continuar
```
