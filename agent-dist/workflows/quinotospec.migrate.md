---
description: Migrar entre versiones de QuinotoSpec con deteccion de breaking changes y backup automatico
---

# Workflow: Migrate

Migra la estructura `.quinoto-spec/` de una version de QuinotoSpec a otra. Detecta breaking changes, genera backup automatico y valida post-migracion.

## Precondiciones

- El proyecto tiene `.quinoto-spec/` inicializado
- Se conoce la version actual y la version destino
- El instalador de la nueva version esta disponible

## Instrucciones

### Paso 1 - Detectar Version Actual
1. Busca `.quinoto-spec/.version` o `.quinoto-spec/manifest.json` para determinar la version actual
2. Si no existe archivo de version, intenta detectar por estructura:
   - Si tiene `agents/` -> v2.0+
   - Si tiene 12 reglas -> v2.0+
   - Si tiene 8 reglas -> v1.0
3. Reporta: "Version detectada: {version_actual}"

### Paso 2 - Validar Compatibilidad
1. Compara version actual con version destino
2. Si es un upgrade (ej. 1.0 -> 2.0):
   - Lista breaking changes entre versiones
   - Verifica que el proyecto cumple precondiciones de la nueva version
3. Si es un downgrade -> **ADVIETE**: "Downgrades no son soportados oficialmente. ¿Continuar? [y/N]"
4. Si no hay breaking changes -> "Migracion compatible, sin cambios criticos"

### Paso 3 - Backup Automatico (BLOQUEANTE - Regla #10)
1. Crea backup en `.quinoto-spec/backups/pre-migrate-{YYYYMMDD-HHmmss}/`
2. El backup incluye:
   - Todo el contenido de `.quinoto-spec/`
   - `AGENTS.md` si existe
3. Verifica integridad del backup (compara tamanos)
4. Reporta: "Backup creado en: {ruta}"

### Paso 4 - Ejecutar Migracion
Segun la version destino, aplica los cambios necesarios:

**Migracion v1.0 -> v2.0:**
- Agregar directorio `agents/` con 9 agentes pre-configurados
- Actualizar `quinotospec-rules.md` con 4 nuevas reglas (#9-#12)
- Renombrar skill `generate-github-branch` -> `quinotospec-generate-branch`
- Agregar nuevas skills: search, stats, diff, sync
- Agregar nuevos workflows: migrate, backup, export, import
- Actualizar `AGENTS.md` con nueva seccion de agentes

**Migracion v2.0 -> v2.1:**
- Actualizar workflows modificados
- Agregar nuevas skills si aplica
- Actualizar reglas si cambiaron

### Paso 5 - Validacion Post-Migracion
1. Ejecuta `quinotospec-validate --full`
2. Ejecuta `./tests/run-all-tests.sh` si existe
3. Verifica que todos los archivos criticos existen
4. Reporta resultado:
   - Si todo pasa: "Migracion exitosa a v{version_destino}"
   - Si algo falla: Lista errores y sugiere correcciones

### Paso 6 - Actualizar Version
1. Crea/actualiza `.quinoto-spec/.version` con la nueva version
2. Actualiza `manifest.json` si existe

## Output Esperado

- Backup en `.quinoto-spec/backups/pre-migrate-{timestamp}/`
- Estructura `.quinoto-spec/` actualizada a la nueva version
- Archivo `.version` actualizado
- Entrada en changelog documentando la migracion

## Errores Comunes

| Error | Causa | Solucion |
|-------|-------|----------|
| Version no detectada | No hay archivo .version | Especifica version manualmente con --from |
| Backup fallo | Permisos insuficientes | Verifica permisos de escritura |
| Validacion post-migracion fallo | Breaking change no resuelto | Revisa reporte de validacion y corrige manualmente |
| Conflictos de merge | Archivos modificados localmente | Resuelve conflictos manualmente o usa --force-overwrite |

## Ejemplos

### Migracion Estandar
```
@quinotospec.migrate --to 2.0.0
```

### Migracion con Version Origen Especifica
```
@quinotospec.migrate --from 1.0.0 --to 2.0.0
```

### Migracion Dry-Run (Solo Verificar)
```
@quinotospec.migrate --to 2.0.0 --dry-run
```

**Instruccion Final OBLIGATORIA (Changelog):**
Una vez completada la migracion, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Titulo de la Accion**: Migration: v{from} -> v{to}
- **Resumen**: Se migro la estructura QuinotoSpec de v{from} a v{to}. Backup en {ruta}. {N} archivos actualizados.
