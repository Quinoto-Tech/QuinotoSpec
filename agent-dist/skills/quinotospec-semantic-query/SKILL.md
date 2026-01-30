---
name: Quinotospec Semantic Query
description: Interfaz de consulta semántica para Runic Memory. Recupera fragmentos de código y documentación basados en significado.
---

# Quinotospec Semantic Query

Esta skill permite al agente consultar la memoria semántica del proyecto para obtener contexto relevante sin necesidad de conocer rutas exactas.

## 📋 Responsabilidades

1. **Interfaz de Búsqueda**: Proveer un comando para buscar por lenguaje natural.
2. **Filtrado Semántico**: Consultar ChromaDB y obtener los fragmentos con mayor similitud de coseno.
3. **Formateo de Contexto**: Entregar los resultados en un formato Markdown limpio que incluya la fuente y el tipo de contenido.

## 🛠️ Requisitos Técnicos

- **Base de Datos**: ChromaDB (lectura desde `.quinoto-spec/memory/`).
- **Procesamiento**: Script `runic_searcher.py`.
- **Salida**: Inyección de bloques de código y texto en el contexto del agente.

## 🚀 Uso del Script

```bash
python3 agent-dist/skills/quinotospec-semantic-query/runic_searcher.py "tu consulta aquí" --top_k 5
```
