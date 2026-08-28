---
name: quinotospec-mimir
description: La Cabeza Sabia — indice BM25 cita-exacta sobre discovery/specs/proposals. Responde por que con file:line, sin LLM externo.
---

# Skill: Quinotospec Mimir — La Cabeza Sabia (BM25)

> Cabeza de Mimir bajo Yggdrasil: memoria viva sin alucinacion. Solo stdlib, offline.

## Cuando usar

- `¿por que se decidio X?` — antes de `create-proposal` evita duplicar
- `mimir --trace PREFIX` — linaje completo de un prefijo
- Como gate de `create-proposal`: si ya existe decision similar en `_archived/` → sugiere reutilizar

## Invocacion

```bash
/quinotospec-mimir "por que TOTP para 2FA?" --cite
/quinotospec-mimir --trace AUTH-a1b2
/quinotospec-mimir --reindex
/quinotospec-mimir --check   # valida indice stale?
```

## Comportamiento

### 1. Index (BM25 puro, sin deps externas)

Fuente: `.quinoto-spec/discovery/*.md + specs/**/*.md + proposals/**/proposal.md + proposals/**/_archived/** + docs/ARCHITECTURE.md + CHANGELOG.md + schema.yaml`

Chunking: por `### Requirement:` / `## ADDED|MODIFIED` / `##` heading — cada chunk guarda `file:line_start-line_end` + `prefix/slug/fecha` (frontmatter).

Indice: `mimir-index.json` en `.quinoto-spec/mimir/` (gitignored, regenerable) + `mimir-sources.json` (hashes SHA1 por archivo para invalidacion incremental).

Formula BM25: `k1=1.5, b=0.75`, tokeniza `re.split(r"\W+", lower)`, sin stopwords externas (lista corta inline ES/EN).

Implementacion: `agent-dist/skills/quinotospec-mimir/index.py` (stdlib only) y `search.py`.

No embeddings, no red, no API.

### 2. Search --cite

```
query: "TOTP 2FA"
1. [score 4.21] proposals/2026-06-11-auth-jwt/delta-specs/auth/spec.md:12-18 (AUTH-a1b2, 2026-06-11)
   > ### Requirement: Two-Factor Authentication
   > The system SHALL support TOTP...

2. [score 2.03] discovery/07-findings-and-recommendations.md:42 (2026-08-28)
   > Recommendation: Add TOTP...
```

Siempre cita verbatim + `file:line`, nunca parafrasea sin fuente.

### 3. Trace

`--trace AUTH-a1b2` lista cronologico: `proposal.md -> delta-specs -> user-stories -> changelog entry -> archive merge -> specs/`

### 4. Gate create-proposal

Si score top1 > umbral 2.5 y es una decision con `Reason:` contradictoria, Mimir advierte:

```
⚠️  Decision similar encontrada: AUTH-a1b2 TOTP (2026-06-11) con Reason: compliance
   ¿Quieres MODIFIED en vez de ADDED? (Was: ...)
```

## Reglas

- Offline, stdlib only, `mimir-index.json` gitignored (como `changelog/INDEX.md`)
- Nunca inventa — si no hay hit >1.0, responde "No encontrado en indice (reindex?)"
- Reindex incremental: solo archivos con hash cambiado (usa `mimir-sources.json`)

## Estructura

```
agent-dist/skills/quinotospec-mimir/
├── SKILL.md
├── index.py   # genera .quinoto-spec/mimir/index.json
└── search.py  # BM25 query + --cite / --trace
```
