---
name: Quinotospec Update Changelog
description: Automates updating the docs/quinoto-spec-changelog.md file with entries appearing from top to bottom (newest first).
---

# Quinotospec Update Changelog

Esta skill se encarga de estandarizar la actualización del archivo de changelog del proyecto, asegurando que las entradas más recientes aparezcan siempre en la parte superior.

## Uso

### A. Agregar Nueva Entrada (Newest First)

Cuando necesites actualizar el changelog, sigue ESTRICTAMENTE estas instrucciones para mantener el orden "de arriba hacia abajo" (lo más nuevo arriba):

1.  **Identificar Archivo**: El archivo objetivo es siempre `docs/quinoto-spec-changelog.md`.
2.  **Leer Contenido**: Lee el archivo actual para identificar la posición de inserción (justo debajo del título principal `# QuinotoSpec Changelog`).
3.  **Formato de Entrada**:
    
    ```markdown
    ## [Fecha: YYYY-MM-DD] - [Título de la Acción]
    ### Resumen
    - [Detalle 1]
    - [Detalle 2]
    **Time Saved**: ~{Human Time} (AI: {AI Time} vs Human: {Human Time})
    ```

4.  **Cálculo de Métricas**:
    - **AI Time**: Tiempo real de ejecución.
    - **Human Time**: Estimación del tiempo manual (10x-50x AI Time).
    - Añade la línea `**Time Saved**: ...`.

5.  **Inserción**:
    - Inserta la nueva entrada al INICIO del archivo, pero SIEMPRE debajo del título h1 `# QuinotoSpec Changelog` y cualquier descripción introductoria.
    - Esto garantiza que al abrir el archivo, el usuario vea lo último que se hizo inmediatamente.

### B. Mantenimiento y Orden

- Si el archivo no tiene el título `# QuinotoSpec Changelog`, créalo al inicio.
- Asegúrate de dejar una línea en blanco entre entradas.

## Ejemplo de Orden Correcto

```markdown
# QuinotoSpec Changelog

## [Fecha: 2026-01-30] - Acción Reciente (Nueva)
...

## [Fecha: 2026-01-29] - Acción Anterior
...
```
