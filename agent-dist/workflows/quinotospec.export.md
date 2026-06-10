---
description: Exportar propuestas, tareas y user stories a formatos externos (JSON, CSV, Markdown consolidado)
---

# Workflow: Export

Exporta datos de `.quinoto-spec/` a formatos externos para integracion con herramientas de gestion de proyectos (Jira, GitHub Projects) o para reportes.

## Precondiciones

- El proyecto tiene `.quinoto-spec/` con al menos una propuesta
- Se tiene permisos de escritura en el directorio de salida

## Instrucciones

### Paso 1 - Determinar Alcance de Exportacion
Recibe parametros:
- `--proposal`: Slug de propuesta especifica (default: todas)
- `--format`: Formato de salida (`json`, `csv`, `markdown`, `jira-csv`) (default: `json`)
- `--output`: Directorio o archivo de salida (default: `.quinoto-spec/exports/`)
- `--include`: Que exportar (`all`, `proposals`, `tasks`, `stories`) (default: `all`)

### Paso 2 - Recopilar Datos
Segun el alcance:

**Propuestas:**
- Lee cada `proposal.md` en `.quinoto-spec/proposals/*/`
- Extrae: slug, titulo, estado, fecha creacion, prefijo, descripcion, archivos afectados

**User Stories:**
- Lee cada `user-stories.md`
- Extrae: US_ID, titulo, descripcion, criterios de aceptacion, estado

**Tareas:**
- Lee cada `*_tasks.md`
- Extrae: TASK_ID, titulo, descripcion, estado, dependencias, criterios

### Paso 3 - Transformar segun Formato

**JSON:**
```json
{
  "export_date": "2026-04-15T10:30:00Z",
  "quinotospec_version": "2.0.0",
  "proposals": [
    {
      "slug": "auth-jwt",
      "title": "Implementar Auth JWT",
      "status": "En Curso",
      "prefix": "AUTH-a1b2",
      "created": "2026-04-01",
      "user_stories": [...],
      "tasks": [...]
    }
  ]
}
```

**CSV:**
```csv
type,id,title,status,proposal,description
proposal,auth-jwt,Implementar Auth JWT,En Curso,AUTH-a1b2,...
story,US-AUTH-001,Login endpoint,En Curso,auth-jwt,...
task,TSK-AUTH-001,Crear endpoint POST /login,Completada,auth-jwt,...
```

**Jira CSV (para import en Jira):**
```csv
Summary,Issue Type,Description,Priority,Status,Labels
"Implementar Auth JWT","Epic","...","High","In Progress","quinotospec,auth"
"Login endpoint","Story","...","High","In Progress","quinotospec,auth"
"Crear endpoint POST /login","Task","...","Medium","Done","quinotospec,auth"
```

**Markdown Consolidado:**
Genera un unico archivo Markdown con toda la informacion formateada para lectura humana.

### Paso 4 - Escribir Archivo de Salida
1. Crea `.quinoto-spec/exports/` si no existe
2. Escribe archivo con nombre: `export-{proposal|all}-{YYYYMMDD}.{ext}`
3. Reporta ruta y tamano del archivo generado

### Paso 5 - Resumen de Exportacion
```
Export completado:
  Formato: JSON
  Archivos: 1 propuesta, 4 stories, 12 tareas
  Salida: .quinoto-spec/exports/export-all-20260415.json
  Tamano: 15KB
```

## Output Esperado

- Archivo de exportacion en `.quinoto-spec/exports/`
- Resumen con conteo de elementos exportados
- Entrada en changelog

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--proposal` | Slug de propuesta especifica | No | todas |
| `--format` | Formato (json, csv, markdown, jira-csv) | No | json |
| `--output` | Ruta de salida | No | .quinoto-spec/exports/ |
| `--include` | Que exportar (all, proposals, tasks, stories) | No | all |
| `--compress` | Comprimir output con gzip | No | false |

## Ejemplos

### Exportar Todo a JSON
```
@quinotospec.export
```

### Exportar una Propuesta a CSV
```
@quinotospec.export --proposal auth-jwt --format csv
```

### Exportar para Import en Jira
```
@quinotospec.export --format jira-csv --output ./jira-import.csv
```

### Exportar Solo Tareas
```
@quinotospec.export --include tasks --format csv
```

### Exportar como Markdown Legible
```
@quinotospec.export --format markdown --proposal auth-jwt
```

## Errores Comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| No hay propuestas | .quinoto-spec/proposals/ vacio | Crea propuestas primero con @quinotospec.create-proposal |
| Permission denied | Sin permisos de escritura | Verifica permisos del directorio de salida |
| Formato no soportado | Typo en --format | Usa: json, csv, markdown, jira-csv |

**Instruccion Final OBLIGATORIA (Changelog):**
Una vez completada la exportacion, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Titulo de la Accion**: Export: {format} ({count} items)
- **Resumen**: Se exportaron {N} elementos a formato {format}. Archivo: {ruta}.
