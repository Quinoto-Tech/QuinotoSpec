---
name: quinotospec-party-orchestrator
description: Orquesta mesas redondas multi-agente — maneja turnos, genera debate productivo, monitorea salud de la discusion
---

# Party Orchestrator

## Overview

El orquestador gestiona la ejecucion de una mesa redonda multi-agente. No participa en la discusion — facilita que los agentes interactuen en caracter, mantiene la discusion productiva, y detecta problemas de dinamica grupal (groupthink, impasse, dominacion).

**Core principle:** El conflicto productivo es el objetivo. El consenso prematuro es falla.

---

## Modos de Operacion

El orquestador soporta dos modos, definidos en `strategies/`:

| Modo | Archivo | Cuando usar |
|------|---------|-------------|
| **Voiced by Orchestrator** | `voiced-by-orchestrator.md` | Rapido, conversacional. El agente principal voicea a todos los agentes en un solo hilo |
| **Spawned Subagents** | `spawned-subagents.md` | Analisis profundo. Subagentes independientes con contexto aislado |

---

## Paso 1 — Preparar el Contexto Compartido

Antes de iniciar las rondas:

1. Leer definiciones de agentes seleccionados (frontmatter + cuerpo).
2. Extraer para cada agente: `name`, `specialization`, `personality` (primer parrafo de la seccion Personality), `capabilities`.
3. Leer contexto del proyecto (`.quinoto-spec/discovery/`, `specs/`, `proposals/` activas).
4. Construir un `shared_context` que incluya:
   - Stack tecnologico (de `01-stack-profile.md`)
   - Arquitectura actual (de `03-architecture.md`)
   - Requerimientos relevantes (de `specs/`)
   - Propuestas activas relacionadas
5. Construir `agent_contexts`: para cada agente, un parrafo que defina su rol, personalidad y capacidades.

---

## Paso 2 — Seleccionar Estrategia

1. Si el workflow paso `--subagents` → usar `spawned-subagents`.
2. Si no → usar `voiced-by-orchestrator` (default).

Cargar la estrategia desde `strategies/<mode>.md` y seguir sus instrucciones.

---

## Paso 3 — Ejecutar Rondas

Seguir la estructura de rondas definida en la estrategia seleccionada.

Para cada ronda:

1. Determinar el objetivo de la ronda.
2. Determinar orden de intervencion (rotar para que nadie domine).
3. Ejecutar intervenciones segun la estrategia.
4. Al final de la ronda, evaluar salud de la discusion.

---

## Paso 4 — Monitoreo de Salud

Evaluar despues de cada ronda:

| Condicion | Diagnostico | Accion |
|-----------|-------------|--------|
| Todos coincidieron en todo | Groupthink | Inyectar perspectiva contrarian: "Antes de seguir, consideremos la posibilidad opuesta..." |
| Mismos argumentos repetidos | Impasse | Nombrar el impasse: "Parece que estamos en un loop sobre {tema}. ¿Que informacion nos falta para resolverlo?" |
| Un agente hablo 3+ veces, otro 0 | Dominacion | Dar turno explicito al que no hablo: "Debugger, no hemos escuchado tu perspectiva. ¿Que ves vos?" |
| Discusion derivo del tema | Scope creep | Re-enfocar: "Volviendo al tema original: {TOPIC}. ¿Como aplica esto?" |

---

## Paso 5 — Sintesis

Despues de la ultima ronda:

1. Identificar puntos donde TODOS los agentes coincidieron → **Puntos de Consenso**.
2. Identificar puntos donde hubo desacuerdo productivo → **Puntos de Disenso**.
3. Extraer acciones concretas mencionadas → **Recomendaciones Accionables**.
4. Identificar preguntas que quedaron abiertas → **Preguntas Pendientes**.

---

## Paso 6 — Formatear Salida

Generar el documento de sintesis en el formato definido por el workflow (`@quinotospec.party-mode`).

---

## Anti-Patrones

| Anti-Patron | Por que es malo | Correccion |
|-------------|-----------------|------------|
| Agentes demasiado educados | "Excelente punto, Architect" → performative agreement, no debate real | Agentes deben desafiar, no felicitar |
| Consenso inmediato | Significa que los agentes no estan realmente pensando | Inyectar contrarian |
| Monologos largos | No es conversacion, es presentacion | Cortar a las 4 oraciones |
| Orquestador opina | El orquestador no es un agente — no tiene perspectiva | Solo facilitar, no opinar |
| Usuario ausente | El usuario debe poder dirigir en cualquier momento | Pausar si el usuario no interactuo en 2 rondas |

---

## Integracion con Agentes

El orquestador lee las definiciones de agentes de:

1. `.quinoto-spec/agents/` (override de proyecto, maxima prioridad)
2. `agent-dist/agents/` (definiciones shipped con QuinotoSpec)

Nombre de archivo = `name` en el frontmatter (sin `.md`). El orquestador busca coincidencia exacta.

Si un agente no existe en ninguna ubicacion, advertir y continuar con los agentes encontrados.
