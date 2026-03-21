---
description: Distribuye las tareas de una propuesta centralizada hacia los sub-proyectos correspondientes según el campo Servicio
---

Este workflow toma una propuesta centralizada (normalmente generada desde un `stack-discovery` o `create-proposal`) y distribuye sus tareas hacia los `.quinoto-spec/` de cada sub-proyecto afectado.

**Parámetro Requerido:**
- `PROPOSAL_SLUG`: El slug de la propuesta centralizada a distribuir (ej. `stack-standardization`).

---

## Paso 1 — Leer la propuesta y sus artefactos

1. Lee `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` y extrae:
    - `**Servicios Afectados:**` → lista de sub-proyectos destino.
2. Lee `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md` y agrupa las historias por su columna `Servicio`.
3. Lee todos los archivos `*_tasks.md` de la propuesta y agrupa las tareas por su columna `Servicio`.

---

## Paso 2 — Validar sub-proyectos destino

Para cada servicio en `Servicios Afectados`:
- Verifica que la carpeta del sub-proyecto exista en el root.
- Verifica que tenga `.quinoto-spec/` (si no existe, créala).
- Si un servicio listado no existe como carpeta → notificar al usuario y saltar ese servicio.

---

## Paso 3 — Distribuir artefactos por servicio

Para cada sub-proyecto destino, crear o actualizar los siguientes archivos dentro de `<servicio>/.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/`:

### `user-histories.md` (filtrado por servicio)
Solo las historias donde `Servicio = <nombre-del-servicio>` (o `todos`).

### `<US_ID>_tasks.md` (filtrado por servicio)
Solo las tareas donde `Servicio = <nombre-del-servicio>`.

**Agregar encabezado de trazabilidad** en cada archivo distribuido:
```markdown
> 📎 Este archivo es una distribución de la propuesta centralizada [`{{PROPOSAL_SLUG}}`](.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md).
> Las modificaciones deben hacerse en la propuesta central y redistribuirse con `@quinotospec.distribute`.
```

**Merge inteligente**: Si el archivo de destino ya existe, no sobreescribir — hacer merge de tareas nuevas solamente.

---

## Paso 4 — Reporte de distribución

Al finalizar, generar un resumen:

| Servicio | Historias distribuidas | Tareas distribuidas | Ruta destino |
| --- | --- | --- | --- |
| auth-service | 3 | 8 | `./auth-service/.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/` |
| user-service | 2 | 5 | `./user-service/.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/` |

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la distribución, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Proposal Distributed: {{PROPOSAL_SLUG}}
- **Resumen**: Se distribuyeron los artefactos de '{{PROPOSAL_SLUG}}' hacia [N] servicios: [lista de servicios].
