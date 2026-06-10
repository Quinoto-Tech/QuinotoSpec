---
name: quinotospec-diff
description: Compara versiones de propuestas, user stories y tareas mostrando cambios entre fechas o entre estados.
---

# Skill: quinotospec-diff

Compara diferentes versiones de archivos QuinotoSpec para visualizar cambios a lo largo del tiempo. Util para entender la evolucion de una propuesta, detectar modificaciones no autorizadas o hacer audit trails.

## Instrucciones de Ejecucion

### Paso 1 - Identificar Objetivo de Comparacion
Recibe los siguientes parametros:
- `--file`: Archivo a comparar (ruta relativa dentro de `.quinoto-spec/`)
- `--proposal`: Slug de propuesta (compara todos los archivos de la propuesta)
- `--from`: Version origen (fecha `YYYY-MM-DD` o tag `v1`, `v2`, etc.)
- `--to`: Version destino (fecha o `current`) (default: `current`)
- `--type`: Tipo de diff (`content`, `status`, `structure`) (default: `content`)

### Paso 2 - Obtener Versiones
1. Para comparacion por fechas:
   - Busca en `.quinoto-spec/backups/` si existe backup de esa fecha
   - Si no hay backup, usa git history: `git show HEAD@{YYYY-MM-DD}:path/to/file`
   - Si el archivo no estaba versionado, reporta error
2. Para comparacion por tags:
   - Busca tags en git: `git show v1:path/to/file`
3. Para `current`:
   - Lee el archivo actual del filesystem

### Paso 3 - Generar Diff
Segun el `--type`:
- **content**: Diff linea por linea (formato unified diff)
- **status**: Solo cambios de estado (checkboxes, markers de completion)
- **structure**: Cambios en estructura (headings agregados/eliminados, secciones movidas)

### Paso 4 - Formatear Output
Muestra el diff con:
- Lineas agregadas en verde (`+`)
- Lineas eliminadas en rojo (`-`)
- Lineas contextuales en gris
- Resumen al final: X agregadas, Y eliminadas, Z modificadas

## Ejemplos

### Diff de una Propuesta
```
/quinotospec-diff --proposal auth-jwt --from 2026-01-15
```

### Diff de User Stories
```
/quinotospec-diff --file proposals/auth-jwt/user-stories.md --from 2026-01-15 --to current
```

### Diff de Status (Solo Cambios de Completion)
```
/quinotospec-diff --proposal auth-jwt --type status --from 2026-01-01
```

### Diff entre Dos Branches
```
/quinotospec-diff --file proposals/auth-jwt/proposal.md --from git:main --to git:feature/auth
```

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--file` | Archivo especifico a comparar | No* | N/A |
| `--proposal` | Slug de propuesta (compara todo) | No* | N/A |
| `--from` | Version origen (fecha, tag, o git:branch) | Si | N/A |
| `--to` | Version destino (fecha, tag, git:branch, current) | No | current |
| `--type` | Tipo de diff (content, status, structure) | No | content |
| `--output` | Formato (text, json) | No | text |

*Requiere `--file` o `--proposal` (exclusivos)

## Notas Importantes

- Requiere que el proyecto tenga git inicializado para comparaciones historicas
- Los backups en `.quinoto-spec/backups/` tienen prioridad sobre git history
- Si no se puede obtener una version, reporta claramente que falta
- El diff de `status` es especialmente util para ver progreso de tareas sin ruido de cambios de contenido
- Ejecuta `quinotospec-update-changelog` si el diff genera un reporte guardado
