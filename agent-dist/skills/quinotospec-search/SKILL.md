---
name: quinotospec-search
description: Búsqueda filtrada sobre el índice BM25 de Mimir con citas file:line, filtros por tipo, prefijo, fecha y estado.
---

# Skill: quinotospec-search

Busqueda inteligente y filtrada dentro de `.quinoto-spec/` y del changelog del proyecto. **Backend unico: el indice BM25 de `quinotospec-mimir`** — esta skill no mantiene un motor paralelo, solo agrega filtros que el indice no aplica por si solo.

> Fuente de verdad del scoring: `agent-dist/skills/quinotospec-mimir/search.py` (BM25, `k1=1.5`, `b=0.75`, solo stdlib). Esta skill construye/usa `.quinoto-spec/mimir/index.json` y filtra `chunk` por metadatos.

## Cuando usar

- Buscar un termino en discovery, specs, propuestas y changelog con cita `file:line`
- Localizar tareas o stories por prefijo antes de abrir una propuesta
- Encontrar decisiones previas (evita duplicar con `mimir --trace`)

## Invocacion

```bash
python3 -B agent-dist/skills/quinotospec-search/search.py --root . --query "autenticacion"
python3 -B agent-dist/skills/quinotospec-search/search.py --root . --query "login" --type task
python3 -B agent-dist/skills/quinotospec-search/search.py --root . --query "endpoint" --prefix AUTH --since 2026-01-01
python3 -B agent-dist/skills/quinotospec-search/search.py --root . --query "security" --json --limit 5
python3 -B agent-dist/skills/quinotospec-search/search.py --root . --query "criterios" --cite
```

## Parametros

| Parametro | Descripcion | Default |
|-----------|-------------|---------|
| `--query TEXT` | Texto a buscar (tambien acepta la query como posicional) | requerido |
| `--type` | `all`, `proposal`, `task`, `story`, `discovery`, `spec` | `all` |
| `--prefix` | Prefijo de propuesta (ej. `AUTH`, `PAY`) | — |
| `--since` | Fecha minima `YYYY-MM-DD` (usa metadato `fecha` o prefijo del nombre) | — |
| `--status` | Estado declarado (`En Curso`, `Completada`, `Archivada`) | — |
| `--limit N` | Maximo de resultados | `10` |
| `--cite` | Incluye hasta 6 lineas de contexto por resultado | off |
| `--json` | Salida JSON con estructura estable | off |

## Comportamiento

1. **Indice**: si `.quinoto-spec/mimir/index.json` no existe, ejecuta `quinotospec-mimir/index.py` una vez para construirlo. Si sospechas staleness, corre `index.py --full`.
2. **Scoring**: delega en `quinotospec-mimir/search.py` (`bm25_search`), sin re-tokenizar el corpus por su cuenta.
3. **Filtros**: se aplican sobre los metadatos del `chunk` (archivo, prefijo, fecha) y, para `--status`, sobre el `**Estado:**` del archivo de la propuesta.
4. **Salida**: `file:line_start-line_end`, score y metadatos en texto; array JSON con `schema_version: 1` en modo `--json`.

## Notas

- La busqueda es case-insensitive; los terminos siguen la tokenizacion BM25 de Mimir (sin stopwords externas).
- Si `.quinoto-spec/` no existe, el indice queda vacio: ejecuta `@quinotospec.discovery` primero.
- Para linaje de un prefijo (propuesta → stories → tareas → changelog) usa `/quinotospec-mimir --trace PREFIX`.
- `INDEX.md` y `.quinoto-spec/mimir/` son artefactos regenerables, no fuente de verdad.
