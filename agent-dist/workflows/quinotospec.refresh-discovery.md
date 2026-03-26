---
description: Refresca solo los archivos de discovery afectados por cambios recientes en el proyecto, sin regenerar los 8 archivos completos
---

Este workflow detecta qué ha cambiado en el proyecto desde el último discovery y actualiza únicamente los archivos de `.quinoto-spec/discovery/` afectados.

**Parámetro Opcional:**
- `SERVICE_PATH`: Ruta relativa al sub-proyecto a refrescar (ej. `./services/auth-service`). Si no se especifica, opera sobre el directorio raíz del proyecto. Este parámetro es utilizado por `quinotospec.stack-discovery` cuando detecta discoveries desactualizados en servicios individuales.

**Precondición**: El discovery completo (`quinotospec.discovery`) debe haberse ejecutado al menos una vez en el directorio objetivo. Si no existe `{{SERVICE_PATH}}/.quinoto-spec/discovery/` (o `.quinoto-spec/discovery/` en la raíz), redirigir al usuario a ejecutar `quinotospec.discovery` primero.

---

## Paso 1 — Verificar fecha del último discovery

1. Lee `.quinoto-spec/discovery/00-stack-profile.md` y extrae el campo `**Discovery Date:**`.
2. Calcula cuántos días han pasado desde esa fecha.
3. Reporta: *"Último discovery: [fecha] ([N] días atrás)"*.

---

## Paso 2 — Detectar archivos modificados desde el último discovery

Busca archivos modificados desde la `**Discovery Date:**` extraída:

```bash
git diff --name-only HEAD@{<discovery-date>} HEAD
```

Si git no está disponible, listar archivos con fecha de modificación posterior al discovery date.

Clasifica los cambios por área de impacto:

| Archivo modificado | Discovery afectado |
| --- | --- |
| `package.json`, `requirements.txt`, `go.mod`, etc. | `00-stack-profile.md` |
| Archivos de rutas/controllers/views | `03-endpoints-and-openapi.md` |
| Archivos de modelos/migrations/schemas | `04-data-and-services.md` |
| `.github/workflows/`, `Dockerfile`, `.env.example` | `05-devops-ci-security.md` |
| Cualquier archivo con bugs/refactors significativos | `06-findings-and-recommendations.md` |

---

## Paso 3 — Regenerar solo los archivos afectados

Para cada archivo de discovery identificado como impactado:
1. Leer el archivo actual de discovery.
2. Analizar los cambios en el código fuente relacionados.
3. Actualizar **solo las secciones afectadas** del archivo discovery, manteniendo el resto intacto.
4. Actualizar el campo `**Discovery Date:**` al día de hoy en `00-stack-profile.md`.

Si no hay cambios relevantes → reportar: *"No se detectaron cambios que requieran actualizar el discovery."*

---

## Paso 4 — Reporte de refresh

Al finalizar, generar un resumen de:
- Archivos de discovery actualizados: [lista]
- Archivos sin cambios: [lista]
- Áreas de atención detectadas durante el refresh (si aplica)

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completado, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Discovery Refreshed
- **Resumen**: Se actualizaron [N] archivos de discovery: [lista]. Último discovery previo: [fecha anterior].
