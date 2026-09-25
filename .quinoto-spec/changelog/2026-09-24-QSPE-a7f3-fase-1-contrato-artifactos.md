---
date: 2026-09-24
prefix: QSPE-a7f3
slug: fase-1-contrato-artifactos
type: maintenance
---

## [2026-09-24] - Fase 1: contrato canónico de artefactos

### Resumen
- Se agregó `quinotospec-contract/contract.py`, parser read-only con modelo normalizado para proposals, stories, tasks, IDs, estados y changelog v1/v2.
- Se añadieron templates canónicos para user stories y tasks, contrato documental y fixtures para formatos modernos y legacy.
- Se actualizaron producers, validators, status, mark-done, suggest-next, archive, rules y consumidores Python para usar el contrato común.
- Se integraron la suite Artifact Contract y Skills Nordic al runner principal; ahora `validate-all.sh` incluye el gate determinista del contrato.
- Se unificó el changelog v2 como formato canónico, manteniendo v1 como adaptador y reversiones append-only.

**Tiempo Ahorrado**: ~6h (IA: ~45min vs Humano: ~6h)
