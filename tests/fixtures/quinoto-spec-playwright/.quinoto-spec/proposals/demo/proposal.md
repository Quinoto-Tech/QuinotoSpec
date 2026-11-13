# Propuesta Técnica: Playwright Fixture

**ID:** 2026-11-13-playwright-fixture
**Prefijo:** FIXT-1a2b
**Fecha de Creación:** 2026-11-13
**Estado:** 🟡 Propuesta
**Prioridad:** P1
**Complejidad:** Baja
**Servicios Afectados:** ui

---

## Resumen Ejecutivo

Propuesta de fixture para validar el review visual con Playwright.

## Contenido de prueba

| Columna | Valor |
|---|---|
| Render | Markdown |
| Mermaid | Sí |

```mermaid
sequenceDiagram
    actor Reviewer
    participant UI
    participant Playwright
    Reviewer->>UI: GET /proposals/demo
    UI-->>Reviewer: HTML
    Playwright->>UI: Verifica render
```

```python
def demo():
    return "ok"
```
