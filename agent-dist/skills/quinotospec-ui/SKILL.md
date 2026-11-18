---
name: quinotospec-ui
description: Dashboard web local read-only sobre .quinoto-spec/ — discovery, propuestas, tareas, changelog y constitución sin modificar archivos. (En desarrollo)
---

> **Fuente de verdad:** esta skill contiene el prompt canónico; el comando `/quinotospec.ui` delega aquí por archivo.

# Skill: Ui

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
| `--stop` | No | Detener instancias en ejecución del servidor UI y salir |
| `--json` | No | Imprimir el resumen JSON y salir |

## Paso 1 — Verificar el proyecto

1. Comprobar que existe `agent-dist/ui/server.py`.
2. Si no existe `.quinoto-spec/`, advertir que la UI mostrará un proyecto vacío (no es un error).
3. Si el proyecto tiene varios repositorios (Bifrost), usa `--roots "r1,r2"` para el panel central multi-proyecto (o una instancia por `--root`).

## Paso 2 — Lanzar el servidor

```bash
python3 -B agent-dist/ui/server.py --root . --port 8765
```

El comando imprime la URL y abre el navegador salvo `--no-browser`. Se detiene con `Ctrl+C`.

## Paso 3 — Navegar

Páginas: `/` (panel), `/projects` (panel multi-proyecto), `/proposals`, `/proposals/<slug>`, `/tasks`, `/changelog`, `/discovery`, `/constitution`. El resumen completo está en `/api/summary`.

Para varios repositorios (Bifrost) usa `--roots "ruta1,ruta2"` (o varias instancias con `--root`); el selector de proyecto en el header filtra las vistas por `?project=`.

## Paso 4 — Cierre

1. Detener el servidor (Ctrl+C) o `python3 -B agent-dist/ui/server.py --stop`.
2. No registrar cambios en el changelog: la UI es read-only y no produce modificaciones.

## Reglas

- La UI nunca escribe en `.quinoto-spec/`; si necesitas modificar estado, usa el workflow propietario.
- No agregar dependencias externas (pip/npm/CDN): el paquete es stdlib-only.
- Si agregas una página, extiende `readers.py` (datos) y `templates.py` (HTML), no lógica de negocio.
- Ejecutar `tests/test-ui.sh` antes de cerrar cambios en la UI.


## Cuando usar

- Ver de un vistazo el estado de discovery, propuestas, stories, tareas y changelog
- Revisar evidencia y gates pendientes sin abrir archivos Markdown
- Onboarding de alguien nuevo en el proyecto

## Invocacion

```bash
python3 -B agent-dist/ui/server.py --root . --port 8765
python3 -B agent-dist/ui/server.py --root . --port 0 --no-browser   # puerto efimero (tests)
python3 -B agent-dist/ui/server.py --root . --json                   # resumen JSON y salir
```

Abre `http://127.0.0.1:8765` (o el puerto indicado).

## Paginas

| Ruta | Contenido |
|------|-----------|
| `/` | Panel: alertas, contadores y tabla de propuestas |
| `/proposals` | Listado completo (activas y archivadas) |
| `/proposals/<slug>` | Detalle: user stories, tareas, evidencia y metadatos |
| `/tasks` | Kanban multi-propuesta (pendientes, en curso, bloqueadas, completadas) |
| `/changelog` | Timeline v1/v2 con resumen y tiempo ahorrado |
| `/discovery` | Archivos de discovery y frescura (limite 30 dias) |
| `/constitution` | Estado, principios y documento completo |
| `/api/summary` | Estado completo en JSON (`schema_version` implicito por estructura estable) |
| `/health` | Healthcheck |

## Garantias

- **Read-only**: el servidor nunca escribe en `.quinoto-spec/` ni en el repositorio.
- **Solo stdlib**: `http.server` + `urllib`; sin pip, sin bundler, sin CDN.
- **Offline**: el CSS y el HTML se sirven desde `agent-dist/ui/templates.py`.
- **Python 3.8+**: compatible con el minimo del paquete.

## Manejo de errores

- Proyecto sin `.quinoto-spec/`: muestra un proyecto vacio con aviso, no falla.
- Archivo mal formado: la pagina responde 200 con lo que pudo leer; un error de lectura responde 500 con el mensaje, sin caer el servidor.
- Puerto ocupado: `OSError` al iniciar; usa `--port 0` o cambia el numero.

## Tests

`tests/test-ui.sh` valida readers sobre la fixture y ejercita todos los endpoints con un servidor efimero.

## Extender

- Datos: `agent-dist/ui/readers.py` (funciones puras, JSON-serializables, sin escritura).
- HTML: `agent-dist/ui/templates.py` (sin Jinja ni CDN; CSS en `STYLE`).
- Rutas: `agent-dist/ui/server.py`.
- Si agregas una pagina, agrega su enlace en `NAV` (templates.py) y una comprobacion en `tests/test-ui.sh`.
