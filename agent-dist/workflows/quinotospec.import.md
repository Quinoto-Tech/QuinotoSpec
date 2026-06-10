---
description: Importar tareas y user stories desde fuentes externas (GitHub Issues, Jira CSV, CSV, JSON)
---

# Workflow: Import

Importa tareas, user stories y propuestas desde fuentes externas hacia `.quinoto-spec/`. Soporta import desde CSV, JSON, GitHub Issues (via `gh` CLI), y Jira CSV (export manual).

## Precondiciones

- El proyecto tiene `.quinoto-spec/` inicializado
- Existe al menos una propuesta activa (o se crea durante la import)
- El archivo/source de import es accesible

## Instrucciones

### Paso 1 - Identificar Fuente de Import
Recibe parametros:
- `--source`: Fuente de import (`csv`, `json`, `github-issues`, `jira-csv`)
- `--file`: Ruta al archivo (para csv, json, jira-csv)
- `--repo`: Repositorio GitHub (para github-issues, formato: `owner/repo`)
- `--proposal`: Slug de propuesta destino (si no existe, se crea)
- `--prefix`: Prefijo a usar para IDs generados (default: deriva del proposal)
- `--dry-run`: Simular import sin hacer cambios

### Paso 2 - Parsear Fuente

**CSV/JSON:**
1. Lee el archivo
2. Detecta columnas/campos automaticamente:
   - `title` / `summary` / `name` -> Titulo
   - `description` / `body` -> Descripcion
   - `type` / `issue_type` -> Tipo (epic, story, task)
   - `priority` -> Prioridad
   - `status` -> Estado
   - `labels` / `tags` -> Etiquetas
3. Mapea columnas a campos QuinotoSpec
4. Si no puede detectar, pide al usuario que mapee manualmente

**GitHub Issues:**
1. Usa `gh` CLI para obtener issues del repositorio
2. Filtra por labels si se especifica `--label`
3. Convierte cada issue a tarea o user story segun labels:
   - Label "story" -> User Story
   - Label "epic" -> Propuesta
   - Sin label -> Tarea
4. Preserva links a issues originales en metadata

**Jira CSV:**
1. Parsea CSV exportado de Jira
2. Mapea campos:
   - `Summary` -> Titulo
   - `Description` -> Descripcion
   - `Issue Type` -> Tipo (Epic -> Propuesta, Story -> US, Task/Sub-task -> Tarea)
   - `Priority` -> Prioridad
   - `Status` -> Estado (mapeo: To Do -> Pendiente, In Progress -> En Curso, Done -> Completada)
3. Extrae `Epic Link` para asociar tareas a proposals

### Paso 3 - Validar Datos Importados
1. Verifica que cada elemento tiene al menos titulo
2. Detecta duplicados (por titulo similar) y reporta
3. Valida que las dependencias referenciadas existen
4. Si hay errores, reporta y pide confirmacion:
   ```
   ! Se encontraron 3 posibles duplicados:
   - "Login endpoint" (import) vs "US-AUTH-001: Login endpoint" (existente)
   ? ¿Importar como nuevos o skip? [import/skip/manual]
   ```

### Paso 4 - Generar IDs QuinotoSpec
Para cada elemento importado:
1. Asigna ID segun convenciones QuinotoSpec:
   - Propuesta: usa slug existente o genera desde titulo
   - User Story: `US-{PREFIX}-{NNN}` (NNN = siguiente numero disponible)
   - Tarea: `TSK-{PREFIX}-{NNN}`
2. Registra prefijo en `prefix-registry.md` si es nuevo

### Paso 5 - Crear/Actualizar Archivos
1. Si la propuesta destino no existe:
   - Crea directorio `.quinoto-spec/proposals/{slug}/`
   - Genera `proposal.md` con datos basicos
2. Agrega user stories a `user-stories.md` (merge inteligente, Regla #4)
3. Genera archivos `*_tasks.md` para cada US
4. No sobreescribe archivos existentes (merge inteligente)

### Paso 6 - Dry Run (si aplica)
Si `--dry-run`:
- No escribe ningun archivo
- Reporta que se importaria:
  ```
  Dry Run - Import Summary:
    Propuestas: 1 nueva
    User Stories: 4 nuevas, 0 existentes
    Tareas: 12 nuevas, 0 existentes
    Duplicados detectados: 3
    Prefijo a registrar: AUTH
  ```

### Paso 7 - Resumen de Import
```
Import completado:
  Fuente: Jira CSV (jira-export.csv)
  Proposal: auth-jwt (AUTH-a1b2)
  Importados: 4 user stories, 12 tareas
  Duplicados skip: 3
  Archivos creados: 5
  Archivos modificados: 2
```

## Output Esperado

- Propuesta actualizada o creada en `.quinoto-spec/proposals/{slug}/`
- User stories agregadas a `user-stories.md`
- Archivos de tareas generados
- Prefijo registrado en `prefix-registry.md`
- Entrada en changelog

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--source` | Fuente (csv, json, github-issues, jira-csv) | Si | N/A |
| `--file` | Ruta al archivo (csv, json, jira-csv) | No* | N/A |
| `--repo` | Repo GitHub (github-issues) | No* | N/A |
| `--proposal` | Proposal destino | No | deriva de source |
| `--prefix` | Prefijo para IDs | No | deriva de proposal |
| `--label` | Filtrar por label (github-issues) | No | N/A |
| `--dry-run` | Simular sin escribir | No | false |
| `--skip-duplicates` | Saltar duplicados automaticamente | No | false |

*Requiere `--file` o `--repo` segun la fuente

## Ejemplos

### Importar desde CSV
```
@quinotospec.import --source csv --file tasks.csv --proposal auth-jwt
```

### Importar Issues de GitHub
```
@quinotospec.import --source github-issues --repo Quinoto-Tech/QuinotoSpec --label enhancement
```

### Importar desde Jira CSV
```
@quinotospec.import --source jira-csv --file jira-export.csv --proposal auth-jwt
```

### Dry Run (Ver que se importaria)
```
@quinotospec.import --source json --file data.json --dry-run
```

## Errores Comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| Archivo no encontrado | Ruta incorrecta | Verifica ruta con `ls` |
| Formato no reconocido | Columnas inesperadas | Usa --dry-run para ver deteccion |
| GitHub API error | Sin autenticacion | Ejecuta `gh auth login` |
| Prefijo en conflicto | Ya existe en registry | Usa --prefix diferente |
| Duplicados | Tareas ya existen | Usa --skip-duplicates o resuelve manualmente |

**Instruccion Final OBLIGATORIA (Changelog):**
Una vez completada la importacion, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Titulo de la Accion**: Import: {source} -> {proposal}
- **Resumen**: Se importaron {N} elementos desde {source}. {X} stories, {Y} tareas creadas. Origen: {archivo/repo}.
