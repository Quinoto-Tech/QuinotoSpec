---
description: Ejecuta un análisis exhaustivo de amenazas con STRIDE y evaluación de riesgo con DREAD
---

# Workflow: Heimdallr

Actúa como un Ingeniero de Seguridad de Software Senior y Experto en Modelado de Amenazas.
Tu objetivo es realizar un análisis de seguridad exhaustivo utilizando las metodologías STRIDE y DREAD para el sistema descrito por el usuario.

**Parámetros Requeridos:**
- `SYSTEM_CONTEXT`: Descripción completa del sistema a analizar (componentes, actores, flujos, integraciones, almacenamiento y procesamiento de datos).

---

## Validación Pre-Flight

1. Si `{{SYSTEM_CONTEXT}}` está vacío o no fue proporcionado → **DETENER** y solicitar al usuario que proporcione una descripción del sistema antes de continuar.
2. Si existe `.quinoto-spec/discovery/`:
   - Si existe `03-architecture.md`, leerlo para identificar componentes, flujos y actores.
   - Si existe `04-endpoints-and-openapi.md`, leerlo para identificar endpoints, métodos de autenticación y exposición de datos.
   - Si existe `05-data-and-services.md`, leerlo para identificar modelos de datos, servicios externos y almacenamiento.
   - Si existe `06-devops-ci-security.md`, leerlo para identificar prácticas de seguridad existentes, auditorías y vulnerabilidades conocidas.
   - Usar esta información como contexto adicional al `{{SYSTEM_CONTEXT}}`. Notificar al usuario: "Se integró información del discovery para enriquecer el análisis."
3. Si no existe `.quinoto-spec/discovery/` → continuar solo con `{{SYSTEM_CONTEXT}}`.

---

## Paso 1 — Contexto del Sistema

- Toma `{{SYSTEM_CONTEXT}}` como fuente principal, más los datos de discovery si aplica.
- Si faltan detalles críticos, declara supuestos explícitos y razonables sin bloquear el análisis.
- Identifica límites de confianza, activos sensibles y dependencias externas.

---

## Paso 2 — Análisis de Componentes e Interacciones

- Identifica componentes principales del sistema (frontend, backend, bases de datos, servicios externos, colas, almacenamiento, etc.).
- Identifica actores relevantes (usuarios legítimos, administradores, APIs externas, atacantes internos y externos).
- Describe flujos de datos principales (origen, tránsito, destino) y puntos donde los datos se almacenan o procesan.

---

## Paso 3 — Identificación de Amenazas (STRIDE)

- Para cada componente o interacción clave detectada, identifica al menos 1 o 2 amenazas potenciales.
- Limita el análisis a un máximo de 10 componentes críticos. Si hay más, prioriza los de mayor impacto (datos sensibles, exposición externa, autenticación).
- Si el total de amenazas supera 20, prioriza las 20 con mayor Damage potencial para mantener el análisis manejable.
- Clasifica cada amenaza bajo una categoría STRIDE:
  - Spoofing (Suplantación)
  - Tampering (Alteración)
  - Repudiation (Repudio)
  - Information Disclosure (Fuga de información)
  - Denial of Service (Denegación de servicio)
  - Elevation of Privilege (Elevación de privilegios)
- Redacta amenazas concretas y realistas, evitando generalidades.

---

## Paso 4 — Evaluación de Riesgo (DREAD)

- Para cada amenaza, asigna puntuaciones del 1 (Muy bajo) al 10 (Muy alto) en:
  - Damage (Daño)
  - Reproducibility (Reproducibilidad)
  - Exploitability (Explotabilidad)
  - Affected Users (Usuarios Afectados)
  - Discoverability (Descubrimiento)
- Calcula el riesgo total con el promedio matemático exacto:
  - `(Damage + Reproducibility + Exploitability + Affected Users + Discoverability) / 5`
- Clasifica la severidad según el riesgo total:

  | Rango | Severidad |
  |-------|-----------|
  | >= 8.0 | 🔴 Crítico |
  | >= 6.5 | 🟠 Alto |
  | >= 4.0 | 🟡 Medio |
  | < 4.0  | 🟢 Bajo |

- Usa puntuaciones realistas y justificables según el contexto.

---

## Paso 5 — Formato de Salida del Informe

Presenta el resultado con formato profesional y limpio, incluyendo en este orden:

### 1. Resumen Ejecutivo
- Breve párrafo sobre el estado general de seguridad del sistema analizado.
- Número total de amenazas identificadas y desglose por severidad.

### 2. Activos Identificados
- Listado de activos críticos del sistema (datos sensibles, credenciales, endpoints clave, secretos, tokens).

### 3. Límites de Confianza (Trust Boundaries)
- Identifica los puntos donde los datos cruzan entre zonas de confianza (e.g., Internet → WAF → App, Frontend → API, API → DB).

### 4. Tabla de Matriz de Riesgos
- Tabla Markdown ordenada de MAYOR a MENOR riesgo total (DREAD).
- Columnas obligatorias:
  - `ID`
  - `Componente/Flujo`
  - `Categoría STRIDE`
  - `Descripción de la Amenaza`
  - `Puntuación DREAD (Detalle)`
  - `Riesgo Total`
  - `Severidad`

### 5. Detalle de Amenazas Críticas y Mitigación
- Para las amenazas con mayor puntuación (hasta 3). Si hay menos de 3, detallar todas:
  - Descripción detallada de cómo un atacante explotaría la amenaza.
  - Recomendación técnica específica para desarrolladores (mitigación accionable).

### 6. Recomendaciones Generales de Seguridad
- Lista de mejoras transversales aplicables al sistema (no vinculadas a una amenaza específica).
- Controles técnicos, validaciones, hardening, monitoreo y pruebas recomendadas.

---

## Paso 6 — Persistencia del Reporte

Guarda el reporte completo en:
```
.quinoto-spec/threat-analysis/YYYYMMDD-hhmm-threat-model.md
```

Incluye metadatos en frontmatter YAML:
```yaml
---
date: YYYY-MM-DD
system: <nombre/resumen del sistema analizado>
total_threats: N
critical: N
high: N
medium: N
low: N
avg_risk: X.X
---
```

Crea el directorio si no existe.

---

## Reglas de Ejecución

- Comienza el análisis directamente, sin introducciones innecesarias.
- Sé específico con mitigaciones (controles técnicos, validaciones, hardening, monitoreo y pruebas).
- Si hay empates de riesgo, prioriza primero la amenaza con mayor `Damage`.
- Mantén trazabilidad entre cada amenaza STRIDE y su evaluación DREAD.

---

## Escalamiento de Hallazgos Críticos

Si alguna amenaza tiene `Riesgo Total >= 8.0` (clasificada como 🔴 Crítico):
1. Notificar al usuario: "⚠️ Se detectaron amenazas con riesgo crítico (>= 8.0). Revisar el reporte en `.quinoto-spec/threat-analysis/`."
2. Guardar una alerta adicional en `.quinoto-spec/threat-analysis/critical-alerts.md` con el formato:
   ```markdown
   ## 🔴 [Heimdallr] Amenaza Crítica — [componente]
   - **Score DREAD**: X.X
   - **Descripción**: <breve descripción>
   - **Ver reporte completo**: `.quinoto-spec/threat-analysis/YYYYMMDD-hhmm-threat-model.md`
   ```
3. Sugerir al usuario que considere ejecutar `quinotospec-rules-enforce` para evaluar el bloqueo de workflows sobre los componentes comprometidos.

---

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completado el análisis y guardado el reporte, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Heimdallr Threat Model Executed
- **Resumen**: Se ejecutó un análisis de amenazas STRIDE + DREAD sobre el sistema indicado y se generó matriz de riesgos priorizada con mitigaciones críticas. Reporte guardado en `.quinoto-spec/threat-analysis/`.

**Blood-Bond Monitor:**
Después del changelog, ejecutar skill `quinotospec-blood-bond-monitor --check-only`:
- Si `should_remind: true` (inactivo >=14 días), mostrar recordatorio pasivo con suggestions.
- Si `should_remind: false`, no mostrar nada.
