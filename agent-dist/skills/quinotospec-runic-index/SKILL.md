---
name: Quinotospec Runic Index
description: Motor de indexación semántica para Runic Memory. Convierte la codebase y especificaciones en embeddings para búsqueda vectorial.
---

# Quinotospec Runic Index

Esta skill es el motor encargado de transformar el conocimiento del proyecto en una representación vectorial almacenable en ChromaDB.

## 📋 Responsabilidades

1. **Escaneo de Archivos**: Identificar archivos relevantes (código y documentación) ignorando archivos de sistema o temporales.
2. **Chunking Semántico**: Dividir archivos grandes en fragmentos que conserven su significado (clases, funciones, bloques H2/H3).
3. **Generación de Embeddings**: Traducir texto a vectores usando el modelo configurado.
4. **Persistencia**: Guardar y actualizar los vectores en `.quinoto-spec/memory/`.

## 🛠️ Requisitos Técnicos

- **Base de Datos**: ChromaDB (local).
- **Procesamiento**: Script de Python `runic_indexer.py` para el manejo de colecciones y chunking.
- **Ubicación de Memoria**: `${PROJECT_ROOT}/.quinoto-spec/memory/`.

## 🧩 Lógica de Chunking (TSK-RUN-002)

La skill utiliza una fragmentación inteligente para no perder el contexto:
- **Markdown**: Divide por encabezados (`#`, `##`, `###`).
- **Python**: Divide por definiciones de `class` y `def`.
- **JavaScript/TS**: Divide por `function`, `class` y `const` arrows.

## 📦 Persistencia (TSK-RUN-003)

Se utiliza `chromadb.PersistentClient` para asegurar que los vectores se guarden en disco dentro de la carpeta `.quinoto-spec/memory/`. Los fragmentos se identifican de forma única mediante `archivo_path_indice`.

## 🚀 Uso del Script

```bash
python3 agent-dist/skills/quinotospec-runic-index/runic_indexer.py [PATH_AL_PROYECTO]
```
