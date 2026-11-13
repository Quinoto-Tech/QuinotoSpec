---
date: 2026-11-13
prefix: PWRE-9f2c
slug: fix-symlinks-macos
type: fix
---

## [2026-11-13] - Fix: rutas resueltas en evidencia (macOS /var -> /private/var)

### Resumen
- El job `test (macos-latest)` quedo rojo con la suite nueva de Playwright: en macOS `/var` es symlink a `/private/var`, asi que comparar `str(path)` contra un path resuelto falla aunque sea el mismo archivo
- **Fix real**: `display_path` resuelve `root` antes de calcular la ruta relativa. Sin eso, la evidencia volvia a guardar rutas absolutas del equipo en macOS (el bug de privacidad que se habia corregido en Linux)
- **Fix de tests**: comparaciones de paths en `test_mcp_detection` y `test_install_playwright_app_runs_pinned_commands_without_sudo` pasan por `.resolve()`
- Nuevo test `test_evidence_paths_work_under_symlinked_root`: reproduce el caso con un root symlinkeado, que corre igual en Linux
- La suite ahora imprime la salida de los unit tests cuando fallan (antes `>/dev/null 2>&1` ocultaba el traceback en CI)

**Verificacion**: 29/29 suites local, `lint-shell` 42 scripts clean; el job `ui-playwright` ya corrio verde en CI por primera vez (run 43472058359)

**Tiempo Ahorrado**: ~1h (IA: ~15min con el traceback visible vs Humano: ~1h de ida y vuelta a ciegas con un runner macOS)
