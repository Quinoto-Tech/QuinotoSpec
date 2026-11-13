# User Stories (Playwright Proposal Review)

**Proposal ID:** 2026-11-13-playwright-proposal-review
**Prefijo:** PWRE-9f2c
**Estado:** proposed

| ID | User Story | Criterios de Aceptación | Prioridad | Estimación | Servicio |
|---|---|---|---|---|---|
| US-PWRE-9f2c-001 | Como **reviewer**, quiero ejecutar `@quinotospec.review --playwright` para revisar una propuesta en la UI local sin salir de mi flujo de review. | - [ ] El flag `--playwright` está documentado en el workflow y en la skill de review<br>- [ ] El orquestador resuelve la propuesta, valida el contrato y arranca la UI en loopback con puerto efímero<br>- [ ] Espera `/health` antes de continuar y detiene el servidor en `finally` sin dejar procesos huérfanos<br>- [ ] Rechaza slugs con `..`, `/` o rutas fuera de `.quinoto-spec/proposals/` | P1 | L | review-workflow |
| US-PWRE-9f2c-002 | Como **reviewer**, quiero que el sistema detecte si tengo Playwright app, Chromium o MCP antes de pedirme instalar algo, para entender qué me falta. | - [ ] `playwright_doctor.py --check --json` detecta Node, `@playwright/test`, Chromium y MCP<br>- [ ] El JSON incluye `schema_version`, `app`, `mcp`, `options` y `recommended`<br>- [ ] El doctor no instala nada ni modifica configuración<br>- [ ] Existen tests para app presente, app ausente, MCP configurado y MCP ausente | P1 | M | review-workflow |
| US-PWRE-9f2c-003 | Como **reviewer sin Playwright app**, quiero que me ofrezcan instalarla y que la instalación solo ocurra si la autorizo, para habilitar el review visual de forma segura. | - [ ] Si falta la app, el menú muestra la opción "Instalar Playwright app" con requisitos y tamaño estimado<br>- [ ] `--install-playwright` instala `@playwright/test` y Chromium solo después de confirmación explícita<br>- [ ] La instalación no usa `sudo`, no es global y se limita a `agent-dist/skills/quinotospec-review/e2e/`<br>- [ ] Después de instalar, el doctor se re-ejecuta y el review continúa automáticamente<br>- [ ] La evidencia registra `install_action: "install-app"` y el consentimiento | P1 | M | review-workflow |
| US-PWRE-9f2c-004 | Como **reviewer que trabaja en un IDE con MCP**, quiero configurar Playwright MCP como alternativa a la app, para hacer la revisión visual de forma interactiva. | - [ ] Si falta la app, el menú muestra la opción "Configurar Playwright MCP" con el comando base y el snippet genérico<br>- [ ] `--install-playwright-mcp` escribe la configuración del IDE o muestra las instrucciones si no puede escribirla<br>- [ ] Si el IDE requiere reinicio, el workflow lo indica y no simula resultados MCP<br>- [ ] El backend `mcp` produce evidencia con `selected_backend: "mcp"` y los checks que el agente pudo ejecutar<br>- [ ] Si MCP no está disponible, se ofrece app u omitir | P1 | M | review-workflow |
| US-PWRE-9f2c-005 | Como **operador de CI**, quiero ejecutar el review visual de forma reproducible con Playwright app, para bloquear regresiones de render antes de mergear. | - [ ] Existe `agent-dist/skills/quinotospec-review/e2e/` con `package.json`, `playwright.config.js`, `proposal-review.spec.js` y `reporter.js`<br>- [ ] El harness usa Chromium y los viewports 1440×900, 768×1024 y 390×844<br>- [ ] Existe un fixture de propuesta con tablas, código y Mermaid<br>- [ ] `npx playwright test` pasa en verde sobre el fixture<br>- [ ] El reporter genera un JSON normalizado reutilizable por el orquestador | P2 | L | tests |
| US-PWRE-9f2c-006 | Como **reviewer**, quiero que el review visual detecte Mermaid roto, errores de consola, requests fallidos y overflow, para no aprobar propuestas que se ven mal en el navegador. | - [ ] La UI expone `data-testid` estables para título, contenido, listas, navegación, buscador y tema<br>- [ ] Cada bloque Mermaid expone `data-mermaid-state` con `pending`, `rendered` o `error`<br>- [ ] HTTP distinto de 200, `console.error`, `pageerror`, requests same-origin fallidos y Mermaid no renderizado son BLOCKING<br>- [ ] Overflow horizontal, screenshots faltantes y accesibilidad smoke son WARN<br>- [ ] `tests/test-ui.sh` sigue en verde después de agregar los selectores | P2 | M | ui |
| US-PWRE-9f2c-007 | Como **reviewer**, quiero recibir un informe con evidencia JSON, Markdown y screenshots, para adjuntar el resultado al review y decidir con datos. | - [ ] Se escribe `.quinoto-spec/reviews/<slug>-playwright.json` con `schema_version: 1` y bloque `dependency`<br>- [ ] Se escribe `.quinoto-spec/reviews/<slug>-playwright.md` con resumen, opción elegida, checks y hallazgos<br>- [ ] Los resultados `pass`, `warn`, `fail`, `skipped` y `action_required` se integran al checklist del review<br>- [ ] Los screenshots se guardan en `.quinoto-spec/reviews/.artifacts/`, ignorado por Git<br>- [ ] El review no modifica `proposal.md`, specs ni discovery | P2 | M | review-workflow |
| US-PWRE-9f2c-008 | Como **maintainer de QuinotoSpec**, quiero un job de CI condicionado y documentación de app/MCP, para mantener el modo visual sin encarecer todos los PRs. | - [ ] El job `ui-playwright` se ejecuta solo ante cambios en UI, review o `agent-dist/skills/quinotospec-review/e2e/`<br>- [ ] El job usa cache de navegador y tiene timeout menor a 10 minutos<br>- [ ] `docs/PLAYWRIGHT-REVIEW.md` documenta instalación app, configuración MCP, uso, outputs y troubleshooting<br>- [ ] `README.md` y `README_EN.md` mencionan el flag opcional<br>- [ ] El review de esta propuesta se ejecuta con `--playwright` como dogfooding y `validate-all.sh --strict` queda en verde | P2 | M | ci |

## Trazabilidad con la propuesta

| Fase de la propuesta | User Story | Delta Spec |
|---|---|---|
| 1. Fundación | US-PWRE-9f2c-001, US-PWRE-9f2c-002 | `workflow`: Playwright Review Mode, Playwright Review Isolation |
| 2. Onboarding | US-PWRE-9f2c-003, US-PWRE-9f2c-004 | `workflow`: Playwright Dependency Onboarding, Playwright Install Consent |
| 3. Harness Playwright | US-PWRE-9f2c-005 | `workflow`: Playwright Evidence Contract |
| 4. Selectores y checks | US-PWRE-9f2c-006 | `ui`: Stable E2E Selectors, Observable Mermaid State |
| 5. Evidencia y review | US-PWRE-9f2c-007 | `workflow`: Playwright Evidence Contract, Playwright Review Blocking Rules |
| 6. CI y docs | US-PWRE-9f2c-008 | `workflow` y `ui`: requisitos de aislamiento y documentación |

## Notas

- Las historias están ordenadas según el plan de implementación de la propuesta.
- La estimación total de las historias es **8–11 días**, consistente con la propuesta.
- La historia 003 y 004 son alternativas de onboarding; ambas comparten el mismo objetivo de habilitar el review visual y no son excluyentes entre sí.
- No se agregó columna de estado: el estado se deriva de las tareas asociadas.
