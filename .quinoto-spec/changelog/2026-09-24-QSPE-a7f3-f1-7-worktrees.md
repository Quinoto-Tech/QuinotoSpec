---
date: 2026-09-24
prefix: QSPE-a7f3
slug: f1-7-worktrees
format: v2
type: change
---

## [2026-09-24] - F1.7: Aislamiento con Git Worktrees

### Resumen
- Se creó `quinotospec-worktree` con detección de aislamiento existente, preferencia por herramientas nativas y fallback seguro a `git worktree`.
- Se documentaron prioridad de rutas, `git check-ignore`, validación de permisos, sandbox privado, detección de stack, instalación con confirmación y baseline limpia antes de TDD.
- Apply ahora acepta `USE_WORKTREE`, reutiliza el contexto aislado y evita implementar en el checkout original; no hay push, merge, limpieza ni eliminación automática.
- Se sincronizaron manifest, installer, CI, documentación, changelog y pruebas; la capacidad es prompt-only y la versión permanece 2.7.0 beta-RC.

**Tiempo Ahorrado**: ~2h (IA: ~25min vs Humano: ~2h)
