---
name: quinotospec-ui
description: Dashboard web local read-only sobre .quinoto-spec/ — discovery, propuestas, tareas, changelog y constitución sin modificar archivos. (En desarrollo)
---

# Skill: QuinotoSpec UI

> Companion de observabilidad: lee el estado del proyecto y lo presenta en el navegador. No reemplaza al agente ni ejecuta workflows.

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
