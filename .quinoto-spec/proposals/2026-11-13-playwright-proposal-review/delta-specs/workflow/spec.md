---
name: Delta Spec — Workflow
description: Playwright review mode, evidencia y degradación segura
---

# Delta Spec: workflow — Playwright Proposal Review

**Contract Version:** 1
**Proposal ID:** 2026-11-13-playwright-proposal-review
**Propuesta:** Playwright Proposal Review
**Prefijo:** PWRE-9f2c
**Fecha de Creación:** 2026-11-13
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Playwright Review Mode
El workflow `@quinotospec.review` MUST aceptar el flag opcional `--playwright` para ejecutar una revisión visual y E2E de la propuesta en la UI local.

#### Scenario: Review visual exitoso
- **GIVEN** una propuesta existente y Playwright app instalado
- **WHEN** el reviewer ejecuta `@quinotospec.review --playwright`
- **THEN** el workflow abre `/proposals/<slug>` en Chromium y produce evidencia JSON + Markdown

#### Scenario: Review visual con backend MCP
- **GIVEN** una propuesta existente y Playwright MCP configurado en el IDE
- **WHEN** el reviewer ejecuta `@quinotospec.review --playwright --playwright-backend mcp`
- **THEN** el agente usa las herramientas MCP y produce evidencia con `selected_backend: "mcp"`

### Requirement: Playwright Dependency Onboarding
Si Playwright app o MCP no están disponibles, el workflow MUST ofrecer tres opciones explícitas: instalar la app, configurar el MCP u omitir el review visual.

#### Scenario: Falta Playwright y el usuario elige app
- **GIVEN** un entorno sin Playwright app
- **WHEN** el workflow detecta la ausencia y el usuario elige "instalar app"
- **THEN** el orquestador instala `@playwright/test` y Chromium solo tras confirmación o `--install-playwright`, re-ejecuta el doctor y continúa

#### Scenario: Falta Playwright y el usuario elige MCP
- **GIVEN** un entorno sin Playwright app y un IDE con soporte MCP
- **WHEN** el usuario elige "configurar MCP"
- **THEN** el workflow escribe la configuración MCP del IDE o muestra el snippet, indica si hace falta reiniciar y usa el backend MCP

#### Scenario: El usuario elige omitir
- **GIVEN** un entorno sin Playwright
- **WHEN** el usuario elige "omitir" o pasa `--no-install-prompt`
- **THEN** el resultado es `skipped` y el review estándar continúa

### Requirement: Playwright Install Consent
El workflow MUST NOT instalar Playwright app, navegadores o configuración MCP sin consentimiento explícito.

#### Scenario: Modo no interactivo sin autorización
- **GIVEN** un entorno sin Playwright y sin TTY
- **WHEN** se ejecuta `--playwright` sin `--install-playwright`, `--install-playwright-mcp` ni `--no-install-prompt`
- **THEN** devuelve `action_required` con las tres opciones y un exit code distinto de 0

#### Scenario: `--yes` no autoriza instalación
- **GIVEN** un entorno sin Playwright
- **WHEN** se ejecuta `--playwright --yes`
- **THEN** no se instala nada y se devuelve `action_required`

### Requirement: Playwright Evidence Contract
El modo `--playwright` MUST escribir `.quinoto-spec/reviews/<slug>-playwright.json` con `schema_version`, `tool`, `browser`, `base_url`, `checks`, `console_errors`, `page_errors`, `failed_requests`, `screenshots`, `result` y `generated_at`.

#### Scenario: Evidencia inspeccionable
- **GIVEN** una ejecución de Playwright
- **WHEN** el orquestador termina
- **THEN** el JSON y el Markdown son legibles y referencian los screenshots generados

### Requirement: Playwright Review Blocking Rules
El modo `--playwright` MUST marcar como BLOCKING los errores de consola, `pageerror`, HTTP distinto de 200, requests same-origin fallidos y Mermaid no renderizado cuando el Markdown contiene bloques Mermaid.

#### Scenario: Mermaid roto
- **GIVEN** una propuesta con un bloque Mermaid inválido
- **WHEN** se ejecuta el review visual
- **THEN** el resultado es `failed` y el informe indica el bloque afectado

### Requirement: Playwright Review Isolation
El orquestador MUST ejecutar la UI en `127.0.0.1` o `localhost`, MUST rechazar slugs con path traversal y MUST detener el servidor en `finally`.

#### Scenario: Slug malicioso
- **GIVEN** un slug con `../` o una ruta absoluta
- **WHEN** se invoca el orquestador
- **THEN** la ejecución falla antes de iniciar la UI

---

## MODIFIED Requirements

(Ninguna)

---

## REMOVED Requirements

(Ninguna)

---

## RENAMED Requirements

(Ninguna)
