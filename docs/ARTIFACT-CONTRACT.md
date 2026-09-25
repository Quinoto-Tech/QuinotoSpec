# Contrato de Artefactos QuinotoSpec

## Objetivo

Markdown continúa siendo el formato de almacenamiento y lectura humana, pero proposals, user stories, tasks y entradas de changelog tienen un modelo lógico común. El contrato permite que producers, validators y consumers compartan la misma interpretación sin reescribir inmediatamente los artefactos legacy.

## Identidad

El prefijo de una propuesta tiene esta forma:

```text
MNEMONIC-SUFFIX
```

`MNEMONIC` contiene cuatro letras y `SUFFIX` cuatro caracteres alfanuméricos. Los IDs nuevos conservan ambos componentes:

```text
US-AUTH-a1b2-001
TSK-AUTH-a1b2-001
```

El parser acepta IDs legacy como `US-001`, `US-AUTH-001` y `TSK-USR-001`, pero los normaliza en memoria y conserva el ID original en la salida.

## Proposal

Los nuevos `proposal.md` deben contener metadata explícita:

```markdown
# Propuesta Técnica: {{TITLE}}

**ID**: {{DATE_PREFIX}}-{{SLUG}}
**Prefijo**: {{PREFIX}}
**Fecha de Creación**: YYYY-MM-DD
**Estado**: 🟡 Propuesta
**Prioridad**: P1
**Complejidad**: Media
**Servicios Afectados**: auth-service
```

El ID puede derivarse de la carpeta para propuestas legacy. `Prefix`, fecha y estado siguen siendo obligatorios para validar una propuesta activa.

## User stories

El formato canónico conserva la tabla de seis columnas:

```markdown
| ID | User Story | Criterios de Aceptación | Prioridad | Estimación | Servicio |
|---|---|---|---|---|---|
| US-AUTH-a1b2-001 | Como usuario, quiero ... | - [ ] Criterio | P1 | M | auth-service |
```

El estado de una story se deriva de sus tareas: `completed` si todas están completadas, `in_progress` si tiene tareas completadas y pendientes, y `pending` si todas siguen pendientes.

## Tasks

El formato canónico agrega estado explícito a la tabla actual:

```markdown
| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-AUTH-a1b2-001 | Backend | ... | ... | US-AUTH-a1b2-001 | auth-service | src/... | M | P1 | — | [ ] |
```

Los checkboxes son la representación visible de `pending` y `completed`. El parser también acepta etiquetas de estado, bloques de tareas y tablas legacy. `all_tasks.md` es un índice derivado y no cuenta como fuente primaria.

## Estados

| Estado canónico | Valores aceptados |
|---|---|
| `proposed` | Propuesta, Planificada, Draft, 🟡 Propuesta |
| `in_progress` | En Curso, En Progreso, In Progress, 🟢 En Curso |
| `pending` | Pendiente, `[ ]`, Pending, Open |
| `completed` | Completada, Done, `[x]`, ✅ Completada |
| `blocked` | Bloqueada, Blocked |
| `cancelled` | Cancelada, Descartada |
| `archived` | Archivada, 🔴 Archivada |

## Changelog

El formato v2 es el default y vive en:

```text
.quinoto-spec/changelog/YYYY-MM-DD-PREFIX-SLUG.md
```

El formato v1 `.quinoto-spec/quinoto-spec-changelog.md` se acepta como adaptador legacy. El parser reconoce `Resumen` y `Summary`, `Tiempo Ahorrado` y `Time Saved`, y prioriza entradas v2 cuando hay duplicados.

El changelog es append-only. Una reversión agrega una entrada nueva; nunca elimina una entrada previa.

## Extensiones y presets

Las extensiones y presets son artefactos opcionales con manifest propio:

- `.quinoto-spec/extensions/<id>/extension.yml`
- `.quinoto-spec/presets/<id>/preset.yml`
- `.quinoto-spec/extensions/.registry`

El registro de ownership de una extensión se valida antes de ejecutar hooks; la resolución de templates sigue el orden overrides → presets → extensions → core.

## Decisiones humanas

Las decisiones humanas que habilitan un gate se almacenan aparte de la evidencia técnica:

```text
.quinoto-spec/approvals/APPROVAL_ID.json
```

El registro requiere `schema_version`, `approval_id`, `decision`, `subject`, `action`, `requested_by`, `decided_by`, `decided_at`, `rationale` y `scope`. `decision` admite `approved`, `rejected` o `deferred`; solo `approved` pasa cuando el registro es fresco y coincide exactamente con el sujeto y la acción. El validador no prueba identidad ni ejecuta comandos.

## Validación

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
```

El comando devuelve errores de contrato con código, severidad, ruta y línea. Los formatos legacy producen warnings de compatibilidad, no errores mientras sus relaciones esenciales sean recuperables.

## Archivos canónicos

- `agent-dist/skills/quinotospec-rules-enforce/approval_validate.py`
- `agent-dist/skills/quinotospec-contract/contract.py`
- `agent-dist/skills/quinotospec-contract/SKILL.md`
- `agent-dist/templates/proposal-template.md`
- `agent-dist/templates/user-stories-template.md`
- `agent-dist/templates/tasks-template.md`
- `tests/test-contract.py`
