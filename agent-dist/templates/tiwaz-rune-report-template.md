---
date: {{YYYY-MM-DD}}
service_path: {{SERVICE_PATH}}
service_name: {{SERVICE_NAME}}
s_final: {{S_FINAL}}
classification: "{{CLASSIFICATION}}"
h_total: {{H_TOTAL}}
s_proxy: {{S_PROXY}}
stack: {{STACK_SUMMARY}}
---

# The Tiwaz Rune — Entropy Report

**Servicio:** {{SERVICE_NAME}} (`{{SERVICE_PATH}}`)
**Fecha:** {{YYYY-MM-DD}}
**Stack:** {{STACK_SUMMARY}}

---

## Resumen Ejecutivo

{{EXECUTIVE_SUMMARY}}

**S_final: {{S_FINAL}}** — {{CLASSIFICATION}}

---

## Stack Detectado

| Aspecto | Valor |
|---------|-------|
| Lenguaje(s) | {{LANGUAGES}} |
| Framework(s) | {{FRAMEWORKS}} |
| Patrón arquitectónico | {{ARCHITECTURE_PATTERN}} |
| Comunicación | {{COMMUNICATION_TYPE}} |
| Build / Package | {{BUILD_FILES}} |

---

## Scores Compuestos

### Score Formal (v2) — H_total: {{H_TOTAL}}

```
H_total = 0.30 * H_grafo_norm + 0.20 * H_complejidad + 0.15 * H_churn_norm
        + 0.15 * H_config_norm + 0.10 * H_size_norm + 0.10 * H_testing
```

| Dimensión | Valor | Peso | Contribución |
|-----------|-------|------|--------------|
| H_grafo_norm | {{H_GRAFO}} | 0.30 | {{H_GRAFO_CONTRIB}} |
| H_complejidad | {{H_COMPL}} | 0.20 | {{H_COMPL_CONTRIB}} |
| H_churn_norm | {{H_CHURN}} | 0.15 | {{H_CHURN_CONTRIB}} |
| H_config_norm | {{H_CONFIG}} | 0.15 | {{H_CONFIG_CONTRIB}} |
| H_size_norm | {{H_SIZE}} | 0.10 | {{H_SIZE_CONTRIB}} |
| H_testing | {{H_TESTING}} | 0.10 | {{H_TESTING_CONTRIB}} |
| **H_total** | | | **{{H_TOTAL}}** |

### Score Proxy (v1) — S_proxy: {{S_PROXY}}

```
S_proxy = 0.20*S_compl + 0.25*S_acop + 0.10*S_config + 0.15*S_deps
        + 0.15*S_seg + 0.10*S_test + 0.05*S_obs
```

| Dimensión | Score | Peso | Contribución |
|-----------|-------|------|--------------|
| S_complejidad | {{S_COMPL}} | 0.20 | {{S_COMPL_CONTRIB}} |
| S_acoplamiento | {{S_ACOP}} | 0.25 | {{S_ACOP_CONTRIB}} |
| S_config | {{S_CONFIG}} | 0.10 | {{S_CONFIG_CONTRIB}} |
| S_dependencias | {{S_DEPS}} | 0.15 | {{S_DEPS_CONTRIB}} |
| S_seguridad | {{S_SEG}} | 0.15 | {{S_SEG_CONTRIB}} |
| S_testing | {{S_TEST}} | 0.10 | {{S_TEST_CONTRIB}} |
| S_observabilidad | {{S_OBS}} | 0.05 | {{S_OBS_CONTRIB}} |
| **S_proxy** | | | **{{S_PROXY}}** |

### Score Final

```
S_final = 0.60 * {{H_TOTAL}} + 0.40 * {{S_PROXY}} = {{S_FINAL}}
```

| Rango | Clasificación |
|-------|---------------|
| 0.00–0.20 | Entropía baja |
| 0.21–0.50 | Entropía media |
| 0.51–0.75 | Entropía alta |
| 0.76–1.00 | Entropía crítica |

---

## FASE 1 — Métricas Formales

### 1.1 Entropía del Grafo de Dependencias

```
H(G) = -Σ (grado(n) / 2|E|) * log2(grado(n) / 2|E|)
H_norm(G) = H(G) / log2(|V|) = {{H_GRAFO}}
```

|V| = {{NUM_NODES}} nodos, |E| = {{NUM_EDGES}} aristas

**Grafo simplificado (ASCII):**

```
{{GRAPH_ASCII}}
```

### 1.2 Entropía de Complejidad Ciclomática

```
H(system) = {{H_COMPL_RAW}}
```

### 1.3 Entropía de Distribución de Tamaños

```
H_size_norm = {{H_SIZE}}
```

**Distribución (ASCII):**

```
{{SIZE_HISTOGRAM_ASCII}}
```

### 1.4 Entropía de Churn

```
H_churn_norm = {{H_CHURN}}
```

**Hotspots (>20% commits):**

| Archivo | % Commits | Impacto |
|---------|-----------|---------|
{{CHURN_HOTSPOTS_TABLE}}

### 1.5 Entropía de Configuración

```
H_config_norm = {{H_CONFIG}}
```

---

## FASE 2 — Hallazgos por Dimensión

{{FINDINGS_BY_DIMENSION}}

---

## FASE 3 — Plan de Remediación

### Inmediato (esta sprint)

{{REMEDIATION_IMMEDIATE}}

### Corto plazo (1–2 sprints)

{{REMEDIATION_SHORT}}

### Mediano plazo (1–2 meses)

{{REMEDIATION_MEDIUM}}

---

## FASE 4 — Métricas de Seguimiento

| # | Métrica | Fórmula | Valor actual | Frecuencia | Target |
|---|---------|---------|--------------|------------|--------|
{{TRACKING_METRICS_TABLE}}

---

## Comparación con Baseline

{{BASELINE_COMPARISON}}
