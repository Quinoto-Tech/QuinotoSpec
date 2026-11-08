# Propuesta Técnica: Elephant-Goldfish Adoption — Fresh-Context Review & Living Spec Drift

**Contract Version:** 1
**ID:** 2026-11-08-egm-adoption
**Prefijo:** EGMS-4f2a
**Fecha de Creación:** 2026-11-08
**Estado:** 🟡 Propuesta
**Prioridad:** P1
**Complejidad:** Media
**Servicios Afectados:** agent-dist/skills, agent-dist/workflows, agent-dist/ui, .quinoto-spec
**Autor:** Quinoto-Tech

---

## Resumen Ejecutivo

QuinotoSpec ya tiene Proposal First, discovery, delta-specs, evidencias y gates. Sin embargo, su revisión de propuestas sigue ocurriendo en el mismo hilo del agente que las redactó, lo que permite **sesgo de confirmación y contaminación de contexto**. El modelo *Elephant-Goldfish* de Google (`google/elephant-goldfish-model`) propone separar dos roles: un **Elephant** con contexto profundo que explora y redacta, y revisores **Goldfish** con contexto limpio (subagentes aislados) que auditan sin sesgo. Esta propuesta adopta ese modelo en QuinotoSpec mediante cinco capacidades: brainstorm con *shootdown* multi-lente, revisión Goldfish por subagentes frescos, validación de *Implementation Readiness*, reporte de drift specs↔código, y protocolo *artifact-first* para no volcar documentos largos al chat.

---

## Contexto y Problema

### Problema Actual

El flujo actual (`create-proposal` → `create-user-stories` → `create-tasks` → `review`) tiene tres debilidades frente a EGM:

1. **Revisión in-thread (no aislada):** `@quinotospec.review` y `review-handoff` pueden ejecutarse en la misma sesión del agente que redactó la propuesta. El agente tiende a validar sus propios supuestos en lugar de detectar puntos ciegos.
2. **Sin *shootdown* temprano:** no hay un paso estructurado que intente **derribar** la idea antes de invertir en user stories y tareas.
3. **Drift docs↔código parcial:** `refresh-discovery` actualiza discovery, y ahora el Specs Gate lee `specs/`, pero no existe un **reporte sistemático de divergencia** entre specs/README/design docs y el código real.
4. **Chat dump:** propuestas y hallazgos largos se vuelcan en la conversación, degradando el contexto del agente (EGM lo llama *Chat Dump Fatigue*).

### Evidencia / Discovery

- Stack relevante: `01-stack-profile.md` (bash, Python stdlib, Node opcional, OpenCode v1/v2).
- Arquitectura afectada: `03-architecture.md` (skills = capacidades; workflows = orquestación; agentes = personas).
- Endpoints/servicios: `04-endpoints-and-openapi.md` (no aplica runtime; sí CLI de skills).
- Deuda/hallazgos: `07-findings-and-recommendations.md` (workflows prompt-only, gates advisory).
- Referencia externa: `google/elephant-goldfish-model` (`docs/designs/architecture.md`, README, skills EGM).

---

## Solución Propuesta

### Enfoque

Adoptar el modelo Elephant-Goldfish como una **capa de revisión y drift** sobre el flujo existente, sin reemplazarlo:

1. **Brainstorm con shootdown (`quinotospec-brainstorm`)** — El Elephant entrevista y ancla la hipótesis; luego un enjambre de revisores con lentes fijos (simplicidad/YAGNI, reuso, escalabilidad, fallos, seguridad, coste operativo, reversibilidad) intenta derribarla. Salida: `concepts_brief.md`.

2. **Revisión Goldfish (`quinotospec-goldfish-review`)** — Orquestador que lanza subagentes **aislados** (contexto limpio) sobre `proposal.md` + `delta-specs/` + `discovery/`:
   - **Comprehension**: ¿el documento es auto-contenido?
   - **Design Critic**: ¿el diseño tiene fallos, cuellos de botella, modos de fallo?
   - **Zoom Out**: ¿simplicidad, YAGNI, reutilización de infraestructura existente?
   - **Implementation Readiness**: ¿existen rutas/archivos/firmas/tests concretos?
   - **Synthesizer**: deduplica y escribe `review-findings.md`.
   La revisión **falla** si el agente no puede crear subagentes frescos (igual que EGM).

3. **Implementation Readiness Gate (`readiness_validate.py`)** — Antes de Apply, valida que la propuesta/tareas declaren: archivos objetivo existentes o creables, comandos de test, criterios de aceptación y evidencia esperada. Endurece el DoR actual.

4. **Drift Report (`quinotospec-drift-report`)** — Compara `specs/`, `discovery/`, `README*.md` y `docs/` contra el código real (rutas, símbolos, comandos). Salida JSON + Markdown con severidad. Complementa `Huginn & Muninn` y `refresh-discovery`.

5. **Protocolo Artifact-First en la UI** — La UI ya es el visor natural: propuestas, specs, evidence y gates se renderizan ahí; los workflows deben escribir artefactos y devolver un enlace corto en chat, no volcar documentos completos.

### Alternativas Consideradas

| Alternativa | Pros | Contras | Descartada porque |
|-------------|------|---------|-------------------|
| Revisión in-thread secuencial | Simple, sin subagentes | Sesgo de confirmación; degrada contexto | EGM demuestra que el modelo se auto-valida |
| Reemplazar `party-mode` por EGM | Menos piezas | Se pierde debate multi-agente existente | `party-mode` es complementario, no sustituto |
| Copiar EGM tal cual (skills `egm-*`) | Paridad directa | Duplica nomenclatura y rompe inventario | Mejor adaptar al modelo skills/workflows de QuinotoSpec |
| Solo drift report | Bajo esfuerzo | No resuelve sesgo de revisión | Incompleto respecto al objetivo |

### Delta Specs

- `delta-specs/review/spec.md` — ADDED: revisión Goldfish en contexto aislado; pipeline de 5 etapas; readiness gate.
- `delta-specs/drift/spec.md` — ADDED: reporte de drift docs↔código con severidad y salida JSON.

---

## Alcance

### Incluye

- Nueva skill `quinotospec-brainstorm` + workflow `@quinotospec.brainstorm`.
- Nueva skill `quinotospec-goldfish-review` + workflow `@quinotospec.goldfish-review`.
- `readiness_validate.py` integrado en el Apply y en `rules_enforce`.
- Nueva skill `quinotospec-drift-report` + workflow `@quinotospec.drift-report`.
- Página UI `/drift` y enlace desde panel.
- Actualización de `manifest.json` (features, madurez, inventario) y `AGENTS.md`.

### No Incluye (Out of Scope)

- Portar las 8 personas EGM completas como agentes nativos (se reutilizan los 9 agentes existentes como lentes).
- Traducción automática de prosa ES/EN (sigue en Skald).
- Reemplazo de `party-mode`; ambos coexisten.
- Ejecución de código o pruebas por parte de los validadores (siguen siendo file-only).

### Servicios/Dominios Afectados

- `agent-dist/skills/` (nuevas skills y validator)
- `agent-dist/workflows/` (nuevos workflows)
- `agent-dist/ui/` (página drift)
- `.quinoto-spec/` (specs, reportes, evidence)

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|--------------|---------|------------|
| Subagentes frescos no disponibles en algún IDE | Media | Alto | El workflow falla explícitamente y documenta el límite; fallback a `review-handoff` humano |
| Sobrecarga de comandos (49→52 workflows) | Alta | Medio | Marcar brainstorm/goldfish/drift como opcionales; no tocar el track Simple/Quick Fix |
| Drift report con falsos positivos | Media | Medio | Severidad graduada; solo BLOCKING para specs aprobados |
| Coste de subagentes (tokens/tiempo) | Media | Medio | Lentes seleccionables; modo `--quick` con 2 lentes |
| Confusión Elephant vs party-mode | Baja | Bajo | Documentar: party-mode = debate; goldfish = auditoría sin sesgo |

---

## Plan de Implementación

1. **User Stories** → `user-stories.md`
2. **Tasks** → `tasks.md` (atómicas, verificables)
3. **Apply** → implementación incremental con tests
   - Fase A: `readiness_validate.py` + tests (bajo riesgo, valor inmediato).
   - Fase B: `goldfish-review` (workflow + skill) con subagentes.
   - Fase C: `brainstorm` (shootdown 7 lentes).
   - Fase D: `drift-report` + UI `/drift`.
4. **Changelog** → trazabilidad vía `quinotospec-update-changelog`
5. **Archive** → merge de delta-specs en `specs/`

### Criterios de Éxito

- [ ] `readiness_validate.py` bloquea Apply sin rutas/comandos/criterios (con `--require`).
- [ ] `goldfish-review` lanza ≥2 subagentes aislados y produce `review-findings.md`.
- [ ] `brainstorm` produce `concepts_brief.md` con lentes y veredicto.
- [ ] `drift-report` detecta al menos un drift sembrado en fixture y devuelve JSON estable.
- [ ] UI `/drift` lista reportes y no escribe en `.quinoto-spec/`.
- [ ] `validate-all.sh --strict` y `run-all-tests.sh` verdes.

---

## Plan de Verificación

- Tests: `bash tests/run-all-tests.sh` + nuevas suites `test-goldfish.sh`, `test-drift.sh`, `test-readiness.sh`.
- Validación: `/quinotospec-syntax-validate --type proposal --slug 2026-11-08-egm-adoption`
- Review: `@quinotospec.review` contra criterios de aceptación (usar Goldfish una vez implementado).

---

## Referencias

- EGM: https://github.com/google/elephant-goldfish-model
- EGM Architecture: `docs/designs/architecture.md` (Elephant/Goldfish, 5-step review, artifact-first)
- EGM Skills: brainstorm, draft, review, review-loop, resolve, bootstrap, drift-report
- Discovery: `.quinoto-spec/discovery/`
- Schema: `.quinoto-spec/schema.yaml`
- Reglas: `agent-dist/rules/quinotospec-rules.md`
