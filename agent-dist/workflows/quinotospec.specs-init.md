---
description: Inicializa el directorio specs/ desde discovery o propuestas existentes
---

# Workflow: Specs Init

Inicializa el directorio `specs/` con requerimientos extraidos del discovery o de propuestas activas. Util para proyectos que ya usaban QuinotoSpec antes de delta-specs, o para crear la base inicial de specs desde cero.

## Modos

| Modo | Flag | Fuente |
|------|------|--------|
| **Desde Discovery** | `--from-discovery` | `.quinoto-spec/discovery/` (03-architecture, 05-data-and-services, 04-endpoints) |
| **Desde Propuestas** | `--from-proposals` | `.quinoto-spec/proposals/*/proposal.md` activas |
| **Desde Cero** | (default) | `01-stack-profile.md` para estructura de dominios |

---

## Paso 1 — Verificar Estado

1. Verificar si `.quinoto-spec/specs/` ya tiene archivos `.md` (no solo README.md).
2. Si tiene archivos:
   - Mostrar: `specs/ ya contiene {{N}} archivos en {{M}} dominios.`
   - Advertir que la operacion puede sobrescribir contenido existente.
   - Pedir confirmacion. Si el usuario no confirma, detener.
3. Si no tiene archivos (solo README.md o vacio), continuar.

---

## Paso 2 — Identificar Dominios

Segun el modo seleccionado:

### Modo `--from-discovery`
1. Leer `.quinoto-spec/discovery/03-architecture.md`:
   - Extraer nombres de servicios/sub-proyectos mencionados.
   - Buscar patrones: `**Servicio:**`, `**Componente:**`, `- servicio:`, diagramas Mermaid.
2. Leer `.quinoto-spec/discovery/05-data-and-services.md`:
   - Extraer entidades y servicios externos.
   - Agrupar entidades por dominio.
3. Leer `.quinoto-spec/discovery/04-endpoints-and-openapi.md`:
   - Extraer endpoints y agrupar por prefijo/dominio (ej. `/auth/*` → auth, `/api/users/*` → users).
4. Consolidar lista de dominios unicos.

### Modo `--from-proposals`
1. Leer todas las propuestas activas en `.quinoto-spec/proposals/*/proposal.md`.
2. Extraer `**Servicios Afectados:**` de cada propuesta.
3. Consolidar lista de dominios unicos.
4. Para cada dominio, extraer requerimientos de la seccion `Especificacion Tecnica Detallada`:
   - Parsear bloques de codigo, descripciones de endpoints, reglas de negocio.
   - Convertir a formato `### Requirement: {{name}}`.
   - Si hay informacion suficiente, agregar escenarios GIVEN/WHEN/THEN.

### Modo Default (Desde Cero)
1. Leer `.quinoto-spec/discovery/01-stack-profile.md` si existe.
2. Si no existe discovery, pedir al usuario que liste los dominios/servicios del proyecto.
3. Crear estructura de directorios vacia con `specs/<dominio>/spec.md` por cada dominio.

---

## Paso 3 — Generar Specs por Dominio

Para cada dominio identificado:

1. Crear directorio `.quinoto-spec/specs/{{dominio}}/` si no existe.
2. Crear `.quinoto-spec/specs/{{dominio}}/spec.md` con el siguiente formato:

```markdown
# Spec: {{dominio}}

> **Inicializado:** {{DATE}}
> **Fuente:** {{discovery | propuestas | manual}}

---

## Current Requirements

<!--
  Requerimientos actuales del sistema para el dominio {{dominio}}.

  Formato:
  ### Requirement: Name
  The system SHALL/MUST/SHOULD ...

  #### Scenario: Name (optional)
  - GIVEN precondition
  - WHEN action
  - THEN expected outcome

  Este archivo se actualiza automaticamente al archivar propuestas con delta-specs/.
  NO editar manualmente — los cambios se hacen via propuestas.
-->
```

3. Si el modo es `--from-proposals` o `--from-discovery`, poblar `Current Requirements` con los requerimientos extraidos.

---

## Paso 4 — Generar Specs README

Crear o actualizar `.quinoto-spec/specs/README.md`:

```markdown
# Specs — Source of Truth

Este directorio contiene la especificacion canonica del sistema, organizada por dominio/servicio.

## Dominios

{{LISTA_DE_DOMINIOS_Y_DESCRIPCIONES}}

## Formato

Cada `spec.md` contiene requerimientos en formato:

### Requirement: Name
The system SHALL...

#### Scenario: Name (optional)
- GIVEN precondition
- WHEN action
- THEN expected outcome

## Actualizacion

Los specs se actualizan automaticamente al archivar propuestas que contienen `delta-specs/`.
El engine de merge aplica ADDED (append), MODIFIED (replace), REMOVED (delete), RENAMED (rename).

## Vinculo con Discovery

Los specs reflejan el estado actual del sistema.
Para entender el stack, arquitectura y contexto, consulta `.quinoto-spec/discovery/`.
```

---

## Paso 5 — Reporte Final

Mostrar resumen:

```
✓ specs/ inicializado

  Modo: {{MODE}}
  Dominios: {{N}}
  Requerimientos generados: {{TOTAL}}

  Dominios creados:
  {{LISTA_DE_DOMINIOS_CON_CONTEO}}

  Próximos pasos:
    1. @quinotospec.create-proposal → Las propuestas ahora generaran delta-specs/
    2. @quinotospec.archive → Al archivar, los delta-specs se mergean en specs/
```

---

## Paso 6 — Changelog (OBLIGATORIO)

Ejecutar skill `quinotospec-update-changelog`:
- **Titulo de la Accion**: Specs Initialized
- **Resumen**: Se inicializo specs/ con {{N}} dominios y {{TOTAL}} requerimientos desde {{MODE}}.

---

## Flags

| Flag | Descripcion |
|------|-------------|
| `--from-discovery` | Extraer dominios y requerimientos de `.quinoto-spec/discovery/` |
| `--from-proposals` | Extraer requerimientos de propuestas activas |
| `--force` | Sobrescribir specs existentes sin confirmacion |

---

## Ejemplos

```
# Inicializar desde discovery
@quinotospec.specs-init --from-discovery

# Migrar propuestas viejas a specs
@quinotospec.specs-init --from-proposals

# Crear estructura vacia
@quinotospec.specs-init

# Forzar regeneracion
@quinotospec.specs-init --from-discovery --force
```
