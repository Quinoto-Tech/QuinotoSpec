---
name: Delta Spec — UI
description: Selectores E2E estables y estado observable de Mermaid
---

# Delta Spec: ui — Playwright Proposal Review

**Contract Version:** 1
**Proposal ID:** 2026-11-13-playwright-proposal-review
**Propuesta:** Playwright Proposal Review
**Prefijo:** PWRE-9f2c
**Fecha de Creación:** 2026-11-13
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Stable E2E Selectors
La UI MUST exponer atributos `data-testid` aditivos en el título de propuesta, el contenido Markdown, la lista de propuestas, la lista de tareas, la navegación principal, el buscador y el selector de tema, sin eliminar clases o IDs existentes.

#### Scenario: Selector estable en propuesta
- **GIVEN** la página `/proposals/<slug>`
- **WHEN** Playwright consulta `[data-testid="proposal-title"]`
- **THEN** encuentra exactamente un elemento con el título de la propuesta

#### Scenario: Compatibilidad con la UI actual
- **GIVEN** un cambio de estilos o de layout
- **WHEN** se ejecutan los tests existentes de `test-ui.sh`
- **THEN** los selectores por clase/ID siguen funcionando

### Requirement: Observable Mermaid State
Cada bloque Mermaid renderizado MUST exponer `data-mermaid-state` con valor `pending`, `rendered` o `error`, para que Playwright pueda esperar el render sin sleeps arbitrarios.

#### Scenario: Render exitoso
- **GIVEN** un Markdown con un bloque Mermaid válido
- **WHEN** la página termina de cargar
- **THEN** el contenedor reporta `data-mermaid-state="rendered"` y contiene un `<svg>`

#### Scenario: Error de sintaxis
- **GIVEN** un bloque Mermaid inválido
- **WHEN** Mermaid intenta renderizarlo
- **THEN** el contenedor reporta `data-mermaid-state="error"` y el review lo marca como BLOCKING

### Requirement: Review Artifact Isolation
La UI y el modo de review MUST NOT escribir en `.quinoto-spec/proposals/`, `.quinoto-spec/specs/` ni `.quinoto-spec/discovery/`; los screenshots MUST guardarse en `.quinoto-spec/reviews/.artifacts/`, ignorado por Git.

#### Scenario: Review read-only sobre la propuesta
- **GIVEN** una ejecución de `--playwright`
- **WHEN** el review termina
- **THEN** el hash de `proposal.md` no cambió y solo se crearon artefactos en `.quinoto-spec/reviews/`

---

## MODIFIED Requirements

(Ninguna)

---

## REMOVED Requirements

(Ninguna)

---

## RENAMED Requirements

(Ninguna)
