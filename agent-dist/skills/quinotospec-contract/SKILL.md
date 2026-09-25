---
name: quinotospec-contract
description: Define y valida el contrato común de proposals, user stories, tasks, IDs, estados y changelog con compatibilidad legacy.
---

# Skill: QuinotoSpec Contract

Esta skill es la fuente de verdad operativa para leer y validar artefactos QuinotoSpec sin depender de interpretación ad hoc de cada workflow.

## Contrato canónico

- `proposal.md`: `**ID:**`, `**Prefijo:**`, `**Fecha de Creación:**`, `**Estado:**`, `**Prioridad:**`, `**Complejidad:**` y `**Servicios Afectados:**`.
- `user-stories.md`: tabla con `ID`, `User Story`, `Criterios de Aceptación`, `Prioridad`, `Estimación` y `Servicio`.
- `*_tasks.md`: tabla con `ID`, `Tipo`, `Título`, `Descripción`, `Historia Relacionada`, `Servicio`, `Archivos a Modificar`, `Estimación`, `Prioridad`, `Dependencias` y `Estado`.
- IDs canónicos: `US-MNEM-suffix-NNN` y `TSK-MNEM-suffix-NNN`, donde `MNEM` contiene cuatro letras y `suffix` cuatro caracteres alfanuméricos.
- Estados canónicos: `proposed`, `in_progress`, `pending`, `completed`, `blocked`, `cancelled` y `archived`.
- Changelog: v2 en `.quinoto-spec/changelog/`; v1 se acepta como entrada legacy.

## Comandos

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py inspect --root . --json
python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
python3 agent-dist/skills/quinotospec-contract/contract.py changelog --root . --json
```

El comando `validate` es read-only. Devuelve código 1 ante errores y también ante warnings cuando se usa `--strict`.

## Compatibilidad legacy

El parser acepta bloques `## US-...` y `## TSK-...`, tablas antiguas, IDs cortos como `TSK-AUTH-001`, estados expresados como `**Estado**: completada` y checkboxes. `all_tasks.md` se reconoce como índice derivado y no duplica tareas primarias.

No se deben reescribir automáticamente los artefactos legacy. La normalización ocurre en la lectura y en la salida JSON; la migración de contenido se realiza mediante merge explícito.

## Integración

- `quinotospec-syntax-validate` usa este contrato para decidir si un artefacto es válido.
- `quinotospec-validate` lo usa antes de workflows de creación o modificación.
- `status`, `suggest-next`, `mark-done` y `archive` deben interpretar IDs y estados desde la misma API.
- `update-changelog` y `changelog-view` deben consultar el parser para evitar divergencias v1/v2.
- El rollback nunca elimina una entrada v2: agrega una entrada de reversión o estado equivalente.

## Salida

El JSON incluye `raw_id`, `canonical_id`, `prefix`, `status`, `source_path`, `source_format`, línea y diagnósticos. Los warnings no bloquean por defecto; los errores sí.
