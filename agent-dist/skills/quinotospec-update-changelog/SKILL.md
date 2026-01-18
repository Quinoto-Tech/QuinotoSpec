---
name: Quinotospec Update Changelog
description: Automates updating the docs/quinoto-spec-changelog.md file with a consistent format.
---

# Quinotospec Update Changelog

Esta skill se encarga de estandarizar la actualización del archivo de changelog del proyecto.

## Uso

### A. Agregar Nueva Entrada (Default)

Cuando necesites actualizar el changelog, sigue ESTRICTAMENTE estas instrucciones:

1.  **Identificar Archivo**: El archivo objetivo es siempre `docs/quinoto-spec-changelog.md`.
2.  **Leer Contenido**: Lee el archivo actual para no sobrescribir entradas recientes si no es necesario.
3.  **Formato de Entrada**:
    
    ```markdown
    ## [Fecha: YYYY-MM-DD] - [Título de la Acción]
    ### Resumen
    - [Detalle 1]
    - [Detalle 2]
    ```

4.  **Cálculo de Métricas (Time Saved)**:
    - **AI Time**: Estima el tiempo que te tomó ejecutar esta tarea (ej. "30s", "2m").
    - **Human Time**: Estima el tiempo que le hubiera tomado a un desarrollador senior manual (ej. "1h", "4h"). *Regla general: Tareas simples = 10x AI, Tareas complejas = 20-50x AI.*
    - **Calculo**: Añade una línea que diga `**Time Saved**: ~{Human Time} (AI: {AI Time} vs Human: {Human Time})`.

5.  **Ejecución**:
    - Obtén la fecha actual.
    - Genera el bloque markdown incluyendo la línea de métricas.
    - Añádelo al final del archivo `docs/quinoto-spec-changelog.md`.

### B. Compactar Changelog (Maintenance)

Cuando el changelog sea demasiado extenso o el usuario lo solicite explícitamente:

1.  **Analizar**: Lee todo el contenido de `docs/quinoto-spec-changelog.md`.
2.  **Resumir**:
    - Agrupa hitos antiguos (más de 1 mes o hitos menores) en bloques consolidados.
    - Mantén las entradas recientes (últimas 24-48h o tareas activas) con todo su detalle.
    - Elimina redundancias.
3.  **Sobrescribir**: Reemplaza el contenido del archivo con la versión optimizada.

## Ejemplo

Si la acción fue "Discovery Executed":

```markdown
## [Fecha: 2024-05-20] - Discovery Executed
### Resumen
- Se exploró el proyecto y se generaron los archivos de especificación en .quinoto-spec/discovery/
- **Time Saved**: ~4h (AI: 2m vs Human: 4h)
```
