---
description: Mesa redonda multi-agente — los agentes discuten, debaten y colaboran en caracter sobre un tema
---

# Party Mode: Mesa Redonda Multi-Agente

Reune a los agentes especializados de QuinotoSpec en una mesa redonda para discutir un tema desde multiples perspectivas. Los agentes interactuan en caracter — debaten, desafian, construyen sobre las ideas de otros, y llegan a conclusiones mas robustas que cualquier agente individual.

**Dos modos de ejecucion:**
- **Voiced by Orchestrator** (default): El agente principal voicea 2-4 agentes en un intercambio fluido. Rapido, conversacional.
- **Spawned Subagents** (`--subagents`): Subagentes genuinamente independientes. Para analisis profundo y revisiones honestas.

---

## Parametros

| Parametro | Requerido | Descripcion |
|-----------|-----------|-------------|
| `TOPIC` | Si | El tema o pregunta a discutir |
| `--agents <lista>` | No | Agentes a incluir (separados por coma). Default: los mas relevantes |
| `--rounds <N>` | No | Numero de rondas de discusion (default: 3) |
| `--subagents` | No | Usar subagentes independientes en lugar de voicing |
| `--focus <aspecto>` | No | Enfocar la discusion en un aspecto especifico |
| `--output <path>` | No | Guardar la transcripcion (default: mostrar en consola) |

---

## Paso 0 — Resolver el Roster

1. Escanear `agent-dist/agents/` (o `.quinoto-spec/agents/` si existe override) para listar agentes disponibles.
2. Leer el frontmatter de cada agente: `name`, `specialization`, `trigger_workflows`.
3. Si se paso `--agents`, filtrar solo esos. Validar que existan.
4. Si NO se paso `--agents`:
   - Analizar el `TOPIC` para inferir que especialidades son relevantes.
   - Seleccionar 2-4 agentes cuyas especialidades cubran el tema.
   - Mostrar la seleccion: `Agentes seleccionados: Architect (diseno), Security Auditor (vulnerabilidades), Test Writer (cobertura).`
   - Preguntar confirmacion. El usuario puede agregar/quitar agentes.

---

## Paso 1 — Definir el Contexto

1. Si el proyecto tiene `.quinoto-spec/`, leer contexto relevante:
   - `.quinoto-spec/discovery/` para stack y arquitectura
   - `.quinoto-spec/specs/` para requerimientos actuales
   - `.quinoto-spec/proposals/` activas para iniciativas en curso
2. Construir un resumen de contexto que se compartira con todos los agentes.
3. Si `--focus`, agregar el aspecto especifico al contexto.

---

## Paso 2 — Ejecutar la Mesa Redonda

### Modo Voiced by Orchestrator (default)

El agente principal (orquestador) ejecuta las rondas voiceando a cada agente en caracter.

**Reglas del orquestador:**

1. **Nunca romper la 4ta pared** — No decir "ahora habla el Architect". Solo cambiar de voz.
2. **Turnos cortos** — 2-4 oraciones por intervencion. Esto es una conversacion, no reportes.
3. **Las personas chocan** — Si todos estan de acuerdo, el orquestador DEBE inyectar un punto de vista contrarian. El consenso prematuro es failure mode.
4. **Construir sobre ideas** — Cada agente puede referenciar lo que otro dijo: "El Architect tiene razon sobre la latencia, pero esta subestimando el costo de mantenimiento..."
5. **Health monitoring**:
   - Si todos estan de acuerdo por 2 turnos seguidos → inyectar perspectiva contrarian
   - Si la discusion va en circulos → nombrar el impasse y sugerir siguiente paso
   - Si un agente domina → dar turno a los que no han hablado
6. **El usuario dirige** — El usuario puede interrumpir en cualquier momento:
   - "Security Auditor, ¿que opinas de eso?"
   - "Trae al Test Writer"
   - "Profundicen en ese punto"
   - "Siguiente tema"

**Formato de cada intervencion:**

```
🛡️ **Security Auditor:** El endpoint POST /api/users no valida el Content-Type. Un atacante podria enviar XML y explotar el parser. Recomiendo agregar validacion estricta y un WAF.

🏗️ **Architect:** Coincido con el riesgo, pero agregar un WAF ahora es prematuro. Primero validemos los inputs en la capa de middleware. Si el trafico crece, ahi evaluamos WAF.
```

**Estructura de rondas:**

| Ronda | Objetivo | Dinamica |
|-------|----------|----------|
| **Ronda 1 — Perspectivas** | Cada agente da su vision inicial del tema | 1 intervencion por agente |
| **Ronda 2 — Debate** | Los agentes reaccionan a las perspectivas de otros | 2-3 intervenciones totales, enfoque en puntos de friccion |
| **Ronda 3 — Sintesis** | Los agentes convergen en recomendaciones accionables | 1 intervencion final por agente, enfocada en "que hacer" |

Si `--rounds` es diferente, ajustar la estructura.

### Modo Spawned Subagents (`--subagents`)

Para analisis profundo y revisiones honestas. Cada agente es un subagente independiente con contexto aislado.

1. **Primera ronda — Independiente:**
   - Spawnear un subagente por cada agente seleccionado, EN PARALELO.
   - Cada subagente recibe:
     - Su definicion de personalidad y especializacion
     - El contexto del proyecto
     - El TOPIC y `--focus` si aplica
     - Instruccion: "Da tu perspectiva inicial sobre este tema, en caracter."
   - Recolectar todas las respuestas.

2. **Segunda ronda — Reaccion:**
   - Spawnear subagentes SECUENCIALMENTE (necesitan ver lo que otros dijeron).
   - Cada subagente recibe las perspectivas de la ronda 1.
   - Instruccion: "Reacciona a lo que dijeron los otros agentes. ¿Donde coincidis? ¿Donde discrepas? ¿Que faltó?"

3. **Tercera ronda — Sintesis:**
   - Spawnear subagentes en PARALELO con todas las intervenciones previas.
   - Instruccion: "Basado en toda la discusion, ¿cual es tu recomendacion final? Se especifico y accionable."

---

## Paso 3 — Sintesis y Conclusiones

Despues de las rondas:

1. **Destilar temas clave:**
   - Puntos de consenso (todos coincidieron)
   - Puntos de disenso (donde hubo friccion productiva)
   - Recomendaciones accionables (que hacer concreto)

2. **Formato de salida:**

```markdown
# Party Mode: {{TOPIC}}

**Fecha:** {{DATE}}
**Agentes:** {{LISTA}}
**Modo:** {{VOICED | SPAWNED}}
**Rondas:** {{N}}

---

## Resumen de la Discusion

### Puntos de Consenso
- ...
### Puntos de Disenso
- ...
### Recomendaciones Accionables
- [ ] ...
- [ ] ...

---

## Transcripcion

{{TRANSCRIPCION_COMPLETA}}
```

3. Si `--output`, guardar en el path especificado.
4. Si no, mostrar en consola y preguntar si guardar.

---

## Paso 4 — Integracion con QuinotoSpec

Despues de la mesa redonda, ofrecer acciones:

```
¿Que queres hacer con estas conclusiones?

1. Crear propuesta (@quinotospec.create-proposal)
2. Agregar a proposal existente
3. Crear RFC (@quinotospec.create-rfc)
4. Guardar y continuar despues
5. Nada, solo fue exploratorio
```

---

## Paso 5 — Changelog (OBLIGATORIO)

Ejecutar skill `quinotospec-update-changelog`:
- **Titulo de la Accion**: Party Mode: {{TOPIC_TRUNCADO}}
- **Resumen**: Mesa redonda con {{N}} agentes ({{LISTA}}) sobre "{{TOPIC}}". Modo: {{MODE}}. {{M}} recomendaciones accionables generadas.

---

## Flags

| Flag | Descripcion |
|------|-------------|
| `--agents <lista>` | Agentes especificos separados por coma |
| `--rounds <N>` | Numero de rondas (default: 3) |
| `--subagents` | Usar subagentes independientes |
| `--focus <aspecto>` | Enfocar en un aspecto especifico |
| `--output <path>` | Guardar transcripcion en archivo |
| `--yes` | Saltar confirmaciones |

---

## Ejemplos

```
# Discusion abierta sobre un tema
@quinotospec.party-mode "¿Monolito o microservicios para el nuevo modulo de pagos?"

# Con agentes especificos
@quinotospec.party-mode "¿Como mejorar la seguridad del API?" --agents security-auditor,architect,devops-engineer

# Analisis profundo con subagentes independientes
@quinotospec.party-mode "¿Es viable migrar a Rust?" --subagents --rounds 4

# Enfocado en un aspecto
@quinotospec.party-mode "Revisar la arquitectura actual" --focus "escalabilidad y puntos de falla"

# Guardar resultado
@quinotospec.party-mode "Estrategia de testing" --output .quinoto-spec/party-mode/testing-strategy.md
```
