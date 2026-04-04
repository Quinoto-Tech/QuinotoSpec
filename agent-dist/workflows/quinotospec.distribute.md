---
description: Distribuye las tareas de una propuesta centralizada hacia los sub-proyectos correspondientes según el campo Servicio
---

Este workflow toma una propuesta centralizada (normalmente generada desde un `stack-discovery` o `create-proposal`) y distribuye sus artefactos hacia los `.quinoto-spec/` de cada sub-proyecto afectado.

**Parámetros Requeridos:**
- `PROPOSAL_SLUG`: El slug de la propuesta centralizada a distribuir (ej. `stack-standardization`).
- `SPRINT_ID`: El ID del sprint al que pertenecen las tareas (ej. `1`).

---

## Paso 1 — Leer el plan de sprint y la propuesta

1. Lee `.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/sprint-plan.md` para identificar qué tareas de la propuesta `{{PROPOSAL_SLUG}}` han sido asignadas a este sprint y a qué **Componente** (sub-proyecto) pertenecen.
2. Lee `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md` y extrae:
    - `**Servicios Afectados:**` → lista de sub-proyectos destino.
3. Lee `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md` y agrupa las historias por la columna que coincida con el **Componente** (o `Servicio`).
4. Lee todos los archivos `*_tasks.md` de la propuesta y agrupa las tareas por su columna **Componente** (o `Servicio`), filtrando solo aquellas que están presentes en el `sprint-plan.md`.

---

## Paso 2 — Validar sub-proyectos destino

Para cada servicio en `Servicios Afectados`:
- Verifica que la carpeta del sub-proyecto exista en el root.
- Verifica que tenga `.quinoto-spec/` (si no existe, créala).
- Si un servicio listado no existe como carpeta → notificar al usuario y saltar ese servicio.

---

## Paso 3 — Distribuir artefactos por servicio

Para cada sub-proyecto destino, crear la siguiente estructura dentro de `<servicio>/.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/proposals/{{PROPOSAL_SLUG}}/`:

### Archivos a distribuir (copia literal)

Estos archivos se distribuyen **sin modificación**, haciendo copy-paste directo del original:

- `proposal.md` → copia literal de `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md`
- `user-histories.md` → copia literal de `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/user-histories.md`
- `all_tasks.md` → copia literal de `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/all_tasks.md` (si existe)
- Cada archivo `*_tasks.md` → copia literal de `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/{{US_ID}}_tasks.md`

**Importante**: NO filtrar contenido. NO modificar nada. Distribuir el archivo completo como existe en la propuesta central.

### Merge inteligente para archivos existentes

Si el archivo de destino ya existe:
1. **NO sobreescribir el archivo existente**
2. **Comparar el contenido existente con el nuevo**
3. Si el nuevo archivo tiene tareas/historias que no están en el destino, agregarlas al final
4. Mantener siempre el contenido original intacto

### Encabezado de trazabilidad

Agregar al INICIO de cada archivo distribuido (antes del contenido original):
```markdown
> 📎 Este archivo es una distribución del Sprint {{SPRINT_ID}} de la propuesta centralizada [`{{PROPOSAL_SLUG}}`](.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/proposal.md).
> Las modificaciones deben hacerse en la propuesta central y redistribuirse con `/quinotospec.distribute`.
> 
---
```

**Nota**: El encabezado se agrega SIN modificar el contenido original del archivo.

---

## Paso 4 — Reporte de distribución

Al finalizar, generar un resumen:

| Componente | Propuesta | Archivos distribuidos | Ruta destino |
| --- | --- | --- | --- |
| auth-service | ✅ | 5 | `./auth-service/.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/proposals/{{PROPOSAL_SLUG}}/` |
| user-service | ✅ | 5 | `./user-service/.quinoto-spec/sprints/sprint-{{SPRINT_ID}}/proposals/{{PROPOSAL_SLUG}}/` |

---

## Paso 5 — Actualizar Changelog

Una vez completada la distribución, DEBES ejecutar la skill `quinotospec-update-changelog`.

- **Título de la Acción**: Proposal Distributed to Sprint {{SPRINT_ID}}: {{PROPOSAL_SLUG}}
- **Resumen**: Se distribuyeron los artefactos de '{{PROPOSAL_SLUG}}' para el Sprint {{SPRINT_ID}} hacia [N] servicios: [lista de servicios].
