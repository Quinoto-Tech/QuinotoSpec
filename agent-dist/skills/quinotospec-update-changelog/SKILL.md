---
name: quinotospec-update-changelog
description: Automates updating the `.quinoto-spec/quinoto-spec-changelog.md` file with entries appearing from top to bottom (newest first).
---

# Skill: quinotospec-update-changelog

Esta skill se encarga de estandarizar la actualización del archivo de changelog del proyecto, asegurando que las entradas más recientes aparezcan siempre en la parte superior.

## Uso

### A. Agregar Nueva Entrada (Newest First)

Cuando necesites actualizar el changelog, sigue ESTRICTAMENTE estas instrucciones para mantener el orden "de arriba hacia abajo" (lo más nuevo arriba):

1.  **Identificar Archivo**: El archivo objetivo es siempre `.quinoto-spec/quinoto-spec-changelog.md`.
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

## Validacion de Formato

Antes de insertar una nueva entrada, valida que las entradas existentes sigan el formato correcto:

1. **Verificar estructura**: Cada entrada debe tener:
   - Heading H2 con formato `## [Fecha: YYYY-MM-DD] - Titulo`
   - Seccion `### Resumen` con al menos un bullet point
   - Linea de metricas `**Time Saved**:` (opcional pero recomendada)

2. **Si se detectan entradas mal formadas**:
   - Reporta al usuario: "Se encontraron X entradas con formato incorrecto en el changelog"
   - Lista las entradas problematicas con su linea numero
   - Pregunta si desea corregirlas antes de insertar la nueva entrada
   - Si el usuario confirma, corrige las entradas mal formadas primero

3. **Validacion de fecha**:
   - La fecha de la nueva entrada no debe ser anterior a la ultima entrada
   - Si lo es, advierte: "Advertencia: La fecha de hoy es anterior a la ultima entrada del changelog"

## Flags Adicionales

### --dry-run
Simula la insercion sin modificar el archivo:
```
/quinotospec-update-changelog --dry-run --title "Mi Accion" --summary "Detalle 1\nDetalle 2"
```
Muestra como quedaria la entrada sin escribir al archivo.

### --validate-only
Solo valida el formato del changelog existente sin agregar nada:
```
/quinotospec-update-changelog --validate-only
```
Reporta: "X entradas validas, Y entradas con formato incorrecto"

### --title y --summary
Permite pasar titulo y resumen como parametros en lugar de modo interactivo:
```
/quinotospec-update-changelog --title "Task: TSK-AUTH-001" --summary "Implementado login endpoint\nAgregados tests unitarios"
```

## Manejo de Errores

- Si el archivo no existe → crealo con el titulo `# QuinotoSpec Changelog`
- Si no tienes permisos de escritura → reporta error y sugiere verificar permisos
- Si el formato de una entrada es ambiguo → pregunta al usuario antes de modificar
