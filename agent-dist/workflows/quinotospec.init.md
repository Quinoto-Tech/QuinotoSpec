---
description: Inicializa la estructura .quinoto-spec/ desde cero sin ejecutar discovery completo. Crea directorios, archivos template y prepara el proyecto para usar QuinotoSpec.
---

Objetivo: crear la estructura base de `.quinoto-spec/` en un proyecto nuevo, dejándolo listo para ejecutar `@quinotospec.discovery` como siguiente paso. No ejecuta discovery ni analiza el código — solo crea el esqueleto de directorios y archivos mínimos.

## Precondiciones

- El directorio de trabajo debe ser la raíz de un proyecto (con `src/`, `package.json`, o similar).
- Si `.quinoto-spec/` ya existe, el workflow se detiene a menos que se use `--force`.

---

### Paso 1 — Verificar estado actual

1. Verificar si `.quinoto-spec/` ya existe.
2. Si existe y NO se usó `--force`:
   - Detener y mostrar: *"`.quinoto-spec/` ya existe. Usá `--force` para reinicializar (se preserva discovery y proposals existentes)."*
3. Si existe y se usó `--force`:
   - Advertir que se sobrescribirán archivos de configuración (no discovery ni proposals).
   - Pedir confirmación.

### Paso 2 — Crear estructura de directorios

Crear la siguiente estructura:

```
.quinoto-spec/
├── discovery/
│   └── README.md
├── proposals/
├── scripts/
└── rfc/
```

El `discovery/README.md` debe contener:

```markdown
# Discovery

Ejecutá `@quinotospec.discovery` para generar los 8 archivos de documentación del proyecto.
```

### Paso 3 — Crear prefix-registry.md

Crear `.quinoto-spec/prefix-registry.md` con la tabla vacía:

```markdown
# Registro de Prefijos

| Prefijo | Propuesta | Fecha de Registro |
|---------|-----------|-------------------|
```

### Paso 4 — Crear quinoto-spec-changelog.md

Crear `.quinoto-spec/quinoto-spec-changelog.md` con el header inicial:

```markdown
# QuinotoSpec Changelog

Registro automático de cambios realizados por agentes QuinotoSpec.
**NO EDITAR MANUALMENTE** — Usar siempre la skill `quinotospec-update-changelog`.

---

## [Fecha: {{TODAY}}] - Estructura QuinotoSpec Inicializada

### Resumen
- Se creó la estructura base de `.quinoto-spec/`
- Se inicializó `prefix-registry.md`
- Próximo paso: ejecutar `@quinotospec.discovery`
```

### Paso 5 — Copiar AGENTS.md (opcional)

Si se usa `--with-agents` y no existe `AGENTS.md` en la raíz del proyecto:
1. Buscar `AGENTS.md` en el paquete QuinotoSpec instalado.
2. Copiarlo a la raíz del proyecto.
3. Si no se encuentra el archivo fuente, advertir y continuar.

### Paso 6 — Resumen y próximos pasos

Mostrar al usuario:

```
✓ Estructura QuinotoSpec inicializada en .quinoto-spec/

Próximos pasos:
  1. @quinotospec.discovery          → Documentar el proyecto
  2. Completar discovery/08-product-and-agreements.md
  3. @quinotospec.sprints.init       → Configurar sprints
  4. @quinotospec.create-proposal    → Primera propuesta
```

### Paso 7 — Changelog (OBLIGATORIO)

Ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: QuinotoSpec Initialized
- **Resumen**: Se creó la estructura `.quinoto-spec/` base con `prefix-registry.md` y `quinoto-spec-changelog.md`.

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--force` | Reinicializar aunque `.quinoto-spec/` ya exista (preserva discovery y proposals) |
| `--with-agents` | Copiar `AGENTS.md` a la raíz del proyecto |

## Ejemplos

```
@quinotospec.init
@quinotospec.init --with-agents
@quinotospec.init --force
```
