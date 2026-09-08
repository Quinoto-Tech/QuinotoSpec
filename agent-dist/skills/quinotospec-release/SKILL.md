---
name: quinotospec-release
description: Automatiza el proceso de release: version bump, consolidación de changelog, tagging y publicación
---

# Workflow: Release

Objetivo: automatizar el proceso de release de QuinotoSpec o de cualquier proyecto que use la metodología. Sigue el proceso documentado en `CONTRIBUTING.md`.

## Precondiciones

- Debe existir changelog (v1 en `.quinoto-spec/quinoto-spec-changelog.md` o v2 en `.quinoto-spec/changelog/`) con entradas desde el último release.
- `.version` debe existir con la versión actual.
- `CHANGELOG.md` (raíz del paquete QuinotoSpec) debe existir con entradas desde el último release.
- Git debe estar disponible y el working tree limpio.

---

### Paso 1 — Analizar cambios desde el último release

1. Buscar el último tag de git: `git describe --tags --abbrev=0`
2. Leer `CHANGELOG.md` (raíz) y `.version` del paquete QuinotoSpec.
3. Extraer todas las entradas posteriores a la fecha del último tag.
4. Si no hay tags previos, considerar todas las entradas del changelog.
4. Clasificar los cambios encontrados:

| Tipo | Palabras clave en entradas | Bump |
|------|---------------------------|------|
| BREAKING | "breaking", "incompatible", "elimina", "migración" | Major |
| Feature | "nueva skill", "nuevo workflow", "nueva feature", "agrega" | Minor |
| Fix / Docs | "corrige", "fix", "documentación", "mejora" | Patch |

### Paso 2 — Determinar y confirmar version bump

1. Según la clasificación del paso 1, determinar el bump sugerido:
   - Si hay al menos 1 BREAKING → Major
   - Si hay al menos 1 Feature y 0 BREAKING → Minor
   - Si solo hay Fix/Docs → Patch
2. Ejecutar `quinotospec-norns --check` para leer la versión actual (fuente canónica `.version`) y detectar drift preexistente entre `.version`, `manifest.json`, `install.sh`, `README.md`/`README_EN.md`, `docs/ARCHITECTURE.md`, `CHANGELOG.md`, `V3_ROADMAP.md` y `scripts/validate-all.sh`. Si reporta `DRIFT`, mostrarlo al usuario — el Paso 4 lo corrige, pero el usuario debe estar al tanto antes de confirmar.
3. Calcular la nueva versión aplicando el bump sugerido (semver) sobre la versión actual.
4. Mostrar al usuario:
   ```
   Release Plan ──────────────────────────────
   Versión actual:  {{CURRENT}}
   Versión nueva:   {{NEW}} ({{BUMP_TYPE}})
   Cambios:         {{N}} entradas de changelog
   ─────────────────────────────────────────────
   ¿Confirmás el release? (si/no)
   ```
5. Si el usuario responde "no", preguntar qué bump forzar: `--bump major|minor|patch`.

### Paso 3 — Consolidar changelog

1. Agregar al inicio del changelog (debajo del título) un header de release:
   ```markdown
   ## [{{NEW}}] - {{YYYY-MM-DD}}
   ```
2. Agrupar las entradas bajo el header.
3. No modificar entradas individuales — solo agregar el header agrupador.

### Paso 4 — Actualizar versión en archivos (delegado a Norns)

1. Ejecutar `quinotospec-norns --to {{NEW}}` (o con `--dry-run` si el release se corrió con `--dry-run`). Esto reemplaza la actualización manual de archivos: Norns sincroniza atómicamente `.version`, badges `version-`/`skills-`/`rules-`/`workflows-` de `README.md`/`README_EN.md`, el diagrama y headings de `docs/ARCHITECTURE.md`, `V3_ROADMAP.md` (`Version actual:`) y `scripts/validate-all.sh` (`EXPECTED_COUNTS`), y valida que no queden referencias colgantes en `schema-template.yaml`.
2. Si Norns reporta error o drift irresoluble, **DETENER** el release y mostrar el reporte al usuario — no continuar al Paso 5 sobre una base inconsistente.
3. Norns ya ejecuta `bash tests/run-all-tests.sh && bash scripts/validate-all.sh --strict` como parte de su propio flujo de bump — no es necesario repetirlo en este paso.

### Paso 5 — Crear tag y mostrar instrucciones

1. Crear tag de git:
   ```bash
   git tag -a {{NEW}} -m "Release {{NEW}}: {{RESUMEN_PRIMERA_ENTRADA}}"
   ```
2. Mostrar al usuario los comandos sugeridos para completar:
   ```
   Release {{NEW}} creado localmente. Para publicar:
     git push origin main
     git push origin {{NEW}}
   ```
3. Si el proyecto tiene GitHub remoto detectado, sugerir:
```
    Para crear el release en GitHub:
      gh release create {{NEW}} --title "{{NEW}}" --notes-file CHANGELOG.md
```

### Paso 6 — Changelog (OBLIGATORIO)

Ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Release {{NEW}}
- **Resumen**: Release {{NEW}} generado. Tipo: {{BUMP_TYPE}}. {{N}} cambios incluidos.

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--dry-run` | Analizar y sugerir bump sin hacer cambios |
| `--bump major` | Forzar major bump |
| `--bump minor` | Forzar minor bump |
| `--bump patch` | Forzar patch bump |
| `--skip-tag` | No crear tag de git |

## Ejemplos

```
@quinotospec.release
@quinotospec.release --dry-run
@quinotospec.release --bump patch
```
