---
name: Proposal Template
description: Template para generar proposal.md con resumen ejecutivo, delta-specs y plan de implementacion
---

# Propuesta Técnica: {{PROPOSAL_NAME}}

**Contract Version:** 1
**ID:** {{DATE_PREFIX}}-{{SLUG}}
**Prefijo:** {{PREFIX}}
**Fecha de Creación:** {{DATE}}
**Estado:** 🟡 Propuesta
**Prioridad:** P1
**Complejidad:** Media
**Servicios Afectados:** {{SERVICIOS}}
**Autor:** {{AUTHOR}}

---

## Resumen Ejecutivo

{{SUMMARY — problema, solucion propuesta, impacto esperado, 3-5 lineas}}

---

## Contexto y Problema

### Problema Actual
{{descripcion del problema que motiva la propuesta}}

### Evidencia / Discovery
- Stack relevante: {{referencia a 01-stack-profile.md}}
- Arquitectura afectada: {{referencia a 03-architecture.md}}
- Endpoints/servicios: {{referencia a 04-endpoints-and-openapi.md}}
- Deuda/hallazgos: {{referencia a 07-findings-and-recommendations.md}}

---

## Solucion Propuesta

### Enfoque
{{enfoque tecnico a alto nivel}}

### Alternativas Consideradas
| Alternativa | Pros | Contras | Descartada porque |
|-------------|------|---------|-------------------|
| {{alt 1}} | {{pros}} | {{cons}} | {{razon}} |

### Delta Specs
Los requerimientos detallados estan en `delta-specs/`:
- `delta-specs/{{DOMAIN}}/spec.md` — secciones ADDED / MODIFIED / REMOVED / RENAMED con escenarios GIVEN/WHEN/THEN opcionales

---

## Alcance

### Incluye
- {{item 1}}
- {{item 2}}

### No Incluye (Out of Scope)
- {{item}}

### Servicios/Dominios Afectados
- {{servicio/dominio 1}}
- {{servicio/dominio 2}}

---

## Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|------------|
| {{riesgo}} | {{alta/media/baja}} | {{alto/medio/bajo}} | {{accion}} |

---

## Plan de Implementacion

1. **User Stories** → `user-stories.md` (desglose por valor)
2. **Tasks** → `*_tasks.md` (atomicas, verificables)
3. **Apply** → implementacion incremental con tests
4. **Changelog** → trazabilidad via `quinotospec-update-changelog`
5. **Archive** → merge de delta-specs en `specs/`

### Criterios de Exito
- [ ] {{criterio 1}}
- [ ] {{criterio 2}}

---

## Plan de Verificacion

- Tests: {{comando segun stack, ej. npm test / pytest / cargo test}}
- Validacion: `/quinotospec-syntax-validate --type proposal --slug {{SLUG}}`
- Review: `/quinotospec.review` contra criterios de aceptacion

---

## Referencias

- Discovery: `.quinoto-spec/discovery/`
- Schema: `.quinoto-spec/schema.yaml`
- Reglas: `agent-dist/rules/quinotospec-rules.md`
