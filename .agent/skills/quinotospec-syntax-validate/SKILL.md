---
name: Quinotospec Syntax Validate
description: Valida la sintaxis y estructura de archivos QuinotoSpec antes de ejecutar workflows.
---

# Skill: Quinotospec Syntax Validate

Valida que los archivos generados por workflows tengan la sintaxis correcta. Útil como pre-check antes de apply o cuando se importan archivos externos.

## Checks de Sintaxis

### 1. Proposal (.quinoto-spec/proposals/{slug}/proposal.md)

Verifica:
- ✅ Tiene campo `**ID:**` con formato correcto
- ✅ Tiene campo `**Prefijo:**` matching prefix-registry
- ✅ Tiene campo `**Estado:**` con valor válido
- ✅ Tiene campo `**Fecha de Creación:**`
- ✅ Tiene sección `## Descripción`
- ✅ Tiene sección `## Solución Propuesta`

**Errores comunes**:
- Estado inválido (no es 🟢, 🔴, ✅)
- Falta prefijo en registry

### 2. User Stories (.quinoto-spec/proposals/{slug}/user-histories.md)

Verifica:
- ✅ Cada US tiene formato `## US-XXX-NN: Título`
- ✅ Tiene columna `**Servicio:**` (para multi-repo)
- ✅ Tiene checkbox list en `**Criterios de Aceptación:**`
- ✅ No hay IDs duplicados

### 3. Tasks (.quinoto-spec/proposals/{slug}/*_tasks.md)

Verifica:
- ✅ Cada tarea tiene formato `## TSK-XXX-NN`
- ✅ Está referenciada a una US válida
- ✅ Tiene checkboxes `[ ]` / `[x]`
- ✅ Servicio coincide con el de la US padre
- ✅ No hay orphan tasks (sin US padre)

### 4. Changelog (.quinoto-spec/quinoto-spec-changelog.md)

Verifica:
- ✅ Formato de fecha ISO (YYYY-MM-DD)
- ✅ Sección por versión con formato `[X.Y.Z]`
- ✅ Tipo de cambio válido (Added, Changed, Deprecated, Removed, Fixed, Security)
- ✅ No hay entradas duplicadas

### 5. Discovery Files (.quinoto-spec/discovery/*.md)

Verifica:
- ✅ Cada archivo tiene `# Título` como H1
- ✅ No está vacío (mínimo 100 caracteres)
- ✅ Si es `07-product-and-agreements.md`, tiene contenido DoR/DoD

### 6. Config Files (base-config.yml, sprint-config.yml)

Verifica:
- ✅ YAML válido (parseable)
- ✅ Campos requeridos presentes
- ✅ Tipos de datos correctos (strings, numbers, arrays)

## Uso

```bash
# Validar una propuesta específica
/syntax-validate --type proposal --slug auth-jwt

# Validar todas las propuestas
/syntax-validate --type all

# Validar solo changelog
/syntax-validate --type changelog

# Validación estricta (falla en warnings)
/syntax-validate --strict
```

## Output

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    { "file": "proposals/auth-jwt/proposal.md", "warning": "Fecha de creación con formato no estándar" }
  ]
}
```

## Integración con Workflows

Esta skill debe ejecutarse como pre-condición en:
- `@quinotospec.apply` - antes de ejecutar código
- `@quinotospec.archive` - antes de archivar
- `@quinotospec.distribute` - antes de distribuir a servicios

## Flags

| Flag | Descripción |
|------|-------------|
| `--type` | `proposal`, `user-stories`, `tasks`, `changelog`, `discovery`, `config`, `all` |
| `--slug` | Slug específico (para proposal/tasks) |
| `--strict` | Tratar warnings como errores |
| `--fix` | Intentar auto-corrección cuando sea posible |
