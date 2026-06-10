---
name: quinotospec-search
description: Busqueda inteligente en todo el directorio .quinoto-spec/ con filtros avanzados por tipo, estado, fecha y prefijo.
---

# Skill: quinotospec-search

Busqueda inteligente y filtrada dentro del directorio `.quinoto-spec/` del proyecto. Permite encontrar propuestas, tareas, user stories y archivos de discovery rapidamente.

## Instrucciones de Ejecucion

### Paso 1 - Identificar Parametros
Recibe los siguientes parametros del usuario:
- `--query`: Texto o patron a buscar (requerido)
- `--type`: Tipo de archivo (`proposal`, `task`, `story`, `discovery`, `all`) (default: `all`)
- `--status`: Filtrar por estado (`en-curso`, `completada`, `archivada`) (opcional)
- `--since`: Filtrar por fecha minima (formato: `YYYY-MM-DD`) (opcional)
- `--prefix`: Filtrar por prefijo de propuesta (ej. `AUTH`, `PAY`) (opcional)
- `--output`: Formato de salida (`text`, `json`) (default: `text`)

### Paso 2 - Ejecutar Busqueda
1. Determina el directorio raiz del proyecto (donde esta `.quinoto-spec/`)
2. Segun `--type`, busca en:
   - `proposal`: `.quinoto-spec/proposals/*/proposal.md`
   - `task`: `.quinoto-spec/proposals/*/*_tasks.md`
   - `story`: `.quinoto-spec/proposals/*/user-stories.md`
   - `discovery`: `.quinoto-spec/discovery/*.md`
   - `all`: Todos los anteriores
3. Aplica filtros adicionales (`--status`, `--since`, `--prefix`)
4. Para cada resultado, extrae:
   - Ruta del archivo
   - Linea donde aparece el match
   - Contexto (2 lineas antes y despues)
   - Estado del elemento (si aplica)

### Paso 3 - Formatear Resultados
- **Modo text**: Muestra resultados en formato legible con colores
- **Modo json**: Muestra array JSON con estructura estandar

## Ejemplos

### Busqueda Basica
```
/quinotospec-search --query "autenticacion"
```

### Busqueda Filtrada por Tipo
```
/quinotospec-search --query "login" --type task
```

### Busqueda por Prefijo y Estado
```
/quinotospec-search --query "endpoint" --prefix AUTH --status en-curso
```

### Busqueda con Output JSON
```
/quinotospec-search --query "security" --output json
```

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--query` | Texto o patron a buscar | Si | N/A |
| `--type` | Tipo de archivo (proposal, task, story, discovery, all) | No | all |
| `--status` | Estado (en-curso, completada, archivada) | No | N/A |
| `--since` | Fecha minima (YYYY-MM-DD) | No | N/A |
| `--prefix` | Prefijo de propuesta (ej. AUTH) | No | N/A |
| `--output` | Formato de salida (text, json) | No | text |

## Notas Importantes

- La busqueda es case-insensitive por defecto
- Soporta expresiones regulares en `--query`
- Si `.quinoto-spec/` no existe, reporta error sugestivo: "Ejecuta @quinotospec.discovery primero"
- Resultados ordenados por relevancia (mas coincidencias primero)
