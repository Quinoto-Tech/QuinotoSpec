---
name: quinotospec-validate
description: Ejecuta checks de validación del estado QuinotoSpec y del contrato de artefactos antes de workflows críticos.
---

# Skill: QuinotoSpec Validate

Usa esta skill como precondición antes de crear o modificar artefactos.

## Preflight

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
```

El comando valida el contrato común de proposals, stories, tasks, IDs, estados y changelog. Debe ejecutarse antes de `create-proposal`, `create-user-stories`, `create-tasks`, `apply` y `archive`.

## Checks del proyecto

1. `.quinoto-spec/discovery/` existe y contiene los ocho archivos esperados.
2. `08-product-and-agreements.md` tiene contenido real de DoR/DoD.
3. `.quinoto-spec/prefix-registry.md` existe y no contiene prefijos duplicados.
4. Existe al menos una fuente de changelog: `.quinoto-spec/changelog/` (v2) o `.quinoto-spec/quinoto-spec-changelog.md` (v1 legacy). v2 es el formato canónico.
5. Las proposals activas tienen proposal.md, prefijo registrado, fecha y estado válido.
6. Cada task tiene una relación explícita con una story existente.
7. Los archivos de `_archived/` no se modifican durante un workflow normal.
8. El discovery no supera 30 días sin una alerta.
9. Si `.quinoto-spec/constitution.md` existe, valida que no tenga placeholders sin resolver y registra si está `draft` o `active`; si está activa, sus gates son obligatorios.

## Comportamiento

- Errores del contrato o de los checks obligatorios: detener el workflow.
- Warnings: informar y pedir confirmación en modo estricto.
- Changelog: usar siempre `quinotospec-update-changelog`; nunca borrar entradas v2.
- Artefactos archivados: solo lectura; cualquier restauración requiere aprobación explícita.
- Decisiones humanas: cuando el gate sea aplicable, valida el registro estructurado con `rules_enforce.py --require-approval`; no acepta `--approved-critical` como sustituto.

## Flags

- `--quick`: discovery, prefijos y contrato básico.
- `--full`: todos los checks del proyecto y del contrato.
- `--strict`: convierte warnings en bloqueo.
- `--json`: salida estable para CI.
- `--fix`: solo corrige estructura segura; nunca reescribe contenido legacy sin confirmación.

## Salida

```json
{
  "valid": true,
  "blocking": false,
  "errors": [],
  "warnings": [],
  "contract_version": 1
}
```

## Checksums

En modo full, los checksums son opcionales y deben generarse con un algoritmo seguro documentado. No se considera evidencia suficiente un checksum ausente; reportar el estado y continuar solo con confirmación cuando la política del proyecto lo permita.
