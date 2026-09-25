---
name: quinotospec-rules-enforce
description: Ejecuta y hace cumplir las reglas definidas en quinotospec-rules.md. Detiene workflows que violen las reglas.
---

# Skill: Quinotospec Rules Enforce

Usa esta skill para verificar cumplimiento de reglas antes de ejecutar acciones críticas. La validación de formato, IDs, estados y changelog se delega en `quinotospec-contract`; esta skill coordina las reglas y clasifica sus severidades.

## Reglas a Verificar

### 1. Changelog - Siempre actualizar

- **Verificación**: Ejecuta `python3 agent-dist/skills/quinotospec-contract/contract.py changelog --root . --json`.
- **Check**: ¿La última entrada es de hace más de 24h o no existe una fuente de changelog?
- **Acción si falla**: Advertir que se necesita actualizar el changelog

### 2. Prefix Registry - No inventar prefijos

- **Verificación**: Lee `.quinoto-spec/prefix-registry.md`
- **Check**: ¿El prefijo ya existe en la tabla?
- **Acción si falla**: Detener y pedir registro del prefijo primero

### 3. Product Agreement Check (BLOQUEANTE)

- **Verificación**: Lee `.quinoto-spec/discovery/08-product-and-agreements.md`
- **Check**: ¿Tiene contenido más allá de headers?
- **Acción si falla**: **DETENER** ejecución - no se puede proceder sin DoR/DoD

### 4. No Sobreescribir Specs

- **Verificación**: Al escribir en archivos `user-stories.md` o `*_tasks.md`
- **Check**: ¿El archivo ya existe?
- **Acción si falla**: Usar merge inteligente, nunca overwrite

### 5. Validación de Estado Antes de Archivar

- **Verificación**: Al ejecutar archive workflow
- **Check**: ¿El estado en proposal.md es `✅ Completada`?
- **Acción si falla**: Advertir antes de proceder

### 6. Convención de Archivado

- **Verificación**: Al mover archivos a `_archived/`
- **Check**: ¿Existe la carpeta `_archived/`?
- **Acción si falla**: Crear la carpeta antes de mover

### 7. Branch Naming Convention

- **Verificación**: Al crear branches
- **Check**: ¿El branch sigue `feature/{{ID}}-descripcion`?
- **Acción si falla**: Corregir nombre antes de crear

### 8. Aprobación de Config Crítica

- **Verificación**: Al modificar archivos de configuración
- **Check**: ¿Es uno de los archivos protegidos?
- **Acción si falla**: Pedir confirmación explícita al usuario

### 9-17. Gates Engineering y Constitution

- Ejecuta el contrato canónico antes de las reglas 9-12.
- Verifica la protección de `_archived/`, el preflight de refactor y el monitor Blood-Bond según el workflow que se está ejecutando.
- Para código de producción, exige RED de `quinotospec-tdd` antes de implementar.
- Ante fallos, exige `quinotospec-debug` antes de un hotfix.
- Antes de cambiar estados, exige `quinotospec-verify-before-done` con evidencia fresca.
- Si existe `constitution.md` activa, verifica compliance en Apply, Review y Archive.
- No declares una regla como ejecutable si solo realizaste una lectura manual del prompt.

## Dispatcher ejecutable

Usa el entrypoint read-only para gates observables:

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py \
  --root . --profile target --action preflight --mode strict --check all --json
```

Flags disponibles: `--root`, `--profile package|target`, `--action`, `--mode strict|warning`, `--check`, `--path`, `--branch`, `--approved-critical`, `--write-mode`, `--evidence-dir`, `--task-id`, `--require-evidence`, `--approval-dir`, `--approval-id`, `--approval-subject`, `--approval-action`, `--require-approval`, `--approval-max-age` y `--json`.

El dispatcher delega IDs, estados, prefijos y changelog al contrato canónico. No crea archivos, no ejecuta el stack y no modifica el proyecto. Las reglas sin evidencia verificable o que dependen de aprobación humana se reportan como `deferred`, nunca como `pass`.

Para evidencia técnica usa `--check tdd,debug,verify-before-done --require-evidence --task-id {{TASK_ID}} --evidence-dir .quinoto-spec/evidence`. El dispatcher delega la validación de estructura/frescura a `evidence_validate.py`; no convierte un registro ausente en un pass.

Para una decisión humana usa `--check human-approval --require-approval --approval-id {{APPROVAL_ID}} --approval-subject {{SUBJECT}} --approval-action {{ACTION}} --approval-dir .quinoto-spec/approvals`. El dispatcher delega la validación a `approval_validate.py`; solo un registro `approved`, fresco y exactamente scoped habilita el gate. `--approved-critical` se conserva para compatibilidad con el check legacy y no sustituye un registro cuando se exige `human-approval`.

Registro mínimo esperado en `.quinoto-spec/approvals/{{APPROVAL_ID}}.json`:

```json
{
  "schema_version": 1,
  "approval_id": "APR-BASE-a1b2-001",
  "decision": "approved",
  "subject": ".quinoto-spec/sprints/base-config.yml",
  "action": "apply",
  "requested_by": "developer",
  "decided_by": "owner",
  "decided_at": "2026-09-24T20:00:00+00:00",
  "rationale": "Reviewed and explicitly approved for this scope.",
  "scope": "single configuration change"
}
```

## Comportamiento

- **Modo strict** (default): falla ante violaciones bloqueantes y warnings
- **Modo warning**: reporta warnings sin bloquear
- JSON estable: `passed`, `blocking`, `checks`, `violations` y `deferred`
- Código `0`: sin violaciones aplicables; `1`: violación; `2`: error operativo

## Uso rápido

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/rules_enforce.py \
  --root . --profile target --action preflight --mode strict \
  --check changelog,prefix,product-agreement --json
```
