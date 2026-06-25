---
name: quinotospec-update-changelog
description: Automates updating the changelog — v1 (single-file) or v2 (file-per-entry in changelog/). Auto-detects format.
---

# Skill: quinotospec-update-changelog

Esta skill se encarga de estandarizar la actualización del changelog del proyecto. Soporta dos formatos:

- **v1** (legacy): archivo único `.quinoto-spec/quinoto-spec-changelog.md`
- **v2** (append-only): archivos individuales en `.quinoto-spec/changelog/YYYY-MM-DD-PREFIX-SLUG.md`

La skill detecta automáticamente el formato activo: si existe `.quinoto-spec/changelog/` → v2. Si solo existe `quinoto-spec-changelog.md` → v1.

---

## Auto-detección de Formato

```text
IF .quinoto-spec/changelog/ EXISTS → usar v2
ELSE IF .quinoto-spec/quinoto-spec-changelog.md EXISTS → usar v1
ELSE → preguntar al usuario: "¿Qué formato querés usar? (v1/v2)"
  Si v2 → crear changelog/ + primera entrada
  Si v1 → crear quinoto-spec-changelog.md + primera entrada
```

---

## A. Modo v1 — Archivo Único (Legacy)

### Uso Básico

Cuando necesites actualizar el changelog en formato v1, sigue estas instrucciones:

1. **Identificar Archivo**: El archivo objetivo es `.quinoto-spec/quinoto-spec-changelog.md`.
2. **Leer Contenido**: Lee el archivo actual para identificar la posición de inserción (justo debajo del título principal `# QuinotoSpec Changelog`).
3. **Formato de Entrada**:
    
    ```markdown
    ## [Fecha: YYYY-MM-DD] - [Título de la Acción]
    ### Resumen
    - [Detalle 1]
    - [Detalle 2]
    **Time Saved**: ~{Human Time} (AI: {AI Time} vs Human: {Human Time})
    ```

4. **Cálculo de Métricas**:
    - **AI Time**: Tiempo real de ejecución.
    - **Human Time**: Estimación del tiempo manual (10x-50x AI Time).
    - Añade la línea `**Time Saved**: ...`.

5. **Inserción**:
    - Inserta la nueva entrada al INICIO del archivo, pero SIEMPRE debajo del título h1 `# QuinotoSpec Changelog` y cualquier descripción introductoria.

### Mantenimiento y Orden (v1)

- Si el archivo no tiene el título `# QuinotoSpec Changelog`, créalo al inicio.
- Asegúrate de dejar una línea en blanco entre entradas.

### Ejemplo de Orden Correcto

```markdown
# QuinotoSpec Changelog

## [Fecha: 2026-01-30] - Acción Reciente (Nueva)
...

## [Fecha: 2026-01-29] - Acción Anterior
...
```

---

## B. Modo v2 — Archivos Individuales (Append-Only)

### B.1 — Crear Nueva Entrada

Cuando el proyecto usa formato v2, cada entrada es un archivo separado en `.quinoto-spec/changelog/`:

1. **Verificar directorio**: Asegurarse de que `.quinoto-spec/changelog/` existe. Si no, crearlo (y agregar `.gitignore` con contenido `INDEX.md` dentro).

2. **Generar nombre de archivo**:
   ```
   changelog/YYYY-MM-DD-PREFIX-SLUG.md
   ```
   Donde:
   - `YYYY-MM-DD` = fecha de hoy
   - `PREFIX` = prefijo de la propuesta (del prefix-registry.md), o `ZZZZ` si no hay propuesta asociada
   - `SLUG` = versión corta kebab-case del título (máx 40 chars)

   Ejemplo: `changelog/2026-06-12-AUTH-a1b2-login-endpoint.md`

3. **Usar template**: Copiar `agent-dist/templates/changelog-entry-template.md` como base y reemplazar placeholders:
   - `{{DATE}}` → fecha actual
   - `{{TITLE}}` → título de la acción
   - `{{SUMMARY}}` → bullet points del resumen (cada línea con `- `)
   - `{{HUMAN_TIME}}` → estimación de tiempo humano
   - `{{AI_TIME}}` → tiempo real de ejecución

4. **Escribir archivo**: Crear el archivo en `.quinoto-spec/changelog/`.

5. **Regenerar INDEX.md** (si existe o si se usa `--v2`):
   - Listar todos los archivos `*.md` en `changelog/` excepto `INDEX.md`.
   - Ordenar por fecha descendente (del nombre de archivo).
   - Generar `changelog/INDEX.md` con tabla de contenido:
     ```markdown
     # Changelog INDEX — Generado Automáticamente
     
     **NO EDITAR MANUALMENTE** — Se regenera al agregar entradas.
     
     | Fecha | Título | Prefijo | Archivo |
     |-------|--------|---------|---------|
     | 2026-06-12 | Login Endpoint | AUTH-a1b2 | [ver](2026-06-12-AUTH-a1b2-login-endpoint.md) |
     ```
   - **Importante**: INDEX.md está en `.gitignore` y nunca se commitea.

### B.2 — Flags para Modo v2

| Flag | Descripción |
|------|-------------|
| `--v2` | Forzar modo v2 (incluso si changelog/ no existe) |
| `--no-index` | No regenerar INDEX.md |
| `--prefix PREFIX` | Prefijo para el nombre del archivo (sobrescribe auto-detección) |
| `--slug SLUG` | Slug para el nombre del archivo (sobrescribe auto-generación) |

### B.3 — Ejemplos v2

```text
@quinotospec-update-changelog --title "Task: TSK-AUTH-001 Login" --summary "Implementado login endpoint\nAgregados tests unitarios"
# → changelog/2026-06-12-AUTH-a1b2-login.md

@quinotospec-update-changelog --v2 --title "Hotfix: CORS" --summary "Corregido CORS en producción"
# → changelog/2026-06-12-ZZZZ-hotfix-cors.md

@quinotospec-update-changelog --title "Refactor DB" --summary "Extraída capa de datos" --no-index
# → No regenera INDEX.md
```

---

## C. Flags Compartidos (v1 + v2)

### --dry-run
Simula la inserción sin modificar archivos:
```
/quinotospec-update-changelog --dry-run --title "Mi Accion" --summary "Detalle 1\nDetalle 2"
```
Muestra cómo quedaría la entrada sin escribir. En v2, también muestra el nombre de archivo propuesto.

### --validate-only
Solo valida el formato del changelog existente sin agregar nada:
```
/quinotospec-update-changelog --validate-only
```
Reporta: "X entradas válidas, Y entradas con formato incorrecto"
En v2, valida todos los archivos en `changelog/`.

### --title y --summary
Permite pasar título y resumen como parámetros en lugar de modo interactivo:
```
/quinotospec-update-changelog --title "Task: TSK-AUTH-001" --summary "Implementado login endpoint\nAgregados tests unitarios"
```

---

## D. Validación de Formato

### v1
1. **Verificar estructura**: Cada entrada debe tener:
   - Heading H2 con formato `## [Fecha: YYYY-MM-DD] - Titulo`
   - Sección `### Resumen` con al menos un bullet point
   - Línea de métricas `**Time Saved**:` (opcional pero recomendada)

2. **Si se detectan entradas mal formadas**:
   - Reporta al usuario: "Se encontraron X entradas con formato incorrecto en el changelog"
   - Lista las entradas problemáticas con su línea número
   - Pregunta si desea corregirlas antes de insertar la nueva entrada
   - Si el usuario confirma, corrige las entradas mal formadas primero

3. **Validación de fecha**:
   - La fecha de la nueva entrada no debe ser anterior a la última entrada
   - Si lo es, advierte: "Advertencia: La fecha de hoy es anterior a la última entrada del changelog"

### v2
1. **Verificar estructura**: Cada archivo debe tener:
   - Heading H2 con formato `## [Fecha: YYYY-MM-DD] - Titulo`
   - Sección `### Resumen` con al menos un bullet point
   - Línea de métricas `**Time Saved**:` (opcional pero recomendada)

2. **Validación de nombre de archivo**:
   - Debe coincidir con patrón `YYYY-MM-DD-PREFIX-SLUG.md`
   - La fecha en el nombre debe coincidir con la fecha en el heading

3. **Archivos huérfanos**: Detectar archivos en `changelog/` que no sean `*.md` o que estén vacíos.

---

## E. Manejo de Errores

- Si el directorio/archivo no existe → créalo con el título `# QuinotoSpec Changelog`.
- Si no tienes permisos de escritura → reporta error y sugiere verificar permisos.
- Si el formato de una entrada es ambiguo → pregunta al usuario antes de modificar.
- Si v2 y el nombre de archivo ya existe → agregar sufijo numérico (`-2`, `-3`).
- Si el template `changelog-entry-template.md` no se encuentra → usar formato plano hardcodeado.
