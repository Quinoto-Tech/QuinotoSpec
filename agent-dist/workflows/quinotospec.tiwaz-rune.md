---
description: The Tiwaz Rune — Análisis formal de entropía de un microservicio (Shannon v2 + proxies v1)
---

# Workflow: The Tiwaz Rune

Eres un arquitecto de software especializado en métricas de complejidad y entropía de sistemas.
Tu tarea es analizar un microservicio y generar un reporte de entropía con soluciones concretas.

Este workflow combina dos enfoques:
1. **Métricas proxies de deuda técnica (v1)** — útiles para acción inmediata
2. **Métricas formales de teoría de la información (v2)** — para medición rigurosa

**Parámetros:**

| Parámetro | Requerido | Default | Descripción |
|-----------|-----------|---------|-------------|
| `SERVICE_PATH` | No | `.` | Ruta al microservicio a analizar (directorio actual si no se pasa) |
| `--formal-only` | No | — | Solo métricas formales (FASE 1) |
| `--proxy-only` | No | — | Solo métricas proxy (FASE 2) |
| `--json` | No | — | Output estructurado JSON además del reporte Markdown |
| `--baseline` | No | — | Comparar con el último reporte en `.quinoto-spec/tiwaz-rune/` |

**Invocación:**

```bash
@quinotospec.tiwaz-rune
@quinotospec.tiwaz-rune --service ./services/payments
@quinotospec.tiwaz-rune --service .
@quinotospec.tiwaz-rune --formal-only
@quinotospec.tiwaz-rune --json
```

---

## Validación Pre-Flight

1. Resolver `SERVICE_PATH`: si no fue proporcionado → usar `.` (directorio de trabajo actual).
2. Verificar que `SERVICE_PATH` existe y contiene código fuente o archivos de configuración de build.
3. Si existe `.quinoto-spec/discovery/` en el proyecto raíz:
   - Leer `01-stack-profile.md`, `03-architecture.md`, `06-devops-ci-security.md`, `07-findings-and-recommendations.md` como contexto adicional.
   - Notificar: *"Se integró información del discovery para enriquecer el análisis."*
4. Ejecutar skill `quinotospec-stack-detect` sobre `SERVICE_PATH`.
5. **Reportar el stack detectado antes de continuar** (BLOQUEANTE).

---

## Paso 0 — Detección de Stack

Detecta el stack del proyecto en `SERVICE_PATH`:

1. Archivos de configuración de build (`pom.xml`, `package.json`, `go.mod`, `Cargo.toml`, etc.)
2. Archivos de configuración de la app (`application.yml`, `.env`, `config.*`, etc.)
3. Estructura de directorios (identificar patrón arquitectónico)
4. Lenguaje(s) y framework(s) predominantes
5. Tipo de comunicación (síncrona, asincrónica, ambos)

Presentar resumen del stack detectado. **No continuar hasta reportarlo.**

---

## Paso 1 — Métricas Formales de Teoría de la Información (FASE 1)

> Omitir si `--proxy-only`.

Ejecutar skill `quinotospec-entropy-calculator` → sección `formal-metrics` sobre `SERVICE_PATH`.

### 1.1 Entropía de Shannon del Grafo de Dependencias

Construir grafo G = (V, E):
- V = módulos/capas (domain, infrastructure, application, adapters, etc.)
- E = imports/dependencias entre módulos

```
H(G) = -Σ (grado(n) / 2|E|) * log2(grado(n) / 2|E|)
```

Normalización: `H_norm(G) = H(G) / log2(|V|)` → rango [0, 1]

| H_norm(G) | Interpretación |
|-----------|----------------|
| ≈ 0 | Grafo degenerado (hub único o cadena lineal) |
| → 1 | Distribución uniforme |
| intermedia | Estructura mixta |

### 1.2 Entropía de Complejidad Ciclomática (Shannon)

Por función: `H(f) = log2(n)` donde n = complejidad ciclomática.
Por archivo: `H(file) = Σ H(f_i) / num_funciones`
Por sistema: `H(system) = Σ H(file_j) * (lineas_j / total_lineas)`

| H(system) | Interpretación |
|-----------|----------------|
| < 2 | Sistema simple |
| 2–4 | Complejidad moderada |
| > 4 | Alta complejidad cognitiva |

### 1.3 Entropía de Distribución de Tamaños (Huberman-Hargitai)

```
H_size = -Σ p(i) * log2(p(i))    donde p(i) = s_i / Σ s_j
H_size_norm = H_size / log2(N_archivos)
```

| H_size_norm | Interpretación |
|-------------|----------------|
| → 0 | God File (un archivo domina) |
| → 1 | Todos del mismo tamaño |
| 0.7–0.9 | Distribución saludable |

### 1.4 Entropía de Churn (Cambios Temporales)

Si hay acceso a git log (últimos 6 meses):

```
H_churn = -Σ p(file) * log2(p(file))    donde p(file) = commits_archivo / total_commits
```

- H_churn baja → hotspots
- H_churn alta → cambios distribuidos (posible falta de ownership)
- Archivos con >20% de commits → **hotspot crítico**

### 1.5 Entropía de Configuración (Shannon)

```
H_config = -Σ p(key) * log2(p(key))    donde p(key) = perfiles_donde_cambia / total_perfiles
```

---

## Paso 2 — Métricas Proxies de Deuda Técnica (FASE 2)

> Omitir si `--formal-only`.

Ejecutar skill `quinotospec-entropy-calculator` → sección `proxy-metrics` sobre `SERVICE_PATH`.

| Dimensión | Qué medir |
|-----------|-----------|
| **2.1 Complejidad** | Archivos por capa, archivos >300 líneas, funciones CC>10, código duplicado |
| **2.2 Acoplamiento** | Violaciones de capas, dependencias circulares, fan-in/fan-out |
| **2.3 Configuración** | Props por entorno, secretos expuestos, centralización vs fragmentación |
| **2.4 Dependencias** | Total externas, versiones sin gestión, obsoletas |
| **2.5 Seguridad** | Filtros, manejo de errores, sanitización de inputs |
| **2.6 Testing** | Ratio test/source por capa, capas sin tests, infra en tests |
| **2.7 Observabilidad** | Logging estructurado, métricas/tracing, health checks |

---

## Paso 3 — Score de Entropía Compuesto (FASE 3)

### Score Formal (v2)

```
H_total = 0.30 * H_grafo_norm
        + 0.20 * H_complejidad
        + 0.15 * H_churn_norm
        + 0.15 * H_config_norm
        + 0.10 * H_size_norm
        + 0.10 * H_testing
```

Donde `H_testing = 1 - (test_files / source_files)` (invertido: más tests = menos entropía).

### Score Proxy (v1)

```
S_proxy = 0.20 * S_complejidad
        + 0.25 * S_acoplamiento
        + 0.10 * S_config
        + 0.15 * S_dependencias
        + 0.15 * S_seguridad
        + 0.10 * S_testing
        + 0.05 * S_observabilidad
```

### Score Final (híbrido)

```
S_final = 0.60 * H_total + 0.40 * S_proxy
```

| S_final | Clasificación |
|---------|---------------|
| 0.00–0.20 | Entropía baja (sistema sano) |
| 0.21–0.50 | Entropía media (mejorable) |
| 0.51–0.75 | Entropía alta (riesgoso) |
| 0.76–1.00 | Entropía crítica (acción inmediata) |

Presentar tabla de contribución por dimensión (valor × peso = contribución).

---

## Paso 4 — Reporte de Hallazgos (FASE 4)

Para cada dimensión reportar:
1. Fórmula usada y valor calculado
2. Score para esa dimensión
3. Top 3 problemas (con archivos y líneas)
4. Impacto: **ALTO** / MEDIO / BAJO
5. Comparación con benchmarks (si `--baseline`, comparar con reporte anterior)

---

## Paso 5 — Plan de Remediación (FASE 5)

### Inmediato (esta sprint)
Quick wins con alto impacto, bajo esfuerzo.

### Corto plazo (1–2 sprints)
Refactorizaciones necesarias.

### Mediano plazo (1–2 meses)
Cambios arquitectónicos.

Para cada solución:
- Qué cambiar exactamente
- Archivos afectados
- Riesgo del cambio
- Esfuerzo estimado (horas)
- Impacto esperado en el score

---

## Paso 6 — Métricas de Seguimiento (FASE 6)

Definir 5–7 métricas con fórmulas específicas para monitorear periódicamente:
- Métricas formales (Shannon del grafo, churn, etc.)
- Métricas proxies (ratio tests, archivos grandes, etc.)
- Métricas de negocio (si aplica)

---

## Paso 7 — Persistencia del Reporte

Generar el reporte usando template `tiwaz-rune-report-template.md`.

**Ruta de salida:**

```
.quinoto-spec/tiwaz-rune/YYYYMMDD-hhmm-entropy-report.md
```

Incluir frontmatter YAML:

```yaml
---
date: YYYY-MM-DD
service_path: .
service_name: <nombre derivado del directorio o package.json/go.mod>
s_final: 0.58
classification: "Entropía alta"
h_total: 0.62
s_proxy: 0.51
stack: <resumen del stack detectado>
---
```

Crear el directorio si no existe.

**Formato de salida obligatorio:**
- Tablas Markdown para scores
- Fórmulas matemáticas en bloques de código
- Resaltar en **BOLD** items de riesgo ALTO
- Incluir gráficos ASCII (distribución de tamaños, grafo simplificado)

---

## Paso 8 — Actualizar Discovery

Si existe `.quinoto-spec/discovery/07-findings-and-recommendations.md`, agregar sección al final:

```markdown
## Tiwaz Rune — Entropía (YYYY-MM-DD)
- **Servicio**: {service_name} (`{service_path}`)
- **S_final**: {score} — {classification}
- **Top riesgos**: {top 3}
- **Reporte**: `.quinoto-spec/tiwaz-rune/YYYYMMDD-hhmm-entropy-report.md`
```

---

## Escalamiento de Entropía Crítica

Si `S_final >= 0.51`:
1. Notificar: *"⚠️ Entropía alta/crítica detectada. Revisar reporte en `.quinoto-spec/tiwaz-rune/`."*
2. Si `S_final >= 0.76`, guardar alerta en `.quinoto-spec/tiwaz-rune/critical-alerts.md`:
   ```markdown
   ## 🔴 [Tiwaz Rune] Entropía Crítica — {service_name}
   - **S_final**: {score}
   - **Top riesgos**: {lista}
   - **Ver reporte**: `.quinoto-spec/tiwaz-rune/YYYYMMDD-hhmm-entropy-report.md`
   ```
3. Sugerir workflows de remediación:
   - `@quinotospec.mjolnir-refactor` — si hay módulos con alta deuda
   - `@quinotospec.create-proposal` — si requiere cambio arquitectónico

---

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completado el análisis y guardado el reporte, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Tiwaz Rune Entropy Analysis Executed
- **Resumen**: Se ejecutó análisis de entropía (v2 formal + v1 proxy) sobre `{service_path}`. S_final: {score} ({classification}). Reporte en `.quinoto-spec/tiwaz-rune/`.

**Blood-Bond Monitor:**
Después del changelog, ejecutar skill `quinotospec-blood-bond-monitor --check-only`:
- Si `should_remind: true` (inactivo >=14 días), mostrar recordatorio pasivo con suggestions.
- Si `should_remind: false`, no mostrar nada.
