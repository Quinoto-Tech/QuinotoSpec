---
name: Engram Memory Management
description: Permite buscar decisiones técnicas y lecciones aprendidas en la base de datos Engram.
trigger: ["memory", "remember", "search memory", "qué sabes de", "busqueda en memoria"]
scope: ["**/*"]
tools: ["run_command", "view_file"]
---

# Skill: Engram Memory Management

Esta habilidad permite gestionar la memoria institucional de QuinotoSpec, permitiendo tanto grabar nuevos hallazgos como recuperar contexto de decisiones pasadas, soluciones a bugs y arquitectura.

## Instrucciones de Uso

### A. Grabar en Memoria
Cuando realices una decisión técnica importante, resuelvas un bug complejo o identifiques una lección aprendida:

1.  **Ejecutar el script de grabado**:
    ```bash
    python agent-dist/skills/quinotospec-memory-search/record_memory.py --type "decision|architecture|bug_fix|lesson" --content "Descripción clara" --prefix "OPCIONAL"
    ```

### B. Recuperar de Memoria
Cuando el usuario solicita "recordar" algo o buscar en la memoria técnica:

1.  **Verificar persistencia**: Si el archivo `engram.db` no existe, infórmalo al usuario y ofrece inicializarlo usando el workflow `memory-init`.
2.  **Identificar el término de búsqueda**: Extrae las palabras clave de la consulta del usuario.
3.  **Ejecutar el script**:
    ```bash
    python agent-dist/skills/quinotospec-memory-search/search.py "término"
    ```
4.  **Procesar resultados**: Lee la salida del script e inyéctala en la respuesta para el usuario, citando las fechas y tipos de registros encontrados.

