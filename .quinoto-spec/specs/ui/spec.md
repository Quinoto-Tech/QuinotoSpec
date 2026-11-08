# UI Spec — QuinotoSpec

## ADDED Requirements

### Requirement: Dashboard read-only por proyecto
La UI MUST exponer `/`, `/proposals`, `/proposals/<slug>`, `/tasks`, `/tasks/<ID>`, `/changelog`, `/discovery`, `/discovery/<file>`, `/constitution`, `/specs`, `/evidence`, `/gates`, `/projects`, `/api/summary`, `/health` sin escribir en disco.

### Requirement: Multi-proyecto Bifrost
`--roots "r1,r2"` MUST agregar propuestas/tareas/changelog y permitir filtro `?project=` con selector en header.

### Requirement: Markdown y Mermaid
Bloques ```mermaid MUST renderizarse con `mermaid.min.js` lazy; otros bloques como `<pre>`. Contenido discovery MUST renderizarse como Markdown server-side.

### Requirement: Búsqueda y tema
`/proposals` y `/tasks` MUST aceptar `?q=` con formulario GET; tema claro/oscuro persistido en `localStorage`.

## MODIFIED Requirements

### Requirement: UI en desarrollo
UI se marca *(en desarrollo)* en README/workflow/skill hasta promover a `beta` en `manifest.json`.

## REMOVED Requirements

(Ninguno)
