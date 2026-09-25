---
date: 2026-09-24
prefix: QSPE-a7f3
slug: g0-2-verifiable-backup
format: v2
type: change
---

## [2026-09-24] - G0.2: Motor de backup verificable

### Resumen
- Se creó `backup.py` con `create`, `verify`, `list`, `restore` y `cleanup`, store externo a `.quinoto-spec/` y layout `manifest.json` + `payload/`.
- Los archivos se verifican con SHA-256; se excluyen secretos, symlinks, caches, backups y datos generados.
- El restore exige `--yes`, crea un backup de seguridad y usa staging/rename atómico con rollback.
- Se reemplazaron las instrucciones inseguras de `cp/rm` en skill/workflow y se añadieron 7 pruebas sandbox.

**Tiempo Ahorrado**: ~5h (IA: ~35min vs Humano: ~5h)
