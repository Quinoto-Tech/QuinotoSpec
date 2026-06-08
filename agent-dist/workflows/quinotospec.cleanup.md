---
description: Limpia branches stale, scripts temporales y propuestas inactivas. Modo dry-run por defecto — nunca borra sin confirmación.
---

Objetivo: eliminar artefactos acumulados que ya no son necesarios: branches mergeados, scripts temporales viejos y propuestas sin actividad.

**Regla de seguridad**: este workflow NUNCA borra sin mostrar primero qué eliminará y pedir confirmación explícita. El modo por defecto es `--dry-run`.

## Precondiciones

- `.quinoto-spec/` debe existir.
- Git debe estar disponible para limpieza de branches.

---

### Paso 1 — Detectar branches stale

1. Ejecutar `git branch --merged` y filtrar:
   - Excluir `main`, `master`, `develop`, `staging`, `production`
   - Incluir branches que sigan el patrón `feature/` o `bugfix/`
2. Si no hay branches stale, reportar y continuar.

### Paso 2 — Detectar scripts temporales

1. Buscar en `.quinoto-spec/scripts/` archivos con patrón `temp_*.*` (`.py`, `.sh`, `.js`, `.ts`).
2. Para cada script, verificar fecha de modificación.
3. Filtrar scripts con > 7 días de antigüedad.
4. Si no se usa `--keep-scripts`, marcarlos para limpieza.

### Paso 3 — Detectar propuestas stale

1. Listar carpetas activas en `.quinoto-spec/proposals/` (excluyendo `_archived/`).
2. Para cada propuesta:
   - Verificar `**Estado:**` en `proposal.md`
   - Buscar entradas en `.quinoto-spec/quinoto-spec-changelog.md` relacionadas
3. Marcar como stale si:
   - Sin entradas en changelog por > 30 días
   - Sin tareas completadas (`[x]`)
   - Estado sigue siendo `🟡 Propuesta`

**IMPORTANTE**: las propuestas stale se sugieren para **archivar**, no para borrar.

### Paso 4 — Mostrar resumen (dry-run)

Mostrar al usuario qué se limpiará:

```
Cleanup Plan ──────────────────────────────────────
Branches stale:     {{N}}  → git branch -d ...
Scripts temp (>7d): {{M}}  → rm .quinoto-spec/scripts/temp_*
Propuestas stale:   {{P}}  → Mover a _archived/
──────────────────────────────────────────────────
¿Proceder con la limpieza? (si/no)
```

### Paso 5 — Ejecutar limpieza

Solo si el usuario confirma "si":

1. **Branches**: `git branch -d {{branch}}` para cada uno.
2. **Scripts**: `rm` para cada script temporal.
3. **Propuestas stale**: mover carpeta a `_archived/` y actualizar `**Estado:**` a `🔴 Archivada`.

Si algún branch no se puede borrar (no fully merged), usar `-D` solo con confirmación adicional.

### Paso 6 — Resumen post-limpieza

```
Cleanup Complete ─────────────────────────────────
Branches eliminados:  {{N}}
Scripts eliminados:   {{M}}
Propuestas archivadas: {{P}}
Espacio liberado:     {{SIZE}}
──────────────────────────────────────────────────
```

### Paso 7 — Changelog (OBLIGATORIO)

Ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Cleanup: {{N}} branches, {{M}} scripts, {{P}} propuestas
- **Resumen**: Se eliminaron {{N}} branches stale, {{M}} scripts temporales (>7 días) y se archivaron {{P}} propuestas sin actividad.

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--dry-run` | (Default) Solo mostrar qué se limpiaría, sin ejecutar |
| `--force` | Ejecutar sin pedir confirmación |
| `--keep-scripts` | No tocar scripts temporales |
| `--skip-branches` | No tocar branches de git |
| `--older-than {{N}}` | Solo limpiar artefactos > N días (default: 7 para scripts, 30 para propuestas) |

## Ejemplos

```
@quinotospec.cleanup
@quinotospec.cleanup --force
@quinotospec.cleanup --keep-scripts
@quinotospec.cleanup --older-than 14
```
