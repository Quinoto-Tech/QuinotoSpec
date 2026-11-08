---
description: Lanza el dashboard web local read-only de QuinotoSpec (discovery, propuestas, tareas, changelog y constitución) sin modificar archivos.
---

# Workflow: QuinotoSpec UI

Dashboard web local que presenta el estado de `.quinoto-spec/` en el navegador. Es un companion de observabilidad: **no ejecuta workflows ni modifica archivos**.

**Cuándo usar:**

- Revisar el estado global antes de retomar trabajo
- Compartir el estado del proyecto con alguien que no conoce el flujo
- Verificar evidencia y gates pendientes de forma visual

**Cuándo NO usar:**

- Para implementar o aplicar tareas -> usar `@quinotospec.apply`
- Para editar propuestas o tareas -> editar los artefactos vía los workflows propietarios

## Parámetros

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| `--root PATH` | No | Raíz del proyecto con `.quinoto-spec/` (default: `.`) |
| `--roots LIST` | No | Lista de raíces separadas por coma para el panel central multi-proyecto |
| `--host HOST` | No | Host de escucha (default: `127.0.0.1`) |
| `--port N` | No | Puerto (default: `8765`; `0` = efímero) |
| `--no-browser` | No | No abrir el navegador automáticamente |
| `--json` | No | Imprimir el resumen JSON y salir |

## Paso 1 — Verificar el proyecto

1. Comprobar que existe `agent-dist/ui/server.py`.
2. Si no existe `.quinoto-spec/`, advertir que la UI mostrará un proyecto vacío (no es un error).
3. Si el proyecto tiene varios repositorios (Bifrost), lanzar una instancia por `--root` (el panel central multi-proyecto llega en una fase posterior).

## Paso 2 — Lanzar el servidor

```bash
python3 -B agent-dist/ui/server.py --root . --port 8765
```

El comando imprime la URL y abre el navegador salvo `--no-browser`. Se detiene con `Ctrl+C`.

## Paso 3 — Navegar

Páginas: `/` (panel), `/projects` (panel multi-proyecto), `/proposals`, `/proposals/<slug>`, `/tasks`, `/changelog`, `/discovery`, `/constitution`. El resumen completo está en `/api/summary`.

Para varios repositorios (Bifrost) usa `--roots "ruta1,ruta2"` (o varias instancias con `--root`); el selector de proyecto en el header filtra las vistas por `?project=`.

## Paso 4 — Cierre

1. Detener el servidor (Ctrl+C).
2. No registrar cambios en el changelog: la UI es read-only y no produce modificaciones.

## Reglas

- La UI nunca escribe en `.quinoto-spec/`; si necesitas modificar estado, usa el workflow propietario.
- No agregar dependencias externas (pip/npm/CDN): el paquete es stdlib-only.
- Si agregas una página, extiende `readers.py` (datos) y `templates.py` (HTML), no lógica de negocio.
- Ejecutar `tests/test-ui.sh` antes de cerrar cambios en la UI.
