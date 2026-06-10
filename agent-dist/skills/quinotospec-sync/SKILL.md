---
name: quinotospec-sync
description: Sincroniza estado entre multiples proyectos QuinotoSpec, detecta conflictos y genera reportes de consistencia.
---

# Skill: quinotospec-sync

Sincroniza y valida consistencia entre multiples proyectos que usan QuinotoSpec. Diseñado para arquitecturas multi-servicio donde las propuestas pueden afectar multiples repositorios.

## Instrucciones de Ejecucion

### Paso 1 - Identificar Proyectos
Recibe los siguientes parametros:
- `--projects`: Lista de rutas de proyectos separadas por comas
- `--scope`: Alcance de sync (`proposals`, `discovery`, `all`) (default: `proposals`)
- `--mode`: Modo de operacion (`check`, `sync`, `report`) (default: `check`)
- `--prefix`: Filtrar por prefijo de propuesta (ej. `AUTH` para sincronizar solo propuestas de auth)

### Paso 2 - Modo Check (Deteccion de Conflictos)
Para cada proyecto indicado:
1. Lee `.quinoto-spec/proposals/` y lista propuestas activas
2. Para cada propuesta activa, extrae:
   - Prefijo y slug
   - Archivos que modifica (seccion "Archivos Afectados")
   - Servicios que afecta (seccion "Servicios Afectados")
3. Cruza informacion entre proyectos:
   - Detecta propuestas con mismo prefijo en diferentes proyectos
   - Detecta archivos que se modifican en multiples proyectos
   - Detecta servicios que son afectados por propuestas en diferentes proyectos
4. Genera reporte de conflictos:
   - Conflictos de alcance (mismo dominio en 2 propuestas)
   - Conflictos de archivos (mismo archivo modificado en 2 propuestas)
   - Dependencias circulares (Proyecto A depende de B, B depende de A)

### Paso 3 - Modo Sync (Sincronizacion)
1. Para cada propuesta que existe en multiples proyectos:
   - Compara versiones (usa timestamp mas reciente como fuente de verdad)
   - Identifica diferencias en user stories y tareas
   - Genera plan de sincronizacion
2. Ejecuta sincronizacion:
   - Actualiza propuestas en proyectos desactualizados
   - Preserva cambios locales si son compatibles
   - Reporta conflictos que requieren resolucion manual

### Paso 4 - Modo Report (Reporte de Consistencia)
Genera un reporte de consistencia global:
- Estado de cada proyecto (discovery actualizado? propuestas activas?)
- Propuestas compartidas entre proyectos
- Dependencias inter-proyecto
- Recomendaciones de sincronizacion

## Ejemplos

### Check de Conflictos
```
/quinotospec-sync --projects ../auth-service,../payment-service,../user-service --mode check
```

### Sincronizar Propuestas de Auth
```
/quinotospec-sync --projects ../auth-service,../api-gateway --prefix AUTH --mode sync
```

### Reporte de Consistencia Global
```
/quinotospec-sync --projects ../service-a,../service-b,../service-c --mode report
```

### Solo Discovery
```
/quinotospec-sync --projects ../frontend,../backend --scope discovery --mode check
```

## Parametros

| Parametro | Descripcion | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--projects` | Rutas de proyectos (separadas por comas) | Si | N/A |
| `--scope` | Alcance (proposals, discovery, all) | No | proposals |
| `--mode` | Modo (check, sync, report) | No | check |
| `--prefix` | Filtrar por prefijo de propuesta | No | N/A |
| `--output` | Formato (text, json) | No | text |

## Formato de Reporte de Conflictos

```
╔══════════════════════════════════════════════════════╗
║   QuinotoSpec Sync - Conflict Report                 ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  Proyectos analizados: 3                             ║
║  ─────────────────────────────────────────           ║
║                                                      ║
║  ❌ CONFLICTOS DETECTADOS: 2                         ║
║                                                      ║
║  1. Conflicto de Alcance                             ║
║     Prefijo: AUTH                                    ║
║     Proyecto A: auth-service (propuesta: auth-jwt)   ║
║     Proyecto B: api-gateway (propuesta: auth-refresh)║
║     Conflicto: Ambos modifican middleware de auth    ║
║                                                      ║
║  2. Conflicto de Archivos                            ║
║     Archivo: src/middleware/auth.ts                   ║
║     Proyecto A: auth-service (TSK-AUTH-003)          ║
║     Proyecto B: api-gateway (TSK-GATE-001)           ║
║                                                      ║
║  ⚠️  DEPENDENCIAS: 1                                 ║
║     payment-service → auth-service (token validation) ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
```

## Notas Importantes

- Todos los proyectos deben tener `.quinoto-spec/` inicializado
- El modo `sync` puede modificar archivos en proyectos destino: confirma antes de ejecutar
- Los conflictos de archivos son los mas criticos: requieren resolucion manual
- El modo `check` es seguro (read-only) y puede ejecutarse frecuentemente
- Para proyectos en diferentes repos, las rutas deben ser accesibles desde el directorio actual
- Ejecuta `quinotospec-update-changelog` en cada proyecto despues de sync
