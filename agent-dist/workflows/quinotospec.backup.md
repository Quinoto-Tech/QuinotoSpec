---
description: Backup completo o incremental de .quinoto-spec/ con compresion y restauracion
---

# Workflow: Backup

Crea backups del estado actual de `.quinoto-spec/` para proteger contra perdida de datos antes de operaciones criticas (refactors, migraciones, etc.). Soporta backup completo, incremental y restauracion.

## Precondiciones

- El proyecto tiene `.quinoto-spec/` inicializado
- Hay espacio en disco para el backup (minimo 2x el tamano de `.quinoto-spec/`)

## Instrucciones

### Paso 1 - Determinar Tipo de Backup
Recibe el parametro `--type`:
- `full`: Backup completo de todo `.quinoto-spec/` (default)
- `incremental`: Solo archivos modificados desde el ultimo backup
- `proposals`: Solo el directorio `proposals/`
- `discovery`: Solo el directorio `discovery/`

### Paso 2 - Crear Directorio de Backup
1. Crea `.quinoto-spec/backups/` si no existe
2. Genera nombre de backup: `backup-{type}-{YYYYMMDD-HHmmss}/`
3. Crea el directorio de backup

### Paso 3 - Ejecutar Backup
Segun el tipo:

**Full:**
```bash
cp -r .quinoto-spec/ .quinoto-spec/backups/backup-full-{timestamp}/
```

**Incremental:**
1. Lee timestamp del ultimo backup en `.quinoto-spec/backups/.last-backup`
2. Copia solo archivos modificados despues de ese timestamp:
```bash
find .quinoto-spec/ -newer .quinoto-spec/backups/.last-backup -type f -exec cp --parents {} .quinoto-spec/backups/backup-incremental-{timestamp}/ \;
```

**Proposals/Discovery:**
- Copia solo el subdirectorio especificado

### Paso 4 - Generar Manifest
Crea `.quinoto-spec/backups/backup-{type}-{timestamp}/MANIFEST.md` con:
- Fecha y hora del backup
- Tipo de backup
- Version de QuinotoSpec
- Lista de archivos incluidos con sus tamanos
- Checksum (md5) de cada archivo
- Tamano total del backup

### Paso 5 - Actualizar Referencias
1. Actualiza `.quinoto-spec/backups/.last-backup` con timestamp actual
2. Si hay mas de 10 backups, sugiere limpieza:
   ```
   ! Hay 11 backups acumulados. ¿Ejecutar limpieza de backups antiguos? [y/N]
   ```

### Paso 6 - Compresion (Opcional)
Si se usa `--compress`:
```bash
tar -czf .quinoto-spec/backups/backup-{type}-{timestamp}.tar.gz -C .quinoto-spec/backups/ backup-{type}-{timestamp}/
```
Reporta tamano original vs comprimido.

## Restauracion

### Paso 1 - Listar Backups Disponibles
```bash
ls -la .quinoto-spec/backups/
```

### Paso 2 - Seleccionar Backup
El usuario especifica cual backup restaurar:
```
@quinotospec.backup --restore backup-full-20260415-103000
```

### Paso 3 - Confirmar Restauracion
**ADVERTENCIA**: La restauracion sobreescribe el estado actual.
```
! Esto restaurara .quinoto-spec/ al estado de 2026-04-15 10:30:00.
! El estado actual se perdera (pero se crea backup automatico antes).
? ¿Continuar? [y/N]
```

### Paso 4 - Backup de Seguridad
Antes de restaurar, crea backup del estado actual:
```
.quinoto-spec/backups/pre-restore-{timestamp}/
```

### Paso 5 - Ejecutar Restauracion
```bash
rm -rf .quinoto-spec/
cp -r .quinoto-spec/backups/backup-{type}-{timestamp}/ .quinoto-spec/
```

### Paso 6 - Validacion Post-Restauracion
Ejecuta `quinotospec-validate --full` para verificar integridad.

## Output Esperado

- Backup en `.quinoto-spec/backups/backup-{type}-{timestamp}/`
- MANIFEST.md con lista de archivos y checksums
- `.last-backup` actualizado
- Entrada en changelog

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--type` | Tipo de backup (full, incremental, proposals, discovery) | No | full |
| `--compress` | Comprimir backup con tar.gz | No | false |
| `--restore` | Restaurar desde backup especifico | No | N/A |
| `--list` | Listar backups disponibles | No | false |
| `--cleanup` | Eliminar backups antiguos (mantener ultimos 5) | No | false |

## Ejemplos

### Backup Completo
```
@quinotospec.backup
```

### Backup Incremental Comprimido
```
@quinotospec.backup --type incremental --compress
```

### Listar Backups
```
@quinotospec.backup --list
```

### Restaurar desde Backup
```
@quinotospec.backup --restore backup-full-20260415-103000
```

### Limpiar Backups Antiguos
```
@quinotospec.backup --cleanup
```

## Errores Comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| Espacio insuficiente | Disco lleno | Libera espacio o usa --type incremental |
| Backup corrupto | Archivo danado | Usa otro backup o --restore con --force |
| No hay backups | Primer backup | Ejecuta sin --restore primero |

**Instruccion Final OBLIGATORIA (Changelog):**
Una vez completado el backup, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Titulo de la Accion**: Backup: {type} ({size})
- **Resumen**: Backup {type} creado en {ruta}. {N} archivos, {size} total.
