---
name: Constitution Template
description: Template para generar .quinoto-spec/constitution.md con principios verificables del proyecto
---

# Constitución del Proyecto — {{PROJECT_NAME}}

> **Versión:** 1.0.0
> **Fecha:** {{DATE}}
> **Stack:** {{STACK}}
> **Owner:** {{OWNER}}
> **Estado:** draft — requiere aprobación explícita

Esta constitución define decisiones de arquitectura e implementación. No deroga reglas globales, legales, de seguridad ni los gates de TDD y verify-before-done; solo puede añadir restricciones más estrictas. Todos los workflows deben revisar sus principios.

---

## Principios Fundamentales

### I. Calidad de Código

- **CODE-01:** {{PRINCIPLE_QUALITY}}
- **CODE-02:** {{PRINCIPLE_SIMPLICITY}}

### II. Estándares de Testing

- **TEST-01:** {{PRINCIPLE_TESTING}}
- **TEST-02:** {{COVERAGE_OR_NA}}

### III. Consistencia de UX

- **UX-01:** {{PRINCIPLE_UX_OR_NA}}
- **UX-02:** {{ACCESSIBILITY_OR_NA}}

### IV. Requisitos de Performance

- **PERF-01:** {{PERFORMANCE_OR_NA}}
- **PERF-02:** {{PERFORMANCE_BUDGET_OR_NA}}

---

## Restricciones Adicionales

### Seguridad

- **SEC-01:** {{SECURITY_REQUIREMENT}}

### Cumplimiento Normativo

- **COMP-01:** {{COMPLIANCE_OR_NA}}

### Dependencias y Stack

- **DEP-01:** {{DEPENDENCY_RULE}}

---

## Flujo de Desarrollo

### Proceso de Review

- Todo PR debe verificar compliance con esta constitución.
- El checklist incluye calidad, testing, seguridad, performance y principios aplicables.
- Cada excepción registra razón, owner y fecha de revisión.

### Quality Gates

- [ ] **Simplicity Gate:** ¿Se puede hacer más simple sin perder valor?
- [ ] **Anti-Abstraction Gate:** ¿La abstracción está justificada por usos reales?
- [ ] **Integration-First Gate:** ¿Se probó integración antes de usar mocks profundos?
- [ ] **Constitution Gate:** ¿La implementación cumple todos los principios activos?

---

## Gobernanza

- Enmiendas requieren proposal, revisión y aprobación explícita.
- No se agregan capacidades especulativas.
- Los cambios breaking requieren una versión mayor.
- Una regla global siempre prevalece sobre una excepción local.

## Aprobación

- [ ] Principios revisados por el usuario
- [ ] Placeholders resueltos o marcados `N/A — no aplica`
- [ ] Estado aprobado explícitamente
- [ ] Registro de aprobación validado en `.quinoto-spec/approvals/{{APPROVAL_ID}}.json`
