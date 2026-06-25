---
description: Muestra el changelog consolidado del proyecto, combinando entradas del formato v2 (changelog/) y v1 (quinoto-spec-changelog.md). Ofrece filtros por fecha, prefijo y tipo.
---

Workflow para visualizar el historial de cambios del proyecto de forma consolidada. Detecta automáticamente si el proyecto usa formato v1 (archivo único) o v2 (directorio `changelog/`) o ambos.

## Precondiciones

- El directorio de trabajo será la raíz del proyecto.
- Si no existe ni `.quinoto-spec/changelog/` ni `.quinoto-spec/quinoto-spec-changelog.md`, mostrar mensaje: "No hay changelog disponible. Ejecutá una acción que genere cambios primero."

---

### Paso 1 — Detectar formato(s) activos

1. Verificar existencia de `.quinoto-spec/changelog/`.
2. Verificar existencia de `.quinoto-spec/quinoto-spec-changelog.md`.
3. Determinar modo:
   - Si existe `changelog/` → **v2 activo**
   - Si existe `quinoto-spec-changelog.md` y NO `changelog/` → **v1 activo**
   - Si ambos existen → **modo híbrido** (mostrar ambos, detectar duplicados)

---

### Paso 2 — Recolectar entradas

#### Si v2 activo (o híbrido):
1. Listar archivos en `.quinoto-spec/changelog/` que coincidan con `*.md`, excluyendo `INDEX.md`.
2. Para cada archivo:
   - Leer contenido completo.
   - Extraer fecha del heading `## [Fecha: YYYY-MM-DD]`.
   - Extraer título del mismo heading.
   - Extraer resumen (líneas debajo de `### Resumen` hasta `**Tiempo Ahorrado**`).
   - Extraer prefijo si está presente en el nombre del archivo (formato `YYYY-MM-DD-PREFIX-rest.md`).
3. Ordenar por fecha descendente (más reciente primero).

#### Si v1 activo (o híbrido):
1. Leer `.quinoto-spec/quinoto-spec-changelog.md`.
2. Parsear entradas por bloques `## [Fecha:`.
3. Extraer misma estructura que v2.

---

### Paso 3 — Detectar duplicados (solo modo híbrido)

1. Comparar entradas v1 y v2 por fecha + título.
2. Si una entrada aparece en ambos formatos, mostrar solo la de v2 (más reciente).
3. Reportar: "X entradas duplicadas encontradas (mostrando versión v2)."

---

### Paso 4 — Mostrar vista consolidada

Mostrar en orden descendente de fecha:

```markdown
# 📋 Changelog Consolidado — {{PROJECT_NAME}}

Formato: v2 (changelog/) | v1 (quinoto-spec-changelog.md)  ← activos
{{TOTAL_ENTRADAS}} entradas totales
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

{{ENTRADA_1}}
╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌╌

{{ENTRADA_2}}
...
```

Cada entrada se muestra con:

```
## [Fecha: YYYY-MM-DD] - Título
- Archivo: changelog/YYYY-MM-DD-PREFIX-slug.md (v2)
- Prefijo: PREFIX (si aplica)

### Resumen
- detalle 1
- detalle 2

**Tiempo Ahorrado**: ~Xh (IA: Ym vs Humano: Zm)
```

---

### Paso 5 — Filtrar (opcional)

Soportar flags de filtro:

| Flag | Descripción |
|------|-------------|
| `--days N` | Mostrar solo entradas de los últimos N días |
| `--prefix PREFIX` | Filtrar por prefijo de propuesta |
| `--search TEXTO` | Buscar en resúmenes y títulos |
| `--since YYYY-MM-DD` | Mostrar desde fecha específica |
| `--until YYYY-MM-DD` | Mostrar hasta fecha específica |
| `--limit N` | Mostrar solo las N entradas más recientes |
| `--json` | Salida en JSON para procesamiento |

Ejemplos:
```
@quinotospec.changelog-view
@quinotospec.changelog-view --days 7
@quinotospec.changelog-view --prefix AUTH
@quinotospec.changelog-view --search "delta-spec" --limit 5
@quinotospec.changelog-view --days 30 --json
```

---

### Paso 6 — Salida JSON (si --json)

```json
{
  "project": "{{PROJECT_NAME}}",
  "total": 42,
  "formats": ["v2", "v1"],
  "entries": [
    {
      "date": "2026-06-12",
      "title": "Acción Reciente",
      "prefijo": "AUTH",
      "archivo": "changelog/2026-06-12-AUTH-a1b2-login.md",
      "formato": "v2",
      "resumen": ["detalle 1", "detalle 2"],
      "tiempo_ahorrado": "~2h (IA: 5m vs Humano: 2h)"
    }
  ]
}
```

---

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--days N` | Últimos N días |
| `--prefix PREFIX` | Filtrar por prefijo |
| `--search TEXTO` | Buscar texto |
| `--since YYYY-MM-DD` | Desde fecha |
| `--until YYYY-MM-DD` | Hasta fecha |
| `--limit N` | Máximo N entradas |
| `--json` | Salida JSON |
| `--v1-only` | Forzar solo formato v1 |
| `--v2-only` | Forzar solo formato v2 |

---

## Manejo de Errores

- Si no hay changelog: mostrar mensaje y sugerir ejecutar acción que genere cambios.
- Si `changelog/` tiene entradas corruptas (sin frontmatter o heading inválido): listarlas como "mal formadas" y continuar.
- Si v1 y v2 están vacíos: mostrar "Changelog vacío."
