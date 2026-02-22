---
name: Memory Search
description: Permite buscar decisiones técnicas y lecciones aprendidas en la base de datos Engram.
trigger: ["memory", "remember", "search memory", "qué sabes de", "busqueda en memoria"]
scope: ["**/*"]
tools: ["run_command", "view_file"]
---

# Skill: Memory Search

Esta habilidad permite consultar la memoria institucional de QuinotoSpec para recuperar contexto de decisiones pasadas, soluciones a bugs y arquitectura.

## Instrucciones de Uso

Cuando el usuario solicita "recordar" algo o buscar en la memoria técnica:

1.  **Verificar persistencia**: Si el archivo `engram.db` no existe, infórmalo al usuario y ofrece inicializarlo usando:
    ```bash
    python agent-dist/skills/quinotospec-memory-search/init_memory.py
    ```
2.  **Identificar el término de búsqueda**: Extrae las palabras clave de la consulta del usuario.
3.  **Ejecutar el script**:
    ```bash
    python agent-dist/skills/quinotospec-memory-search/search.py "término"
    ```
3.  **Procesar resultados**: Lee la salida del script e inyéctala en la respuesta para el usuario, citando las fechas y tipos de registros encontrados.

## Casos de Uso
- "¿Por qué decidimos usar este patrón de diseño?"
- "¿Cómo resolvimos el bug de los subagentes la semana pasada?"
- "Busca en la memoria todo lo relacionado con el prefijo AUTH."
