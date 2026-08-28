---
name: Constitution Template
description: Template para generar .quinoto-spec/constitution.md con principios fundacionales del proyecto
---

# Constitucion del Proyecto — {{PROJECT_NAME}}

> **Version:** 1.0.0
> **Fecha:** {{DATE}}
> **Stack:** {{STACK}}
> **Estado:** 🟡 Borrador — requiere aprobacion

Esta constitucion supersede cualquier otra practica del proyecto. Todos los workflows, proposals y reviews deben verificar compliance.

---

## Principios Fundamentales

### I. Calidad de Codigo
- {{principio 1 — ej. "Simplicidad sobre abstraccion prematura"}}
- {{principio 2 — ej. "Codigo legible, testeable y documentado donde aporte valor"}}

### II. Estandares de Testing
- {{estandar 1 — ej. "TDD para logica de negocio, tests de contrato para integraciones"}}
- {{estandar 2 — ej. "Coverage minimo {{X}}% en dominios criticos, sin perseguir 100% vacio"}}

### III. Consistencia de UX
- {{principio 1 — ej. "Consistencia visual y de interaccion en todos los flujos"}}
- {{principio 2 — ej. "Accesibilidad WCAG {{nivel}}"}}

### IV. Requisitos de Performance
- {{requisito 1 — ej. "p95 < {{X}}ms en endpoints criticos"}}
- {{requisito 2 — ej. "Presupuesto de bundle < {{X}}KB"}}

---

## Restricciones Adicionales

### Seguridad
- {{restriccion — ej. "STRIDE/DREAD via @quinotospec.heimdallr para cambios con superficie de ataque"}}

### Cumplimiento Normativo
- {{requisito — ej. "GDPR / HIPAA / SOC2 segun aplique"}}

### Dependencias y Stack
- {{regla — ej. "Nuevas dependencias deben justificarse en proposal.md — Alternativas Consideradas"}}

---

## Flujo de Desarrollo

### Proceso de Review
- Todo PR debe verificar compliance con esta constitucion
- Review checklist incluye: calidad, testing, seguridad, performance

### Quality Gates
- [ ] **Simplicity Gate:** ¿Se puede hacer mas simple sin perder valor?
- [ ] **Anti-Abstraction Gate:** ¿La abstraccion se justifica con 3+ usos reales?
- [ ] **Integration-First Gate:** ¿Se probo integracion antes de unit mocks profundos?

---

## Gobernanza

- Enmiendas requieren: documentacion en proposal, revision del equipo, aprobacion explicita
- La complejidad debe ser justificada — "No speculative or 'might need' features"
- Versionado semantico de la constitucion; cambios breaking requieren major bump
