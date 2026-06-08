---
description: Detecta archivos huérfanos, inconsistencias entre _archived/ y propuestas activas, y problemas de integridad en la estructura .quinoto-spec/
---

Objetivo: ejecutar un chequeo de salud completo del sistema QuinotoSpec, identificando archivos huérfanos, referencias rotas, propuestas inconsistentes y problemas de frescura.

## Precondiciones

- `.quinoto-spec/` debe existir.
- Git debe estar disponible para chequeo de branches.

---

### Paso 1 — Chequear integridad de discovery

1. Verificar que `.quinoto-spec/discovery/` existe.
2. Listar los archivos esperados y verificar presencia:

| Archivo | Esperado | Chequeo adicional |
|---------|----------|-------------------|
| `01-stack-profile.md` | Sí | Extraer `**Discovery Date:**`, verificar < 30 días |
| `02-overview.md` | Sí | |
| `03-architecture.md` | Sí | |
| `04-endpoints-and-openapi.md` | Sí | |
| `05-data-and-services.md` | Sí | |
| `06-devops-ci-security.md` | Sí | |
| `07-findings-and-recommendations.md` | Sí | |
| `08-product-and-agreements.md` | Sí | Verificar que no esté vacío (solo placeholders) |

3. Reportar: *"Discovery: {{N}}/8 archivos presentes. {{M}} con problemas."*

### Paso 2 — Chequear consistencia de propuestas

1. Listar carpetas en `.quinoto-spec/proposals/` (excluyendo `_archived/`).
2. Para cada propuesta activa:
   - Verificar que existe `proposal.md`
   - Verificar que el prefijo en `proposal.md` está registrado en `prefix-registry.md`
   - Verificar que los archivos `*_tasks.md` referencian historias que existen en `user-stories.md`
3. Listar entradas en `prefix-registry.md` y verificar que cada prefijo tiene una carpeta de propuesta correspondiente.
4. Detectar:
   - Prefijos registrados sin propuesta → huérfano
   - Propuestas sin prefijo registrado → sin trazabilidad
   - `*_tasks.md` sin `user-stories.md` → inconsistente

### Paso 3 — Chequear _archived/

1. Listar carpetas en `.quinoto-spec/proposals/_archived/`.
2. Para cada propuesta archivada:
   - Verificar que `proposal.md` tiene `**Estado:** ✅ Completada` o `🔴 Archivada`
   - Verificar que el prefijo está movido a la sección `## Archivados` en `prefix-registry.md`
3. Detectar:
   - Propuestas en `_archived/` con estado incorrecto
   - Prefijos no movidos a sección Archivados

### Paso 4 — Chequear archivos huérfanos

1. Buscar archivos en `.quinoto-spec/` que no pertenecen a la estructura esperada:

| Directorio | Archivos esperados |
|------------|-------------------|
| `discovery/` | 8 archivos `0X-*.md` |
| `proposals/` | `proposal.md`, `user-stories.md`, `*_tasks.md` |
| `scripts/` | `temp_*.py`, `temp_*.sh`, `temp_*.js` |
| `sprints/` | `base-config.yml`, `sprint-*/` |
| Raíz `.quinoto-spec/` | `prefix-registry.md`, `quinoto-spec-changelog.md` |

2. Reportar cualquier archivo fuera de lo esperado.

### Paso 5 — Chequear frescura

1. Leer `**Discovery Date:**` de `01-stack-profile.md`.
2. Si > 30 días: *"⏰ Discovery desactualizado ({{N}} días). Ejecutar @quinotospec.refresh-discovery."*
3. Leer última entrada de `quinoto-spec-changelog.md`.
4. Si > 14 días sin entradas: *"⚠️ Sin actividad en changelog por {{N}} días."*

### Paso 6 — Chequear branches (requiere git)

1. Ejecutar `git branch --merged` y detectar branches mergeados que no son `main`/`master`/`develop`.
2. Listar branches stale (mergeados pero no borrados).
3. NO borrar — solo listar.

### Paso 7 — Generar reporte de salud

Crear `.quinoto-spec/HEALTH_REPORT.md` con:

```markdown
# Health Report — {{YYYY-MM-DD}}

## Score General: {{SCORE}}/100

| Categoría | Puntaje | Estado |
|-----------|---------|--------|
| Discovery | {{N}}/8 | ✅/⚠️/❌ |
| Propuestas | {{N}}/{{M}} | ✅/⚠️/❌ |
| _archived/ | {{N}}/{{M}} | ✅/⚠️/❌ |
| Huérfanos | {{N}} | ✅/⚠️/❌ |
| Frescura | — | ✅/⚠️/❌ |
| Branches | {{N}} stale | ✅/⚠️/❌ |

## Issues Encontrados

| Categoría | Issue | Recomendación |
|-----------|-------|---------------|
| | | |

## Branches Stale

{{LISTA}}
```

### Paso 8 — Changelog (OBLIGATORIO)

Ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Health Check: {{SCORE}}/100
- **Resumen**: Health check ejecutado. {{N}} issues encontrados. Score: {{SCORE}}/100.

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--quick` | Solo score, sin reporte detallado |
| `--skip-branches` | No chequear branches de git |
| `--json` | Output en formato JSON |

## Ejemplos

```
@quinotospec.health
@quinotospec.health --quick
@quinotospec.health --skip-branches
```
