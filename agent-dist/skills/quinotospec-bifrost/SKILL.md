---
name: quinotospec-bifrost
description: El Puente Arcoiris — federacion multi-repo con schema federado, git notes sync y context puenteado vigilado por Heimdallr.
---

# Skill: Quinotospec Bifrost — El Puente Arcoiris

> Bifrost une Asgard y Midgard. Este puente une tus repos sin colapsar.

## Cuando usar

- Tienes 2+ repos con `.quinoto-spec/` y necesitas `stack-discovery` consolidado sin copiar archivos
- `sync` actual solo copia estado, no valida schema federado ni contract drift cross-repo
- Como pre-requisito de Mimir multi-repo

## Invocacion

```bash
/quinotospec-bifrost --init                    # crea .quinoto-spec/federation.yaml
/quinotospec-bifrost --sync                    # push/pull git notes + validate
/quinotospec-bifrost --status                  # tabla federada + drift
```

## Comportamiento

### 1. Federation.yaml

```yaml
# .quinoto-spec/federation.yaml
federation: quinoto-falange
version: 1
repos:
  - path: ../quinotospec-auth
    role: auth
    schema: .quinoto-spec/schema.yaml
  - path: ../quinotospec-pay
    role: payments
    schema: .quinoto-spec/schema.yaml
bridge:
  discovery: stack-discovery  # consolida 01-stack-profile.md de cada repo
  specs: federated            # specs/<domain>/spec.md por repo, índice federado
  changelog: aggregated       # changelog-view --federated
```

Bifrost no copia `specs/` — genera `federation/index.md` con links y valida que no haya `REQUIREMENT` duplicado cross-repo (via Valkyrie scoring si conflicto).

### 2. Sync

- Usa `git notes --ref=refs/notes/quinotospec-events` (ya usado por claim-task) + `git push origin refs/notes/quinotospec-events`
- `quinotospec-sync` delegado para estado, Bifrost añade validacion:
  - `jormungandr --federated` detecta ciclo cross-repo `auth requires payments requires auth`
  - `huginn-muninn --federated` reporta S_final por repo + agregado

### 3. Status federado

```
Repo      | S_final | Propuestas | Drift | Bridge
auth      | 0.42    | 2 activas  | OK    | synced 2m ago
payments  | 0.67    | 1 bloqueada| WARN contract drift v2/auth | sync needed
```

## Reglas

- Nunca rompe Asgard (repo central) — si un repo no tiene `.quinoto-spec/`, Bifrost lo inicializa via `specs-init` en modo federado, no overwrite
- Requiere `federation.yaml` versionado; cambios requieren `valkyrie` rank si hay conflicto de dominio
