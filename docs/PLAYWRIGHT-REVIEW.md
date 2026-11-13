# Playwright Review

Review visual opcional de propuestas QuinotoSpec con Playwright. Abre la UI local en Chromium, verifica render, Mermaid, errores de consola, requests fallidos, overflow responsive, accesibilidad básica y guarda evidencia JSON + Markdown.

> **Estado:** experimental. El modo es opcional y no forma parte del runtime obligatorio del paquete.

## Requisitos

| Requisito | Obligatorio | Nota |
|---|---|---|
| Python 3.8+ | Sí | Orquestador y UI |
| Node.js 20+ | Solo para Playwright app/MCP | El paquete sigue funcionando sin Node |
| `@playwright/test` | Solo para backend `app` | Se instala en `agent-dist/skills/quinotospec-review/e2e` |
| Chromium | Solo para backend `app` | `npx playwright install chromium` |
| Playwright MCP | Solo para backend `mcp` | Configuración del IDE; puede requerir reinicio |

## Opciones de instalación

El review detecta si falta Playwright y ofrece tres caminos. **Nunca instala sin consentimiento.**

### 1. Instalar Playwright app

```bash
cd agent-dist/skills/quinotospec-review/e2e
npm install
npx playwright install chromium
```

O dejar que el orquestador lo haga tras confirmación:

```bash
python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
  --root . \
  --proposal 2026-11-13-mi-propuesta \
  --install-playwright
```

Características:

- Instala solo en `agent-dist/skills/quinotospec-review/e2e`.
- No usa `sudo`, no instala globalmente.
- Vuelve a ejecutar el doctor y continúa si Chromium quedó disponible.

### 2. Configurar Playwright MCP

El paquete no instala el MCP en todos los IDEs porque cada host usa un formato distinto. El adaptador escribe la configuración cuando puede o muestra el snippet:

```json
{
  "mcp": {
    "playwright": {
      "type": "local",
      "command": ["npx", "-y", "@playwright/mcp@latest"],
      "enabled": true
    }
  }
}
```

```bash
python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
  --root . \
  --proposal 2026-11-13-mi-propuesta \
  --install-playwright-mcp
```

Si el IDE requiere reinicio, el comando devuelve `action_required` y lo indica. No se simulan resultados MCP.

### 3. Omitir el review visual

```bash
python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
  --root . \
  --proposal 2026-11-13-mi-propuesta \
  --no-install-prompt --json
```

Resultado: `skipped`, exit code 0. El review estándar continúa.

## Uso

```bash
# Verificar dependencias
python3 -B agent-dist/skills/quinotospec-review/playwright_doctor.py --root . --check --json

# Review visual de una propuesta
python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
  --root . \
  --proposal 2026-11-13-mi-propuesta \
  --json

# Incluir una tarea
python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
  --root . \
  --proposal 2026-11-13-mi-propuesta \
  --task-id TSK-MNEM-xxxx-001 \
  --json

# Forzar backend
python3 -B agent-dist/skills/quinotospec-review/playwright_review.py \
  --root . \
  --proposal 2026-11-13-mi-propuesta \
  --playwright-backend app
```

Desde el workflow:

```text
@quinotospec.review --playwright TASK_ID BRANCH_NAME
```

## Flags

| Flag | Efecto |
|---|---|
| `--proposal <slug>` | Propuesta a revisar (obligatorio) |
| `--task-id <ID>` | Tarea opcional a revisar |
| `--playwright-backend auto\|app\|mcp` | Backend; `auto` prefiere app y luego MCP |
| `--install-playwright` | Autoriza instalar app + Chromium |
| `--install-playwright-mcp` | Autoriza configurar MCP |
| `--no-install-prompt` | Si falta Playwright, omite sin preguntar |
| `--require-playwright` | Si falta Playwright, falla |
| `--yes` | No interactivo; **no autoriza instalar** |
| `--json` | Salida JSON |
| `--check-only` | Solo ejecuta el doctor |
| `--timeout <segundos>` | Timeout del test runner (default 300) |

## Evidencia

Se escribe en `.quinoto-spec/reviews/`:

```text
.quinoto-spec/reviews/
├── <slug>-playwright.json
├── <slug>-playwright.md
└── .artifacts/
    └── <slug>-playwright/
        ├── screenshots/
        │   ├── desktop.png
        │   ├── tablet.png
        │   └── mobile.png
        └── playwright-raw.json
```

`*.json` y `*.md` son versionables. `.artifacts/` está ignorado por Git para evitar screenshots con datos sensibles.

### Resultados

| Resultado | Significado | Exit code |
|---|---|---|
| `pass` | Todos los checks OK | 0 |
| `warn` | Checks no bloqueantes (overflow, a11y smoke) | 0 |
| `fail` | Check BLOCKING o error de Playwright | 1 |
| `skipped` | El usuario omitió el review visual | 0 |
| `action_required` | Falta instalación o decisión del usuario | 3 |
| `error` | Error de configuración, contrato o ejecución | 1/2 |

### Checks BLOCKING

- HTTP distinto de 200 en la propuesta o tarea.
- Título o contenido de propuesta ausente.
- `console.error` no allowlisted.
- `pageerror`.
- Request same-origin fallido.
- Bloque Mermaid no renderizado cuando el Markdown lo contiene.

### Checks WARN

- Overflow horizontal en desktop, tablet o mobile.
- Screenshots faltantes.
- Accesibilidad smoke: `h1`, label del buscador, nombres accesibles.

## Seguridad

- La UI escucha solo en `127.0.0.1`.
- El orquestador rechaza slugs con path traversal, symlinks y rutas fuera de `.quinoto-spec/proposals/`.
- El review no modifica `proposal.md`, specs ni discovery.
- No se navega a URLs externas.
- No se instala nada sin confirmación o flag explícito.
- No se usa `sudo`.
- Los screenshots se guardan en `.artifacts/` ignorado por Git.

## CI

El job `ui-playwright` corre solo cuando cambian UI, review, tests o el fixture:

```bash
cd agent-dist/skills/quinotospec-review/e2e
npm ci
npx playwright install --with-deps chromium
cd ../../../..
QS_RUN_PLAYWRIGHT=1 bash tests/test-review-playwright.sh
```

## Troubleshooting

### `Playwright app: no disponible`

```bash
cd agent-dist/skills/quinotospec-review/e2e
npm install
npx playwright install chromium
```

### `Chromium no disponible`

```bash
cd agent-dist/skills/quinotospec-review/e2e
npx playwright install --with-deps chromium
```

### `MCP configurado pero el agente no lo ve`

- Reiniciar el IDE.
- Verificar la entrada MCP en la configuración del IDE.
- Ejecutar `playwright_doctor.py --check --json` y revisar `mcp.detected_in`.

### `Mermaid no renderiza`

- Verificar que el bloque tenga sintaxis Mermaid válida.
- Revisar `data-mermaid-state` en el HTML: `pending`, `rendered` o `error`.
- Ejecutar el review sin lazy loading no es necesario; el check espera hasta 20s.

### `overflow-mobile` en WARN

- Revisar tablas, bloques de código y enlaces largos.
- Los contenedores `.table-wrap` ya tienen scroll horizontal; el warning indica que algo fuera de ellos desborda.

## Limitaciones

- Solo Chromium en la primera fase.
- El backend MCP depende de las herramientas del IDE y no se puede ejecutar desde CI.
- No hay regresión visual pixel-perfect.
- La accesibilidad es un smoke test, no una auditoría WCAG completa.
- La instalación de MCP varía por IDE y puede requerir reinicio.

## Referencias

- `agent-dist/skills/quinotospec-review/playwright_doctor.py`
- `agent-dist/skills/quinotospec-review/playwright_review.py`
- `agent-dist/skills/quinotospec-review/e2e/`
- `tests/test-review-playwright.sh`
- `tests/fixtures/quinoto-spec-playwright/`
- `.quinoto-spec/proposals/2026-11-13-playwright-proposal-review/`
