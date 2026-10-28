---
description: Genera una guia de code review para el revisor humano cuando una propuesta esta completada, consolidando propuesta, historias, tareas, evidencia, changelog y cambios en git en un solo archivo
---

# Workflow: Review Handoff

Este workflow se ejecuta cuando una propuesta esta completada (todas sus tareas corrieron) y **antes** de `/quinotospec.archive`. Genera un archivo autonomo — `CODE_REVIEW_GUIDE.md` — que sirve de guia a la persona que hara el code review, consolidando en un solo documento todo el contexto disperso de `.quinoto-spec/` y del historial git.

> ⚠️ Orden del ciclo: `apply` → `mark-done` → **`review-handoff`** (este workflow) → code review humano (feedback via `quinotospec-receive-review`) → `archive`.

Diferencia con `/quinotospec.review`: ese workflow hace que **el agente** revise **una tarea/branch** contra sus criterios. Este workflow no revisa codigo: **prepara el terreno** para que **un humano** revise **la propuesta completa** con todo el contexto necesario.

## Extension hooks

Consulta `before_review_handoff` y `after_review_handoff` con `extension_manager.py hooks --point <point> --json`. Ejecuta hooks automaticos solo con `--run --yes` y adjunta sus resultados a la guia.

**Parametros Requeridos:**
- `PROPOSAL_SLUG`: El slug de la propuesta completada (ej. `2026-09-24-add-login`).

**Flags:**

| Flag | Descripcion |
|------|-------------|
| `--force` | Genera la guia aunque queden tareas pendientes; el gap queda documentado en la seccion de completitud |
| `--full-diff` | Incluye el diff completo inline en la seccion de git (por defecto solo `--stat` y `--name-status`) |
| `--output PATH` | Escribe una copia adicional de la guia en PATH (ej. raiz del repo para entregarsela al reviewer) |
| `--archived` | Busca la propuesta en `.quinoto-spec/proposals/_archived/{{PROPOSAL_SLUG}}/` |

## Instrucciones de Ejecucion

### Paso 1 — Localizar la propuesta y validar completitud (OBLIGATORIO)

1. Localiza la propuesta en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/`; si no existe y se paso `--archived`, busca en `.quinoto-spec/proposals/_archived/{{PROPOSAL_SLUG}}/`. Si no existe en ninguna ubicacion, notifica al usuario y detente.
2. Recupera el **Prefijo** y la **Fecha de Creacion** desde `proposal.md`.
3. Ejecuta `python3 -B agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json` y filtra las tareas de la propuesta por prefijo.
4. **Gate de completitud**:
   - Si hay tareas `pending`, `blocked` o `in_progress` → muestra el conteo y la lista de pendientes. Genera la guia **solo con `--force`**, documentando el gap en la seccion 1 de la guia; sin `--force`, detente y sugiere `/quinotospec.apply {{NEXT_TASK_ID}}`.
5. **Evidencia por tarea**: verifica `.quinoto-spec/evidence/{{TASK_ID}}/` para cada tarea. Una tarea sin evidencia genera `⚠️` en la guia (advertencia, no bloqueo).
6. **Advertencias de contexto** (se registran en la guia, no bloquean):
   - Discovery obsoleto: `01-stack-profile.md` con mas de 30 dias.
   - `.quinoto-spec/constitution.md` con estado `active` → lee sus principios para el checklist de revision; si esta ausente → advertencia de compatibilidad.

### Paso 2 — Recolectar contexto

Lee los artefactos de la propuesta (en su carpeta **y en su subcarpeta `_archived/`** — `mark-done` mueve ahi los archivos completados):

- `proposal.md` → titulo, estado, prioridad, complejidad, servicios afectados, resumen ejecutivo, alcance (incluye / no incluye), riesgos, criterios de exito.
- `user-stories.md` → stories con sus criterios de aceptacion.
- `*_tasks.md` → tabla de tareas: ID, titulo, **Archivos a Modificar** declarados, dependencias, estado.
- `.quinoto-spec/evidence/{{TASK_ID}}/` → que se verifico por tarea (verify-before-done, tests, lint).
- `delta-specs/*/spec.md` (si existe) → requerimientos ADDED / MODIFIED / REMOVED / RENAMED.
- `.quinoto-spec/discovery/01-stack-profile.md` → comandos de tests / lint / typecheck del stack.
- Changelog de la propuesta: `python3 -B agent-dist/skills/quinotospec-contract/contract.py changelog --root . --json` filtrado por el prefijo.

### Paso 3 — Analizar cambios en git

1. Identifica los branches de la propuesta por convencion de nombrado:
   ```bash
   git branch --list '*{{PREFIX}}*'
   ```
   (patrones `feature/TSK-{{PREFIX}}-*` y `bugfix/TSK-{{PREFIX}}-*`).
2. Determina la rama base (`main` o la rama por defecto del repo).
3. Por cada branch (o por el rango de commits si ya se mergeo):
   ```bash
   git log --oneline {{BASE}}..{{HEAD}}
   git diff --name-status {{BASE}}..{{HEAD}}
   git diff --stat {{BASE}}..{{HEAD}}
   ```
4. **Mapea tarea → commits**: asocia cada commit/branch a su `{{TASK_ID}}` (por el nombre del branch o por la mencion del ID en el mensaje). Las tareas sin commits identificables quedan `⚠️ sin mapeo` en la guia.
5. Compara **archivos declarados vs reales**: los archivos de la columna "Archivos a Modificar" de cada tarea contra el `--name-status`. Declara `⚠️` cualquier archivo real que no estaba declarado.
6. Fallback si no hay branches con el prefijo: `git log --since="{{FECHA_DE_CREACION}}" --oneline --name-only` filtrando por los archivos declarados en las tareas.

### Paso 4 — Generar la guia

Escribe `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/CODE_REVIEW_GUIDE.md` con la estructura del Paso 5. Si se paso `--output {{PATH}}`, escribe una copia adicional alli.

**Reglas de generacion:**
- La guia es **autonoma**: el reviewer entiende el cambio sin abrir `.quinoto-spec/` (los paths fuente se citan para profundizar).
- Cita paths exactos (`archivo` y `archivo:linea` cuando aplique); nunca parrafos genericos.
- Marca cada item verificable como ✅ verificado / ⚠️ advertido / ❌ faltante; **nunca inventes estado**.
- Con `--full-diff` incrusta el `git diff` completo; por defecto solo estadisticas + los comandos exactos para reproducir la inspeccion.

### Paso 5 — Estructura de la guia (template)

````markdown
# Code Review Guide — {{PROPOSAL_TITLE}}

> Generado por `quinotospec.review-handoff` el {{DATE}}.
> Propuesta: `{{PROPOSAL_SLUG}}` | Prefijo: `{{PREFIX}}` | Estado: {{ESTADO}} | Prioridad: {{PRIORIDAD}} | Complejidad: {{COMPLEJIDAD}}

## 1. Resumen para el reviewer

- **Problema**: {{1-2 lineas del problema que motiva la propuesta}}
- **Solucion implementada**: {{1-2 lineas del enfoque}}
- **Servicios/Dominios afectados**: {{lista de servicios}}
- **Alcance**: incluye {{...}} — no incluye {{...}}
- **Completitud**: {{N}}/{{TOTAL}} tareas completadas.{{ Si se genero con --force: " Generada con --force: faltan {{PENDIENTES}} tareas — revisar con cuidado extra: {{lista}}."}}

{{Advertencias detectadas: discovery obsoleto, constitucion ausente, evidencia faltante por tarea, branches sin mapear.}}

## 2. User Stories y criterios de aceptacion

| Story | Criterio de aceptacion | Como verificarlo |
|-------|------------------------|------------------|
| {{US_ID}} — {{titulo}} | {{criterio}} | {{comando / archivo / escenario concreto}} |

## 3. Tareas ejecutadas

| Tarea | Titulo | Archivos declarados | Deps | Estado | Evidencia |
|-------|--------|--------------------|------|--------|-----------|
| {{TSK_ID}} | {{titulo}} | {{archivos}} | {{dependencias}} | {{estado}} | `.quinoto-spec/evidence/{{TSK_ID}}/` |

## 4. Cambios en Git

**Rama base**: {{BASE}} | **Branches**: {{lista de branches}}

**Commits ({{N}})**:
{{git log --oneline base..head}}

**Archivos**: {{N}} modificados, {{N}} nuevos, {{N}} eliminados
{{git diff --stat base..head}}

**Mapeo tarea → commits**:

| Tarea | Commits | Archivos reales vs declarados |
|-------|---------|-------------------------------|
| {{TSK_ID}} | {{commits o "sin mapeo"}} | {{coinciden / extra: {{lista}}}} |

**Comandos para reproducir la inspeccion**:
```bash
git diff --stat {{BASE}}..{{HEAD}}
git diff {{BASE}}..{{HEAD}} -- {{ARCHIVO}}
```

## 5. Historial del changelog (prefijo {{PREFIX}})

| Fecha | Entrada | Tiempo ahorrado |
|-------|---------|-----------------|
| {{fecha}} | {{titulo de la entrada}} | {{tiempo}} |

## 6. Evidencia de verificacion

| Tarea | Evidencia registrada | Verificado |
|-------|----------------------|------------|
| {{TSK_ID}} | {{kinds de evidencia}} | ✅ / ⚠️ sin evidencia |

## 7. Delta de requerimientos (si aplica)

{{Por dominio: N ADDED, M MODIFIED, R REMOVED en delta-specs/{{dominio}}/spec.md — citar los nombres de los requerimientos.}}

## 8. Como verificar el cambio

{{Comandos del stack desde 01-stack-profile.md: suite completa de tests, tests focalizados por archivo, lint, typecheck.}}

## 9. Checklist de revision (marca el resultado)

- [ ] **Criterios de aceptacion**: cada criterio de las stories esta cubierto por el codigo
- [ ] **Tests**: hay tests para la logica nueva y pasan
- [ ] **Convenciones del stack**: el codigo sigue los patrones de `01-stack-profile.md`
- [ ] **Archivos declarados vs reales**: sin archivos extra ni declarados sin tocar
- [ ] **Sin regresiones**: la suite completa pasa
- [ ] **Compliance constitucional**: {{si la constitucion esta activa: cada principio aplicable tiene evidencia o excepcion aprobada}}
- [ ] **Sin deuda tecnica obvia**: sin TODOs sin resolver, logs de debug ni codigo comentado que no deberia estar
- [ ] **Seguridad basica**: inputs validados, sin secretos hardcodeados, endpoints nuevos con auth
- [ ] **Performance**: rutas criticas tocadas no degradan (si aplica)

## 10. Riesgos y areas sensibles

- **Servicios criticos tocados**: {{lista}}
- **Breaking changes**: {{schema / API / contratos}}
- **Archivos mas modificados**: {{top 3 por frecuencia de cambio}}
- **Riesgos declarados en la propuesta**: {{tabla riesgo/probabilidad/impacto/mitigacion}}

## 11. Como reportar feedback

- Formato sugerido: `{{TSK_ID}} — hallazgo — severidad (bloqueante / menor / pregunta)`.
- El agente procesa el feedback con `quinotospec-receive-review` (READ → UNDERSTAND → VERIFY → EVALUATE → RESPOND → IMPLEMENT): verifica antes de implementar, sin acuerdo performativo, y aplica los cambios via `quinotospec-apply` conservando sus gates.
- Si un hallazgo viola YAGNI, falta contexto o rompe funcionalidad, se responde con push back tecnico.

---
*Fuentes: proposal.md, user-stories.md, *_tasks.md, `.quinoto-spec/evidence/`, `.quinoto-spec/changelog/`, git.*
````

### Paso 6 — Cierre

1. Reporta al usuario: path de la guia, secciones generadas, advertencias detectadas (⚠️) y pendientes de mapeo.
2. Pasos siguientes sugeridos:
   - Entregar `CODE_REVIEW_GUIDE.md` (o la copia en `--output`) al reviewer humano.
   - Al recibir su feedback → `quinotospec-receive-review`.
   - Tras resolver el feedback → `/quinotospec.archive {{PROPOSAL_SLUG}}`.

**Instruccion Final OBLIGATORIA (Changelog):**
Una vez completada la accion, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Titulo de la Accion**: Review Handoff Generated: {{PROPOSAL_SLUG}}
- **Resumen**: Se genero la guia de code review para la propuesta '{{PROPOSAL_SLUG}}' en `CODE_REVIEW_GUIDE.md`. Completitud: {{N}}/{{TOTAL}} tareas. Advertencias: [lista si aplica].

## Manejo de Errores

- Propuesta inexistente → notificar y listar slugs disponibles (`ls .quinoto-spec/proposals/`).
- Tareas pendientes sin `--force` → detener y sugerir `/quinotospec.apply {{NEXT_TASK_ID}}`.
- Repo sin historial git o sin branches del prefijo → generar la guia con fallback por fecha y marcar la seccion 4 como `⚠️ inspeccion git limitada`.
- Tarea sin evidencia → `⚠️` en secciones 3 y 6; no bloquea la generacion.
- `CODE_REVIEW_GUIDE.md` ya existente → sobreescribe y notifica (regenerable por diseno).

## Ejemplos

```
@quinotospec.review-handoff 2026-09-24-add-login
@quinotospec.review-handoff 2026-09-24-add-login --output ./CODE_REVIEW.md
@quinotospec.review-handoff 2026-09-24-add-login --full-diff
@quinotospec.review-handoff 2026-08-01-refactor-api --archived
@quinotospec.review-handoff 2026-09-24-add-login --force
```
