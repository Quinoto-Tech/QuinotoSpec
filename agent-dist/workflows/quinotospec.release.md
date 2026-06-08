---
description: Automatiza el proceso de release: version bump, consolidación de changelog, tagging y publicación
---

Objetivo: automatizar el proceso de release de QuinotoSpec o de cualquier proyecto que use la metodología. Sigue el proceso documentado en `CONTRIBUTING.md`.

## Precondiciones

- `.quinoto-spec/quinoto-spec-changelog.md` debe existir con entradas desde el último release.
- Git debe estar disponible y el working tree limpio.
- `README.md` debe tener una línea de título con versión (ej. `# QuinotoSpec: Possessed Edition`).

---

### Paso 1 — Analizar cambios desde el último release

1. Buscar el último tag de git: `git describe --tags --abbrev=0`
2. Leer `.quinoto-spec/quinoto-spec-changelog.md` y extraer todas las entradas posteriores a la fecha del último tag.
3. Si no hay tags previos, considerar todas las entradas del changelog.
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
2. Leer la versión actual (del último tag o de `README.md`).
3. Calcular nueva versión con semver.
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

### Paso 4 — Actualizar versión en archivos

1. `README.md`: actualizar la línea de título si incluye versión (ej. `# QuinotoSpec: Possessed Edition` → sin cambios, pero si tiene `v2.0.0` → `v2.1.0`).
2. `README_EN.md` (si existe): mismo cambio.
3. `CHANGELOG.md` del proyecto (si existe, distinto al de `.quinoto-spec/`): misma consolidación.

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
     gh release create {{NEW}} --title "{{NEW}}" --notes-file .quinoto-spec/quinoto-spec-changelog.md
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
