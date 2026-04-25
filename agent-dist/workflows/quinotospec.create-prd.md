---
description: crear un Product Requirements Document (PRD)
---

Este workflow te guía en la creación de un Product Requirements Document (PRD) estructurado para validar ideas de producto antes de comprometer recursos de desarrollo. El PRD es un documento vivo que evoluciona durante la sesión de trabajo.

**Inputs obligatorios:**
- `PRD_TOPIC`: El tema, problema o oportunidad de producto a documentar.
- `PRD_AUDIENCE`: Audience principal del producto (ej. "desarrolladores B2B", "usuarios finales", "equipos internos").

**Flujo de Trabajo:**

1. **Contextualización**
   - Revisa `.quinoto-spec/discovery/` para entender el contexto del proyecto
   - Especialmente `08-product-and-agreements.md` para visión de producto y acuerdos existentes
   - Si no existe discovery, ejecuta `/quinotospec.discovery` primero

2. **Exploración del Topic**
   - Investiga qué existe actualmente relacionado con `{{PRD_TOPIC}}`
   - Identifica douleur points actuales del usuario
   - Busca features o documentos relacionados en `.quinoto-spec/proposals/`

3. **Generación del PRD**
   - Crea directorio `.quinoto-spec/prd/{{SLUG}}/`
   - Genera `prd.md` con la siguiente estructura:

## PRD.md Structure

```markdown
---
prd_id: {{PRD_ID}}
topic: {{PRD_TOPIC}}
audience: {{PRD_AUDIENCE}}
created_date: {{DATE}}
status: 🟡 Draft
version: 0.1
---

# Product Requirements Document: {{PRD_NAME}}

## 1. Resumen Ejecutivo
- Problema/Oportunidad identificados
- Propuesta de valor concise
- Impacto esperado (cuantificado si posible)

## 2. User Personas
| Persona | Descripción | Necesidades | Pain Points |
|---------|-------------|-------------|-------------|
|         |             |             |             |

## 3. Problem Statement
- **陈述 del Problema**: Descripción clara del problema
- **Contexto**: Cuándo, dónde, cómo ocurre
- **Impacto**: Cuantificación del dolor (tiempo, dinero, conversión)

## 4. Goals & Objectives
| Objetivo | Métrica | Target | Timeline |
|----------|---------|--------|----------|
|          |         |        |          |

## 5. Feature Requirements

### 5.1 Core Features
| Feature | Descripción | Prioridad | Estimación |
|---------|-------------|-----------|------------|
|         |             | P0/P1/P2  |            |

### 5.2 Secondary Features
| Feature | Descripción | Prioridad | Estimación |
|---------|-------------|-----------|------------|
|         |             | P0/P1/P2  |            |

### 5.3 Out of Scope
- Lista de features explícitamente excluidas

## 6. User Stories

### Must Have
- **COMO** [persona]
- **QUIERO** [功能]
- **PARA** [beneficio]
- **CRITERIOS DE ACEPTACIÓN**:
  - [ ] Given... When... Then...

### Should Have
- ...

## 7. User Flows
- Diagramas de flujo en Mermaid mostrando flujos principales
- Happy path y edge cases

## 8. Technical Considerations
- Constraints técnicos identificados
- Integraciones necesarias
- Dependencias externas
- Consideraciones de compliance/seguridad

## 9. Metrics & Success Criteria
| KPI | Baseline | Target | Measurement |
|-----|----------|--------|-------------|
|     |          |        |             |

## 10. Risks & Open Questions
| Riesgo/Pregunta | Impacto | Status |
|-----------------|---------|--------|
|                 |         | 🔴 Open |

## 11. Competitive Analysis (opcional)
- Productos competidores
- Diferenciadores propuestos

## 12. Appendices
- Research links
- Meeting notes
- Feedback collected

---

## 13. Validation Checklist
- [ ] Al menos 3 user personas definidas
- [ ] Al menos 5 user stories (2 Must Have, 2 Should Have, 1 Could Have)
- [ ] KPIs con baseline y target
- [ ] User flow diagramado
- [ ] Review interno completado
```

4. **Iteración y Refinamiento**
   - Presenta el draft al usuario
   - Recoge feedback y ajusta
   - Actualiza version a 0.2, 0.3, etc.

5. **Mark Done**
   - Cuando el PRD está validado, cambia status a 🟢 Validado
   - Usa skill `quinotospec-mark-done` si aplique

**Gestión de Prefijos:**
- Registra el PRD en `.quinoto-spec/prefix-registry.md` con prefijo `PRD-{código}` (ej. `PRD-0001`)

**Nota:** A diferencia de una Proposal Técnica, el PRD se enfoca en el "qué" y el "por qué", no en el "cómo". La implementación técnica viene después vía `/quinotospec.create-proposal`.
