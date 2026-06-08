---
name: quinotospec-estimate
description: Estima la complejidad y esfuerzo de una propuesta analizando servicios afectados, archivos, tipo de cambio y riesgos. Soporta comparación contra resultados reales.
---

# Skill: Estimate

Calcula una estimación de complejidad para una propuesta QuinotoSpec basada en métricas objetivas extraídas del `proposal.md`. Útil para planificación de sprints y priorización.

## Instrucciones de Ejecución

### Paso 1 - Recibir input

Recibir uno de:
- `--proposal-slug {{SLUG}}`: lee el `proposal.md` existente y estima
- `--from-description "{{TEXTO}}"`: estima desde una descripción libre (modo rápido, menos preciso)
- `--compare --proposal-slug {{SLUG}}`: compara estimación vs resultado real (requiere changelog)

### Paso 2 - Extraer factores del proposal.md

Del archivo `proposal.md`, extraer:

| Factor | Sección | Peso |
|--------|---------|------|
| Servicios afectados | Metadatos → `**Servicios Afectados**` | +1 por servicio |
| Archivos modificados | `**Impacto en el Sistema**` → archivos existentes listados | +0.5 por archivo |
| Archivos nuevos | `**Impacto en el Sistema**` → archivos por crear | +1 por archivo |
| Dependencias nuevas | `**Impacto en el Sistema**` → tooling/libs mencionados | +0.5 por dependencia |
| Fases del plan | `**Plan de Implementación**` → filas en tabla | +0.5 por fase |
| Riesgos altos | `**Riesgos y Mitigaciones**` → riesgos con impacto Alto | +1 por riesgo alto |
| Tipo de cambio | Inferir del `**Resumen Ejecutivo**` y `**Problema Actual**` | Ver tabla abajo |

### Paso 3 - Peso por tipo de cambio

| Tipo | Peso extra | Razón |
|------|-----------|-------|
| Nueva feature | +0 | Baseline |
| Mejora/enhancement | +0.5 | Requiere entender código existente |
| Bugfix | +1 | Requiere debugging + tests de regresión |
| Refactor | +2 | Alto riesgo de regresión, sin cambios visibles |
| Migración | +3 | Riesgo máximo, compatibilidad hacia atrás |
| Breaking change | +2 | Impacto en consumidores |

### Paso 4 - Calcular score y complejidad

```
SCORE = suma de todos los factores (servicios + archivos + dependencias + fases + riesgos + tipo)

Escala:
  SCORE 1-5   → Complejidad: Baja    → ~1-3 días
  SCORE 6-12  → Complejidad: Media   → ~3-8 días
  SCORE 13+   → Complejidad: Alta    → ~8-20 días
```

Si el proposal.md ya declara una `**Complejidad**`, comparar con la estimación calculada. Si hay discrepancia > 1 nivel, advertir:
```
⚠️ Complejidad declarada: {{DECLARADA}} | Estimada: {{CALCULADA}}
La estimación difiere significativamente. ¿Revisar?
```

### Paso 5 - Modo comparación (--compare)

Si se usa `--compare`:
1. Leer `proposal.md` para obtener la estimación original
2. Leer `.quinoto-spec/quinoto-spec-changelog.md` para encontrar entradas relacionadas
3. Extraer `**Tiempo Ahorrado**` de las entradas del changelog
4. Comparar tiempo estimado vs tiempo real
5. Calcular precisión: `(real / estimado) * 100`
6. Reportar:

```
Comparación — {{PROPOSAL_SLUG}}
────────────────────────────────
Complejidad estimada:  {{ESTIMADA}} (~{{N}} días)
Complejidad real:       Tiempo IA: {{T_IA}} / Tiempo Humano: {{T_HUMANO}}
Precisión:              {{PRECISION}}%
────────────────────────────────
```

### Output

```json
{
  "proposal_slug": "auth-jwt",
  "estimated_complexity": "Media",
  "score": 9.5,
  "estimated_days": "3-8",
  "breakdown": {
    "servicios_afectados": 2,
    "archivos_modificados": 4,
    "archivos_nuevos": 2,
    "dependencias_nuevas": 1,
    "fases": 3,
    "riesgos_altos": 1,
    "tipo_cambio": "Nueva feature"
  }
}
```

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--proposal-slug {{SLUG}}` | Estimar desde proposal.md existente |
| `--from-description "..."` | Estimación rápida desde texto libre |
| `--compare` | Comparar estimación vs tiempo real del changelog |
| `--json` | Output en formato JSON |
| `--brief` | Solo complejidad y score, sin desglose |

## Ejemplos

```
@quinotospec-estimate --proposal-slug auth-jwt
@quinotospec-estimate --proposal-slug auth-jwt --json
@quinotospec-estimate --from-description "Agregar login con JWT al auth-service, modificar gateway y crear tabla de sesiones"
@quinotospec-estimate --compare --proposal-slug pay-v2
```

## Integración

Esta skill es llamada automáticamente por:
- `@quinotospec.sprint.plan`: para estimar capacidad del sprint
- `@quinotospec.create-proposal`: puede usarse para validar la complejidad declarada

## Notas

- La estimación es orientativa. Factores humanos (experiencia del dev, interrupciones) no se modelan.
- En modo `--from-description`, la precisión es menor (no hay archivos ni fases concretas).
- El modo `--compare` requiere que el changelog tenga entradas con `**Tiempo Ahorrado**`.
