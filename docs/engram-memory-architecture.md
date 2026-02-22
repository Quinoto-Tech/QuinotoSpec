# Arquitectura de Engram (Memoria Persistente)

Engram es el componente de memoria institucional de QuinotoSpec, permitiendo que las decisiones técnicas trasciendan los límites de tokens.

## Esquema de Base de Datos (SQLite + FTS5)

```sql
-- Tabla principal de hallazgos y decisiones
CREATE TABLE engrams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    type TEXT NOT NULL, -- 'decision', 'architecture', 'bug_fix', 'lesson'
    prefix TEXT,        -- Referencia al prefijo de propuesta (ej. AUTH)
    content TEXT NOT NULL,
    hash TEXT UNIQUE    -- Para prevenir duplicados y facilitar la sincronización Git
);

-- Tabla de búsqueda virtual (FTS5) para búsqueda de texto completo
CREATE VIRTUAL TABLE engrams_search USING fts5(
    content,
    prefix,
    content='engrams',
    content_rowid='id'
);

-- Triggers para mantener sincronizada la tabla FTS5
CREATE TRIGGER engrams_ai AFTER INSERT ON engrams BEGIN
  INSERT INTO engrams_search(rowid, content, prefix) VALUES (new.id, new.content, new.prefix);
END;
```

## Protocolo de Sincronización (engram sync)
Para permitir la colaboración, la memoria se exporta a archivos JSON hasheados en `.quinoto-spec/memory/chunks/*.json`.
1. **Export**: Se generan archivos JSON con las nuevas filas de la DB.
2. **Commit**: Se versionan en Git.
3. **Import**: Otros desarrolladores corren `engram import`, que lee los JSON e inyecta las filas faltantes en su SQLite local.

## Integración con Agentes
Cuando el Orchestrator detecta una necesidad de contexto histórico (ej. "por qué usamos JWT en lugar de cookies"), realiza una búsqueda en `engrams_search` e inyecta los resultados más relevantes en la System Prompt del subagente correspondiente.
