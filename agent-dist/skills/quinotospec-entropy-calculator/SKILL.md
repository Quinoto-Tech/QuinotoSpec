---
name: quinotospec-entropy-calculator
description: Calcula métricas formales de entropía (Shannon v2) y proxies de deuda técnica (v1) para el workflow The Tiwaz Rune.
---

# Skill: Quinotospec Entropy Calculator

Motor de cálculo para `@quinotospec.tiwaz-rune`. Proporciona fórmulas, heurísticas por stack y comandos para obtener valores numéricos reproducibles.

**Input:** `SERVICE_PATH` (default: `.`)

---

## Sección: formal-metrics

### Grafo de dependencias — H(G)

1. Identificar módulos/capas según estructura de directorios y convenciones del stack.
2. Por cada archivo fuente, extraer imports según lenguaje:

| Stack | Comando / Patrón |
|-------|------------------|
| TypeScript/JS | `rg "^import .* from" --glob "*.{ts,tsx,js,jsx}"` |
| Python | `rg "^(from|import) " --glob "*.py"` |
| Go | `rg "^import" --glob "*.go"` |
| Java | `rg "^import " --glob "*.java"` |
| Rust | `rg "^use " --glob "*.rs"` |

3. Agrupar archivos en nodos (capa o paquete de primer nivel).
4. Construir aristas dirigidas entre nodos.
5. Calcular grado(n) = in-degree + out-degree por nodo.
6. Aplicar fórmula Shannon y normalizar.

**Gráfico ASCII del grafo** (obligatorio en output):

```
[domain] ──→ [application] ──→ [infrastructure]
     ↑              │
     └──────────────┘  ⚠️ ciclo detectado
```

### Complejidad ciclomática — H(system)

Heurística por función/método (sin herramienta externa):
- CC ≈ 1 + número de puntos de decisión (`if`, `else if`, `for`, `while`, `case`, `catch`, `&&`, `||`, `?`)
- `H(f) = log2(CC)` (mínimo log2(1) = 0 para funciones sin ramas)
- Ponderar por líneas del archivo para H(system)

Si el stack tiene herramienta de análisis estático, preferirla:
- JS/TS: `npx eslint --rule 'complexity: [error, 10]'` o similar
- Python: `radon cc -a -s`
- Go: `gocyclo`

### Distribución de tamaños — H_size

```bash
# Contar líneas por archivo fuente (excluir node_modules, vendor, dist, .git)
find SERVICE_PATH -type f \( -name "*.ts" -o -name "*.py" -o -name "*.go" -o -name "*.java" -o -name "*.rs" \) \
  -not -path "*/node_modules/*" -not -path "*/vendor/*" -not -path "*/dist/*" \
  -exec wc -l {} + | sort -n
```

Calcular H_size y H_size_norm. Generar histograma ASCII:

```
Líneas │ Frecuencia
  0-50 │ ████████████ (24)
51-100 │ ██████ (12)
101-300│ ████ (8)
  >300 │ ██ (3)  ⚠️
```

### Churn — H_churn

```bash
git -C SERVICE_PATH log --since="6 months ago" --name-only --pretty=format: \
  | sort | uniq -c | sort -rn | head -20
```

- Calcular H_churn sobre todos los archivos con commits.
- Marcar hotspots: archivos con >20% del total de commits.

### Configuración — H_config

1. Listar archivos de config: `application*.yml`, `.env*`, `config/*`, `settings*.py`, etc.
2. Extraer keys de cada perfil/entorno.
3. Contar keys que varían entre perfiles.
4. Calcular H_config.

### H_testing

```
H_testing = 1 - (test_files / source_files)
```

Contar archivos en `*test*`, `*spec*`, `__tests__/`, `tests/` vs archivos fuente.

---

## Sección: proxy-metrics

### 2.1 Complejidad (S_complejidad)

| Señal | Umbral | Score parcial |
|-------|--------|---------------|
| Archivos >300 líneas | por archivo | +0.1 c/u (max 1.0) |
| Funciones CC > 10 | por función | +0.05 c/u (max 1.0) |
| Ratio duplicación | >5% LOC | +0.3 |

### 2.2 Acoplamiento (S_acoplamiento)

| Señal | Score |
|-------|-------|
| Violación de capas (domain → infrastructure invertido) | +0.2 c/u |
| Dependencia circular detectada | +0.4 |
| Fan-out > 10 en un módulo | +0.2 |

Detectar ciclos con DFS sobre el grafo del paso formal.

### 2.3 Configuración (S_config)

| Señal | Score |
|-------|-------|
| Secretos en código fuente (no .env) | +0.5 |
| >3 archivos de config por entorno | +0.2 |
| Keys sin default documentado | +0.1 |

### 2.4 Dependencias (S_dependencias)

Analizar manifest del stack (`package.json`, `go.mod`, `requirements.txt`, etc.):
- Total > 50 dependencias directas → +0.2
- Sin lockfile → +0.3
- Dependencias con versión `*` o sin pin → +0.2

### 2.5 Seguridad (S_seguridad)

Revisar contra `06-devops-ci-security.md` si existe:
- Stack traces al cliente → +0.3
- Inputs sin validación en endpoints públicos → +0.3
- Sin filtros CORS/auth en rutas sensibles → +0.2

### 2.6 Testing (S_testing)

```
S_testing = 1 - min(ratio_test_source, 1.0)
```

Capas sin ningún test → +0.2 adicional por capa.

### 2.7 Observabilidad (S_observabilidad)

| Señal presente | Reduce score |
|----------------|--------------|
| Logging estructurado (JSON/logger con niveles) | -0.2 |
| Métricas/tracing (Prometheus, OpenTelemetry, etc.) | -0.2 |
| Health check endpoint | -0.1 |
| Circuit breaker / retry configurado | -0.1 |

Score base 1.0, restar señales encontradas (mínimo 0).

---

## Normalización de scores proxy

Todos los S_* deben normalizarse a rango [0, 1] antes de calcular S_proxy.

---

## Output estructurado (--json)

Cuando el workflow solicita `--json`, retornar además del reporte Markdown:

```json
{
  "service_path": ".",
  "formal": {
    "h_grafo_norm": 0.72,
    "h_complejidad": 3.1,
    "h_churn_norm": 0.45,
    "h_config_norm": 0.60,
    "h_size_norm": 0.82,
    "h_testing": 0.35,
    "h_total": 0.58
  },
  "proxy": {
    "s_complejidad": 0.45,
    "s_acoplamiento": 0.55,
    "s_config": 0.20,
    "s_dependencias": 0.30,
    "s_seguridad": 0.25,
    "s_testing": 0.60,
    "s_observabilidad": 0.40,
    "s_proxy": 0.42
  },
  "s_final": 0.52,
  "classification": "Entropía alta",
  "hotspots": [
    { "file": "src/services/order.service.ts", "lines": 847, "impact": "ALTO" }
  ]
}
```
