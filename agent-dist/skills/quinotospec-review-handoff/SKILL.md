---
name: quinotospec-review-handoff
description: Genera una guia de code review para el revisor humano cuando una propuesta esta completada, consolidando propuesta, historias, tareas, evidencia, changelog y cambios en git en un solo archivo
---

# Workflow: Review Handoff

Este workflow se ejecuta cuando una propuesta esta completada (todas sus tareas corrieron) y **antes** de `/quinotospec.archive`. Genera un archivo autonomo — `CODE_REVIEW_GUIDE.md` — que sirve de guia a la persona que hara el code review, consolidando en un solo documento todo el contexto disperso de `.quinoto-spec/` y del historial git.

> ⚠️ Orden del ciclo: `apply` → `mark-done` → **`review-handoff`** (esta skill) → code review humano (feedback via `quinotospec-receive-review`) → `archive`.

Diferencia con `/quinotospec.review`: ese workflow hace que **el agente** revise **una tarea/branch** contra sus criterios. Esta skill no revisa codigo: **prepara el terreno** para que **un humano** revise **la propuesta completa** con todo el contexto necesario.

**Parametros Requeridos:**
- `PROPOSAL_SLUG`: El slug de la propuesta completada (ej. `2026-09-24-add-login`).

**Flags:**

| Flag | Descripcion |
|------|-------------|
| `--force` | Genera la guia aunque queden tareas pendientes; el gap queda documentado en la seccion de completitud |
| `--full-diff` | Incluye el diff completo inline en la seccion de git (por defecto solo `--stat` y `--name-status`) |
| `--output PATH` | Escribe una copia adicional de la guia en PATH (ej. raiz del repo para entregarsela al reviewer) |
| `--archived` | Busca la propuesta en `.quinoto-spec/proposals/_archived/{{PROPOSAL_SLUG}}/` |

**Instrucciones:**

1. **Localizar la propuesta y validar completitud (OBLIGATORIO)**:
    - Localiza la propuesta en `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/`; si no existe y se paso `--archived`, busca en `.quinoto-spec/proposals/_archived/{{PROPOSAL_SLUG}}/`. Si no existe, notifica al usuario y detente.
    - Recupera el **Prefijo** y la **Fecha de Creacion** desde `proposal.md`.
    - Ejecuta `python3 -B agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json` y filtra las tareas de la propuesta por prefijo.
    - **Gate de completitud**: si hay tareas `pending`, `blocked` o `in_progress` → muestra el conteo y la lista; genera la guia **solo con `--force`** (documentando el gap); sin `--force`, detente y sugiere `/quinotospec.apply {{NEXT_TASK_ID}}`.
    - **Evidencia por tarea**: verifica `.quinoto-spec/evidence/{{TASK_ID}}/`; una tarea sin evidencia genera `⚠️` en la guia (advertencia, no bloqueo).
    - **Advertencias de contexto** (se registran en la guia, no bloquean): discovery obsoleto (>30 dias), constitucion ausente (si esta `active`, lee sus principios para el checklist).

2. **Recolectar contexto** (en la carpeta de la propuesta **y en su `_archived/`** — `mark-done` mueve alli los completados):
    - `proposal.md` → titulo, estado, prioridad, complejidad, servicios afectados, resumen, alcance, riesgos, criterios de exito.
    - `user-stories.md` → stories con sus criterios de aceptacion.
    - `*_tasks.md` → tabla de tareas: ID, titulo, **Archivos a Modificar**, dependencias, estado.
    - `.quinoto-spec/evidence/{{TASK_ID}}/` → que se verifico por tarea.
    - `delta-specs/*/spec.md` (si existe) → requerimientos ADDED / MODIFIED / REMOVED / RENAMED.
    - `.quinoto-spec/discovery/01-stack-profile.md` → comandos de tests / lint / typecheck.
    - Changelog de la propuesta: `python3 -B agent-dist/skills/quinotospec-contract/contract.py changelog --root . --json` filtrado por el prefijo.

3. **Analizar cambios en git**:
    - Identifica branches por convencion (`git branch --list '*{{PREFIX}}*'`; patrones `feature/TSK-{{PREFIX}}-*` / `bugfix/TSK-{{PREFIX}}-*`).
    - Determina la rama base (`main` o la rama por defecto).
    - Por branch: `git log --oneline`, `git diff --name-status`, `git diff --stat` (rango `{{BASE}}..{{HEAD}}`).
    - **Mapea tarea → commits** por nombre de branch o mencion del ID en el mensaje; sin mapeo → `⚠️`.
    - Compara **archivos declarados vs reales**; marca `⚠️` cualquier archivo real no declarado.
    - Fallback sin branches del prefijo: `git log --since="{{FECHA_DE_CREACION}}" --oneline --name-only` filtrando por archivos declarados.

4. **Generar la guia** `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/CODE_REVIEW_GUIDE.md` (copia extra si `--output`):
    - Autonoma: el reviewer entiende el cambio sin abrir `.quinoto-spec/`.
    - Cita paths exactos; nunca parrafos genericos.
    - Marca cada item verificable como ✅ verificado / ⚠️ advertido / ❌ faltante; **nunca inventes estado**.
    - Estructura (11 secciones): resumen para el reviewer · user stories y criterios · tabla de tareas ejecutadas · cambios en git (commits, archivos, mapeo tarea→commits, comandos para reproducir) · historial del changelog · evidencia de verificacion · delta de requerimientos · como verificar el cambio · **checklist de revision** (criterios, tests, convenciones, archivos declarados vs reales, regresiones, constitucion, deuda tecnica, seguridad, performance) · riesgos y areas sensibles · como reportar feedback (flujo `quinotospec-receive-review`).
    - `--full-diff` incrusta el diff completo; por defecto estadisticas + comandos.

5. **Cierre**:
    - Reporta: path de la guia, secciones, advertencias ⚠️ y pendientes de mapeo.
    - Pasos siguientes: entregar la guia al reviewer → feedback via `quinotospec-receive-review` → `/quinotospec.archive {{PROPOSAL_SLUG}}`.

**Instruccion Final OBLIGATORIA (Changelog):**
Una vez completada la accion, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Titulo de la Accion**: Review Handoff Generated: {{PROPOSAL_SLUG}}
- **Resumen**: Se genero la guia de code review para la propuesta '{{PROPOSAL_SLUG}}' en `CODE_REVIEW_GUIDE.md`. Completitud: {{N}}/{{TOTAL}} tareas. Advertencias: [lista si aplica].

## Manejo de Errores

- Propuesta inexistente → notificar y listar slugs disponibles.
- Tareas pendientes sin `--force` → detener y sugerir `/quinotospec.apply {{NEXT_TASK_ID}}`.
- Repo sin branches del prefijo → fallback por fecha y `⚠️ inspeccion git limitada` en la seccion de git.
- Tarea sin evidencia → `⚠️` en las tablas; no bloquea la generacion.
- `CODE_REVIEW_GUIDE.md` ya existente → sobreescribe y notifica (regenerable por diseno).

## Ejemplos

```
@quinotospec.review-handoff 2026-09-24-add-login
@quinotospec.review-handoff 2026-09-24-add-login --output ./CODE_REVIEW.md --full-diff
@quinotospec.review-handoff 2026-08-01-refactor-api --archived
```
