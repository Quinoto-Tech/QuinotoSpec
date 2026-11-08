# Delta Spec — drift

## ADDED Requirements

### Requirement: Reporte de drift docs↔código
El sistema MUST producir un reporte que compare `specs/`, `discovery/`, `README*.md` y `docs/` contra el código real (rutas, símbolos, comandos) con salida JSON y Markdown, y severidad graduada (OK / WARN / BLOCKING).

#### Scenario: Documento referencia un archivo inexistente
- **GIVEN** un spec que menciona `agent-dist/foo/bar.py`
- **WHEN** se ejecuta `@quinotospec.drift-report`
- **THEN** el reporte marca WARN/BLOCKING con la ruta faltante y el archivo de origen.

### Requirement: Drift visible en la UI
La UI MUST exponer los reportes de drift en `/drift` sin escribir en `.quinoto-spec/`.

## MODIFIED Requirements

### Requirement: Refresh discovery
`refresh-discovery` MUST seguir actualizando discovery; drift-report lo complementa, no lo reemplaza.

## REMOVED Requirements

(Ninguno)
