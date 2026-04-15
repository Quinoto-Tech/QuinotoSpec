---
description: Inicializa la estructura de configuración de sprints del proyecto
---

Este workflow configura la estructura base de sprints para el proyecto.

---

## Paso 1 — Crear estructura de carpetas

1. Verifica si existe `.quinoto-spec/sprints/`.
2. Si no existe, créala.

---

## Paso 2 — Crear configuración base

Verifica si existe `.quinoto-spec/sprints/base-config.yml`:

### A. Si el archivo NO existe:
- Créalo con el esquema de referencia (valores en `null` o vacíos).
- **DETÉN LA EJECUCIÓN INMEDIATAMENTE**.
- **Notifica al usuario**: "Se ha creado el archivo de configuración base `.quinoto-spec/sprints/base-config.yml`. Por favor, complétalo con la definición del equipo y sus capacidades antes de intentar ejecutar este workflow de nuevo."

### B. Si el archivo existe:
Verifica que tenga datos válidos (`equipo` no vacío y `velocidad_promedio_puntos` no sea `null`).

- **SI TIENE VALORES EN `null` O VACÍOS**:
  - **DETÉN LA EJECUCIÓN INMEDIATAMENTE**.
  - **Notifica al usuario**: "El archivo `.quinoto-spec/sprints/base-config.yml` contiene valores incompletos. Por favor, asegúrate de definir al menos un integrante del equipo y la velocidad promedio antes de continuar."

- **SI TIENE DATOS VÁLIDOS**:
  - Notifica al usuario: "Configuración base de sprints verificada. Archivo: `.quinoto-spec/sprints/base-config.yml`"

---

## Esquema de `base-config.yml`

```yaml
# Capacidad del equipo (Base)
equipo:
  - nombre: ""
    rol: ""          # Backend | Frontend | FullStack | DevOps | QA
    disponibilidad: 1.0
    componentes_permitidos: []  # ej: ["api", "ui"]
    componente_owner: ""        # Prioridad de asignación

# Conversión de tallas a puntos
puntos_por_talla:
  XS: 1
  S: 2
  M: 3
  L: 5
  XL: 8

velocidad_promedio_puntos: null
```

**Próximo paso:** Usar `@quinotospec.sprint.create` para crear sprints individuales.
