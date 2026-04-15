---
description: Ejecución paralela de múltiples agentes para tareas masivas
---

# Battle Frenzy: Swarm Mode

Ejecuta múltiples subagentes en paralelo para tareas masivas.

---

## Concepto

Battle Frenzy divide tareas grandes en chunks independientes y los ejecuta en paralelo:
- Analiza la tarea y determina si es paralelizable
- Divide en chunks de hasta 5 trabajadores simultáneos
- Ejecuta usando subagentes en paralelo
- Consolida resultados

---

## Comandos

| Comando | Descripción |
|---------|-------------|
| `@quinotospec.battle-frenzy` | Ejecución completa |
| `@quinotospec.battle-frenzy --dry-run` | Solo mostrar división |
| `@quinotospec.battle-frenzy --limit N` | Limitar a N agentes |

---

## Flujo de Ejecución

### Paso 1 — Task Splitter
Ejecutar skill `quinotospec-swarm-task-splitter`:
- Analiza la tarea masiva
- Determina si es paralelizable
- Genera `chunks.json` con chunks independientes

### Paso 2 — Validación
Si `--dry-run`: mostrar chunks y preguntar confirmar

### Paso 3 — Swarm Executor
Ejecutar skill `quinotospec-swarm-executor`:
- Lee `chunks.json`
- Agrupa chunks por dependencias (waves)
- Ejecuta en paralelo (max 5)
- Recolecta resultados

### Paso 4 — Consolidación
Combinar resultados y generar reporte:
- Mostrar summary
- Detallar éxitos y fallos
- Ofrecer siguiente acción

---

## Ejemplo de Sesión

```
👤: @quinotospec.battle-frenzy Migrar 10 endpoints a v2
🤖: 🪓 **Battle Frenzy: Análisis**

    Analizando tarea: Migrar 10 endpoints a v2
    ¿Es paralelizable? ✅ Sí (independientes)

    Dividiendo en chunks...
    → SWARM-001: /users
    → SWARM-002: /products
    → SWARM-003: /orders
    → SWARM-004: /payments
    → SWARM-005: /notifications
    → SWARM-006: /auth
    → SWARM-007: /profile
    → SWARM-008: /settings
    → SWARM-009: /reports
    → SWARM-010: /webhooks

    Total: 10 chunks, 5 paralelos, 2 waves

    ⚡ Ejecutando en paralelo...
    Wave 1: [SWARM-001 al SWARM-005] → ✅✅✅✅✅
    Wave 2: [SWARM-006 al SWARM-010] → ✅✅✅✅✅

🪓 **Battle Frenzy: Completado**
    ✅ 10/10 exitosos (45s)
    📊 Reporte: .quinoto-spec/swarm/results.json

👤: @quinotospec.battle-frenzy --dry-run
🤖: 🪓 **Battle Frenzy: Dry Run**

    Chunks generados (no ejecutados):
    ├── SWARM-001: /users
    ├── SWARM-002: /products
    └── ...

    Para ejecutar: @quinotospec.battle-frenzy
```

---

## Manejo de Errores

| Error | Acción |
|-------|--------|
| No paralelizable | Recomendar `@quinotospec.apply` |
| Algunos chunks fallan | Partial results (continúa) |
| Timeout | Marcar chunk como timeout |

---

## Archivos Generados

```
.quinoto-spec/swarm/
├── chunks.json     # División de tareas
├── results.json   # Resultados consolidados
└── errors.json    # Errores si los hay
```