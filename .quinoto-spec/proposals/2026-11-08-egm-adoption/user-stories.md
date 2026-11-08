# User Stories — Elephant-Goldfish Adoption

| ID | User Story | Prioridad | Estado |
|----|-----------|-----------|--------|
| US-EGMS-4f2a-001 | Como ingeniero, quiero que revisores con contexto limpio auditen mi propuesta para descubrir supuestos no declarados. | P1 | 🟡 Propuesta |
| US-EGMS-4f2a-002 | Como product owner, quiero un shootdown temprano de ideas para no invertir en propuestas débiles. | P2 | 🟡 Propuesta |
| US-EGMS-4f2a-003 | Como agente implementador, quiero validar readiness antes de Apply para no empezar sin información. | P1 | 🟡 Propuesta |
| US-EGMS-4f2a-004 | Como mantenedor, quiero un reporte de drift docs↔código para detectar documentación obsoleta. | P1 | 🟡 Propuesta |
| US-EGMS-4f2a-005 | Como revisor, quiero ver los reportes de drift en el dashboard para priorizar correcciones. | P2 | 🟡 Propuesta |

## US-EGMS-4f2a-001 — Revisión sin sesgo con subagentes frescos

**Como** ingeniero que redactó una propuesta, **quiero** que revisores con contexto limpio la auditen, **para** descubrir supuestos no declarados y puntos ciegos que mi propia sesión no detecta.

**Criterios de aceptación:**
- El workflow `@quinotospec.goldfish-review` lanza ≥2 subagentes aislados sobre `proposal.md` + `delta-specs/` + `discovery/`.
- Produce `review-findings.md` con hallazgos deduplicados y severidad.
- Si no hay subagentes frescos, falla explícitamente (no simula la revisión).

## US-EGMS-4f2a-002 — Shootdown temprano de ideas

**Como** product owner, **quiero** que una idea sea derribada por lentes fijos antes de crear user stories, **para** evitar invertir en propuestas débiles.

**Criterios de aceptación:**
- `@quinotospec.brainstorm` produce `concepts_brief.md` con hipótesis, lentes y veredicto (GO / PIVOT / KILL).
- Lentes por defecto: simplicidad/YAGNI, reuso, escalabilidad, fallos, seguridad, coste operativo, reversibilidad.

## US-EGMS-4f2a-003 — Validar readiness antes de Apply

**Como** agente implementador, **quiero** que Apply valide rutas, comandos y criterios declarados, **para** no empezar sin información suficiente.

**Criterios de aceptación:**
- `readiness_validate.py --root . --json` devuelve `valid` y lista faltantes.
- Integrado en Apply y en `rules_enforce` con `--require`.
- Si la propuesta no declara archivos/comandos/criterios, Apply se detiene.

## US-EGMS-4f2a-004 — Detectar drift docs↔código

**Como** mantenedor, **quiero** un reporte periódico que compare specs/docs con el código, **para** detectar documentación obsoleta.

**Criterios de aceptación:**
- `@quinotospec.drift-report` compara `specs/`, `discovery/`, `README*.md`, `docs/` contra rutas/símbolos/comandos.
- Salida JSON + Markdown con severidad (OK / WARN / BLOCKING).
- Detecta un drift sembrado en fixture y no produce falsos bloqueos en repo limpio.

## US-EGMS-4f2a-005 — Ver reportes de drift en la UI

**Como** revisor, **quiero** ver los reportes de drift en el dashboard, **para** priorizar la corrección sin abrir archivos.

**Criterios de aceptación:**
- Nueva página `/drift` lista reportes con fecha, severidad y enlaces a detalle.
- La UI sigue read-only.
