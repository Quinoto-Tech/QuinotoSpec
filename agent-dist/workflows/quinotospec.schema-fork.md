---
description: Crea una copia personalizada del schema de artefactos para adaptarlo al flujo del proyecto
---

# Workflow: Schema Fork

Permite crear una version personalizada del schema de artefactos (`schema.yaml`) adaptada al flujo de trabajo especifico del proyecto. Util cuando el schema default no se ajusta al proceso del equipo.

## Modos

| Flag | Descripcion |
|------|-------------|
| `--from <schema>` | Schema base a forkear (default: `quinotospec-default`) |
| `--name <name>` | Nombre para el nuevo schema |
| `--add-artifact <id>` | Agrega un artefacto nuevo (pregunta interactiva) |
| `--remove-artifact <id>` | Elimina un artefacto del schema |
| `--skip-optional` | Omite artefactos marcados como opcionales |
| `--preview` | Muestra el schema resultante sin escribirlo |

---

## Paso 1 — Cargar Schema Base

1. Determinar schema fuente:
   - Si `--from`: buscar `.quinoto-spec/schema.yaml` (si existe) o `agent-dist/templates/schema-template.yaml`
   - Default: `agent-dist/templates/schema-template.yaml`
2. Parsear YAML y mostrar resumen:
   ```
   Schema: quinotospec-default (v1)
   Artefactos: 7
   Fases: 4
   Reglas de validacion: 3
   ```

---

## Paso 2 — Personalizar

### Si se usa `--add-artifact`:

Preguntar interactivamente (una pregunta a la vez):

1. **ID del artefacto:** Identificador unico (ej. `security-review`)
2. **Glob que genera:** Path relativo a `.quinoto-spec/` (ej. `proposals/{slug}/security-review.md`)
3. **Dependencias:** Lista de IDs de artefactos que deben existir antes (separados por coma)
4. **Template:** Path a template (opcional, ej. `security-review-template.md`)
5. **Instruccion:** Mini-prompt que el agente recibe
6. **Opcional:** Si este artefacto es opcional (no bloquea dependientes)
7. **Fase:** A que fase del ciclo pertenece (setup/planning/breakdown/implementation)

### Si se usa `--remove-artifact`:

1. Verificar que el artefacto exista en el schema.
2. Advertir: `⚠️ Eliminar '{id}' puede romper dependencias. Artefactos afectados: {lista}.`
3. Si se confirma, eliminar el artefacto y actualizar `requires` de los artefactos que dependian de el.
4. Si el artefacto eliminado era requerido por `apply.requires`, advertir y pedir alternativa.

### Si se usa `--skip-optional`:

Eliminar del schema todos los artefactos con `optional: true`. Util para equipos que quieren un flujo minimo.

---

## Paso 3 — Validar Schema Resultante

Antes de escribir:

1. Verificar que no haya dependencias circulares.
2. Verificar que todos los `requires` referencien artefactos existentes.
3. Verificar que `apply.requires` referencie artefactos existentes.
4. Verificar que `phases` referencie artefactos existentes.

Si hay errores, mostrarlos y preguntar si corregir o abortar.

---

## Paso 4 — Escribir Schema

1. Si `--preview`, mostrar el YAML completo y detener.
2. Si `.quinoto-spec/schema.yaml` ya existe:
   - Advertir que se sobrescribira.
   - Hacer backup a `.quinoto-spec/schema.yaml.bak`.
3. Escribir `.quinoto-spec/schema.yaml` con:
   - `name:` actualizado
   - `version:` incrementado
   - `description:` actualizado con fecha y motivo del fork
   - Metadata: `forked_from: quinotospec-default`, `forked_date: {{DATE}}`

---

## Paso 5 — Reporte Final

```
✓ Schema forkeado: mi-flujo-personalizado (v1)

  Artefactos: 6 (-1 removido, +0 agregados)
  Fases: 3
  Cambios:
    - Eliminado: security-review
    - Modificado: user-stories ahora requiere [delta-specs, design]

  Schema guardado en: .quinoto-spec/schema.yaml
  Backup: .quinoto-spec/schema.yaml.bak

  Para usar: el artifact engine detecta automaticamente el schema local.
  Para restaurar: rm .quinoto-spec/schema.yaml && mv .quinoto-spec/schema.yaml.bak .quinoto-spec/schema.yaml
```

---

## Paso 6 — Changelog (OBLIGATORIO)

Ejecutar skill `quinotospec-update-changelog`:
- **Titulo de la Accion**: Schema Forked: {{SCHEMA_NAME}}
- **Resumen**: Se creo schema personalizado '{{SCHEMA_NAME}}' desde {{SOURCE}}. {{N}} artefactos, {{CHANGES}}.

---

## Ejemplos

```
# Fork del schema default
@quinotospec.schema-fork --name mi-flujo

# Agregar un artefacto nuevo
@quinotospec.schema-fork --add-artifact security-review

# Eliminar artefactos opcionales
@quinotospec.schema-fork --skip-optional --name flujo-minimo

# Previsualizar sin guardar
@quinotospec.schema-fork --remove-artifact design --preview

# Combinar operaciones
@quinotospec.schema-fork --name enterprise --add-artifact compliance-check --skip-optional
```
