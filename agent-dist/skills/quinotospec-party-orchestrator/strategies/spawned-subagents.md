# Strategy: Spawned Subagents

## When to Use

- Analisis profundo que requiere contexto aislado
- Cuando se necesita independencia real entre agentes (no sesgo de grupo)
- Revisiones de seguridad, arquitectura, o calidad donde la honestidad es critica
- Temas complejos que requieren razonamiento extenso
- Cuando hay suficiente presupuesto de tokens para multiples subagentes

## How It Works

Cada agente es un subagente independiente con su propio contexto aislado. No comparten sesion con el orquestador ni entre ellos. El orquestador recolecta resultados y los comparte en rondas posteriores.

**Ventaja:** Independencia real, sin sesgo de grupo. Cada agente piensa por si mismo.
**Desventaja:** Mas lento, consume mas tokens, requiere sincronizacion de resultados.

---

## Rondas (Default: 3)

### Ronda 1 — Perspectivas Independientes (PARALELO)

**Objetivo:** Cada agente analiza el tema desde su especialidad, sin saber que otros agentes estan participando.

**Ejecucion:**
- Spawnear 1 subagente por agente seleccionado.
- Todos en PARALELO (no secuencial — son independientes).
- Usar `Task` tool con `subagent_type: general`.

**Prompt para cada subagente:**

```
Eres el agente **{{NAME}}** de QuinotoSpec — {{TITLE}}.

## Tu Especialidad
{{SPECIALIZATION}}

## Tu Personalidad
{{PERSONALITY}}

## Contexto del Proyecto
{{SHARED_CONTEXT}}

## Topico a Analizar
{{TOPIC}}
{{FOCUS}}

## Instruccion
Analiza este tema desde tu area de expertise. Da tu perspectiva inicial:
- Que ves como los puntos mas importantes desde tu especialidad?
- Que riesgos o problemas potenciales identificas?
- Que recomendaciones iniciales darias?

Se especifico, concreto, y en caracter. Responde en 3-5 parrafos.
No sabes que otros agentes estan participando — solo da tu perspectiva.
```

**Recoleccion:**
- Esperar a que TODOS los subagentes terminen.
- Almacenar respuestas etiquetadas por agente.

---

### Ronda 2 — Reaccion Cruzada (SECUENCIAL)

**Objetivo:** Cada agente lee lo que los otros dijeron y reacciona. Aqui es donde emerge el debate.

**Ejecucion:**
- Spawnear subagentes SECUENCIALMENTE (un orden aleatorio, rotar en cada ejecucion).
- Cada subagente recibe las perspectivas COMPLETAS de la ronda 1.

**Prompt para cada subagente:**

```
Eres el agente **{{NAME}}** de QuinotoSpec.

## Perspectivas de la Ronda Anterior

{{ALL_ROUND_1_PERSPECTIVES}}

## Tu Perspectiva en la Ronda 1
{{YOUR_ROUND_1_PERSPECTIVE}}

## Instruccion
Leiste las perspectivas de otros agentes. Ahora reacciona:

1. ¿En que coincidis con otros? ¿En que discrepas?
2. ¿Hay algo que los otros no estan viendo desde tu especialidad?
3. ¿Cambiaste de opinion en algo despues de leer a los otros?
4. ¿Que preguntas le harias a un agente especifico?

Se honesto. Si crees que otro agente esta equivocado, decilo con argumentos tecnicos.
El objetivo no es ser educado — es llegar a la mejor conclusion.
```

**Recoleccion secuencial:**
- Esperar a que CADA subagente termine antes de spawnear el siguiente.
- El orden secuencial importa: el agente 2 lee lo que dijo el agente 1 en ronda 2, etc.
- Esto crea una cadena de reacciones que simula una conversacion real.

---

### Ronda 3 — Sintesis Independiente (PARALELO)

**Objetivo:** Cada agente propone su recomendacion final, informada por toda la discusion.

**Ejecucion:**
- Spawnear subagentes en PARALELO.
- Cada uno recibe TODAS las intervenciones de rondas 1 y 2.

**Prompt para cada subagente:**

```
Eres el agente **{{NAME}}** de QuinotoSpec.

## Discusion Completa

{{ALL_PERSPECTIVES_ALL_ROUNDS}}

## Instruccion
Basado en toda la discusion anterior, da tu RECOMENDACION FINAL:

1. ¿Cuales son las 3 acciones mas importantes que deberiamos tomar?
2. ¿Hay algo en lo que todos coincidimos y deberiamos ejecutar ya?
3. ¿Que quedo sin resolver y necesita mas analisis?

Se accionable, no teorico. Cada recomendacion debe ser algo que un desarrollador pueda ejecutar.
Formato: viñetas con "Accion: [que] | Responsable: [quien] | Prioridad: [P1/P2/P3]".
```

---

## Prompt Construction Guidelines

### Context Injection

Cada subagente recibe:

1. **Agent persona** — De `agent-dist/agents/{name}.md`:
   - Frontmatter: `specialization`, `trigger_workflows`
   - Body: `## Personality` (primer parrafo), `## Capabilities` (lista completa)

2. **Project context** — Compartido entre todos:
   - Stack tecnologico (de discovery)
   - Arquitectura (de discovery)
   - Specs relevantes (de specs/)
   - Propuestas activas relacionadas

3. **Topic context** — Compartido entre todos:
   - El TOPIC exacto
   - El FOCUS si existe
   - Lo que el usuario quiere obtener de la discusion

### Context Size Management

- El contexto compartido debe ser < 1000 tokens.
- Si discovery + specs + proposals excede esto, resumir.
- Priorizar: topic relevance > recency > completeness.

---

## Manejo de Errores

| Error | Accion |
|-------|--------|
| Subagente timeout (> 120s) | Marcar como timeout. Mostrar "Debugger no respondio a tiempo. Continuando con los otros agentes." |
| Subagente devuelve error | Mostrar el error. Ofrecer: reintentar, omitir, o abortar party mode |
| Subagente responde fuera de caracter | Advertir en la sintesis: "Test Writer respondio de forma generica. Tomar con precaucion." |
| Subagente contradice su propia ronda anterior | Senialarlo en la sintesis: "Code Reviewer cambio de opinion entre ronda 1 y 3 sobre {tema}." |

---

## Comparacion con Voiced by Orchestrator

| Dimension | Voiced | Spawned |
|-----------|--------|---------|
| **Velocidad** | Rapido (1 llamada) | Lento (N*3 llamadas) |
| **Costo** | Bajo | Alto (tokens * N agentes * 3 rondas) |
| **Independencia** | Baja (contexto compartido) | Alta (contexto aislado) |
| **Sesgo de grupo** | Posible | Eliminado |
| **Debate real** | Simulado por orquestador | Real entre agentes |
| **Calidad de sintesis** | Depende del orquestador | Cada agente sintetiza independientemente |
| **Mejor para** | Brainstorming, exploracion | Auditoria, decisiones criticas |
