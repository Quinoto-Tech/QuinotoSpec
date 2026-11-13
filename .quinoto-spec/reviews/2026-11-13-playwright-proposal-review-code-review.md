# Code Review — Playwright Proposal Review (PWRE-9f2c)

- **Fecha:** 2026-11-13
- **Alcance:** `2026-11-13-playwright-proposal-review` (8 user stories / 32 tareas)
- **Referencia del diff:** `HEAD` (79c86b1) → working tree. **No existe branch**: la implementación está sin commitear sobre `master`.
- **Resultado:** ❌ **Requiere cambios** — 3 hallazgos BLOCKING, 8 WARN, 3 INFO
- **Goldfish:** no solicitado (`--goldfish` no pasado) → omitido por diseño
- **Playwright visual review:** reutilizada la evidencia del dogfooding (`.quinoto-spec/reviews/2026-11-13-playwright-proposal-review-playwright.{json,md}`): `pass`, 9 checks, 2/2 Mermaid, 3 viewports, 0 console errors

## Gates ejecutados (evidencia fresca)

| Gate | Comando | Resultado |
|---|---|---|
| Contrato de artefactos | `contract.py validate --root . --strict` | ✅ 0 errores |
| Suite completa | `bash tests/run-all-tests.sh` | ✅ **29/29 suites** |
| Gate del paquete | `bash scripts/validate-all.sh --strict` | ✅ 0 errores, 0 warnings |
| Suite de la feature | `bash tests/test-review-playwright.sh` | ✅ 19 checks |
| Unit doctor | `python3 -B tests/test-playwright-doctor.py` | ✅ 4 tests |
| Unit orquestador | `python3 -B tests/test-review-playwright.py` | ✅ 6 tests |
| Dogfooding visual | `playwright_review.py --proposal <esta>` | ✅ `pass` |

## Checklist del workflow

| # | Punto | Resultado | Detalle |
|---|---|---|---|
| 1 | Criterios de Aceptación (DoD) | ❌ | 3 DoD incumplidos: path traversal (lateral), `QS_FORCE_MISSING_PLAYWRIGHT`, onboarding con Node 18 |
| 2 | Cobertura de tests | ⚠️ | 19 checks sólidos para skip/action_required/MCP/no-mutación; faltan `install-app`, éxito, fallo y timeout (el DoD los pide) |
| 3 | Convenciones del stack | ✅ | stdlib-only en Python, sin deps en runtime, `-B` y `dont_write_bytecode`, mensajes en español, scripts con `# shellcheck` limpio |
| 4 | Archivos declarados | ⚠️ | 4 archivos tocados fuera de la tabla "Archivos modificados" + un segundo workstream (discovery refresh) en el mismo árbol |
| 5 | Sin regresiones | ✅ | 29/29 suites y `validate-all --strict` verdes; UI existente con cambios aditivos |
| 6 | Compliance constitucional | ⚠️ | CODE-01 ✅, TEST-01 ✅, CODE-02 parcial (harness Node viaja en `agent-dist/`); falta registro de aprobación humana del override DoR |
| 7 | Goldfish review | ⏭️ | No aplica (`--goldfish` no solicitado) |
| 8 | Sin deuda técnica obvia | ✅ | Sin TODO/FIXME/`console.log`; ver INFO-1 por código redundante menor |

---

## BLOCKING

### B-01 · El rechazo de path traversal escribe evidencia fuera de `reviews/` y puede crashear

`playwright_review.py:427` usa el slug **sin validar** para nombrar archivos:

```python
data["evidence"] = write_evidence(root, args.proposal, data)   # args.proposal viene del usuario
```

`write_evidence` (`:230-238`) hace `reviews / (slug + "-playwright.json")`, así que un slug inválido escapa del directorio:

```bash
$ python3 -B .../playwright_review.py --root "$T" --proposal "../escape" --skip-contract --json
# exit=2, result=error  (correcto)
# PERO escribe:
.quinoto-spec/escape-playwright.json      <-- fuera de reviews/
.quinoto-spec/escape-playwright.md

$ ... --proposal "../../../opencode/PWNED2" --skip-contract --json
# exit=1 con Traceback (FileNotFoundError) — no devuelve el JSON documentado
```

- **DoD afectado:** "El orquestador rechaza slugs con `..`, `/` o rutas fuera de `.quinoto-spec/proposals/`". Rechaza el *acceso*, pero el efecto lateral escribe fuera del sandbox y, con suficiente profundidad, tira un traceback al usuario.
- **Fix sugerido (2 líneas):** sanitizar el nombre (`re.sub(r"[^A-Za-z0-9._-]", "_", slug)`) y, en el branch de `ReviewError`, no escribir evidencia (o escribirla en `reviews/invalid-<hash>`) + envolver el write en `try/except OSError` que devuelva `EXIT_USAGE` con JSON.
- **Test que falta:** assert de que tras un slug inválido **no** se crea ningún archivo fuera de `reviews/`.

### B-02 · `QS_FORCE_MISSING_PLAYWRIGHT` está documentado y no existe

El proposal lo declara como variable de entorno (`proposal.md:271`) y como criterio de aceptación (`:487`, prueba manual del onboarding). `grep` sobre `agent-dist/` y `tests/` no encuentra ninguna implementación.

- **Impacto:** el DoD "Prueba manual del onboarding con `QS_FORCE_MISSING_PLAYWRIGHT=1`" no se puede ejecutar; la doc promete una palanca inexistente. Hoy el onboarding se testea con `PATH` vacío, que es más frágil.
- **Fix:** implementar el override en `playwright_doctor.check_environment` (`env.get("QS_FORCE_MISSING_PLAYWRIGHT") == "1"` → `app`/`mcp` no disponibles) o eliminar la variable del proposal y del DoD.

### B-03 · El onboarding promete Node 18+, pero Playwright exige Node ≥ 20

| Fuente | Dice |
|---|---|
| `playwright_doctor.py:188,196,210` | `Node.js 18+` (`node_ready = major >= 18`, `:174`) |
| `docs/PLAYWRIGHT-REVIEW.md:12` | `Node.js 18+` |
| `e2e/package.json` → lock `@playwright/test 1.65.0` | `"engines": {"node": ">=20"}` |

Un usuario con Node 18 recibe `available: true`, elige "instalar app" y falla (o instala algo que no corre). La feature existe justamente para no dejar al usuario en un callejón.

- **Fix:** `>= 20` en doctor, prompt, docs y proposal; agregar test con `node major = 18` → `install-app.available = false` y blocker claro.

---

## WARN

| ID | Hallazgo | Evidencia | Fix |
|---|---|---|---|
| W-01 | `configure_mcp` en modo `auto` sin config previa escribe `./mcp.json` (IDE `generic`), que ningún IDE lee, y devuelve `configured: true` | `mcp_config.py:51-72`; el test solo verifica `dependency.mcp.configured` | Exigir `--ide`, o devolver `configured: false` + snippet y `requires_manual_step` |
| W-02 | `@playwright/mcp@latest` sin pin y `npm install` (no `npm ci`) | `mcp_config.py:14`, `playwright_review.py:151-155` | Pin de versión para MCP; `npm ci` para reproducibilidad |
| W-03 | La evidencia versionable filtra rutas absolutas del equipo | `reviews/...-playwright.json`: `screenshots: ["/home/barba/..."]`, `e2e_dir`, `mcp.detected_in` | Guardar rutas relativas a `root` |
| W-04 | `start_ui` deja `stdout`/`stderr` en `PIPE` sin drenar y no mata el grupo de procesos | `playwright_review.py:101-120`, `:123-134` | `DEVNULL` o hilo lector; `start_new_session=True` + `killpg` |
| W-05 | El job nuevo usa `actions/setup-node@v4` (runtime Node 20) y el guard `test-ci-config.sh` no lo cubre | `ci.yml` job `ui-playwright` | Bump a major actual y sumarlo a `MINIMUMS` del guard |
| W-06 | Archivos tocados no declarados + segundo workstream en el mismo árbol | `readers.py`, `check-links.sh`, `validate-all.sh`, `install.sh`; discovery 01–08, `CHANGELOG.md`, `prefix-registry.md` | Declararlos en el proposal y separar el discovery refresh en su propio commit/branch |
| W-07 | Cobertura DoD incompleta del orquestador | `tests/test-review-playwright.py`: 6 tests; faltan `install-app`, éxito, fallo, timeout | Agregar los 4 casos (mock de `subprocess`) |
| W-08 | "Fuera del payload instalable" es inexacto: el harness viaja al config del usuario | Instalé en un proyecto temporal: quedan `.opencode/skills/quinotospec-review/e2e/{package.json,playwright.config.js,proposal-review.spec.js,reporter.js}` | Ajustar la afirmación en proposal/docs (node_modules **sí** queda fuera) o excluir `e2e/` del payload |
| W-09 | Override DoR/DoD sin registro de aprobación humana | `.quinoto-spec/approvals/` solo tiene `QSPE-REVIEW-HANDOFF.json` | Registrar `approvals/PWRE-9f2c-dor-override.json` y validarlo con `rules_enforce.py` |

## INFO

- **I-01:** `--check-only` tiene dos ramas idénticas (`:410-415`); `build_install_commands(e2e_dir)` recibe un parámetro que no usa; `--e2e-dir` (oculto) permite ejecutar `npx playwright test` en un cwd arbitrario.
- **I-02:** La tabla de checks del proposal promete 10; se implementan 8 (falta "enlaces internos responden 200" y un check explícito de "3 screenshots generados"). El check de título no compara con el título real de la propuesta, solo verifica existencia.
- **I-03:** `a11y` cubre `h1` y label del buscador (bien), pero el proposal sugiere "nombres accesibles en controles" — el `select` de proyecto y el botón de tema no se verifican.

---

## Lo que está bien (no tocar)

- Degradación en tres caminos con consentimiento explícito; `--yes` **no** instala (probado).
- `resolve_proposal` rechaza `/`, `\`, `..`, symlinks y valida el padre (el bug de B-01 es el *efecto lateral*, no la validación).
- Validación del contrato antes de arrancar y `stop_ui` en `finally`.
- Cambios de UI **aditivos**: `data-testid`, `data-mermaid-state`, `table-wrap`, label oculto para el buscador; `test-ui.sh` sigue verde.
- `install.sh`/`package-release.sh` excluyen `node_modules`, `__pycache__` y `.bin`; el binario no contamina el payload.
- Evidencia JSON con `schema_version`, `dependency`, checks y screenshots; el dogfooding sobre esta misma propuesta pasa.

## Veredicto

**Requiere cambios.** Los tres BLOCKING son acotados (sanitizar un nombre de archivo, implementar o quitar una env var, subir el umbral de Node a 20) y no tocan la arquitectura. Con B-01..B-03 resueltos y los WARN de pin/reproducibilidad cubiertos, la propuesta queda lista para mergear como capacidad `experimental`.

**Antes de mergear, además:** commitear en un branch `feature/PWRE-9f2c-...` (hoy está sobre `master` sin commit), separar el discovery refresh y correr el job `ui-playwright` en CI por primera vez.

---

## Actualización post-fix (2026-11-13)

Se aplicaron los BLOCKING y los WARN de bajo costo, con test RED antes del fix:

| Hallazgo | Estado | Evidencia |
|---|---|---|
| B-01 path traversal en evidencia | ✅ Resuelto | `safe_slug()` sanitiza el nombre; el write del camino de error va en `try/except OSError`. Tests: `test_invalid_slug_does_not_write_outside_reviews`, `test_deep_traversal_returns_json_not_traceback` (RED antes: escribía `.quinoto-spec/escape-playwright.json` y con `../../..` tiraba Traceback) |
| B-02 `QS_FORCE_MISSING_PLAYWRIGHT` | ✅ Implementado | `check_environment` fuerza app/MCP ausentes y marca `forced_missing_playwright`. Test: `test_force_missing_playwright_env_var` |
| B-03 Node 18+ vs engines >=20 | ✅ Resuelto | `MIN_NODE_MAJOR = 20`, textos y docs actualizados. Test: `test_node_18_is_not_enough` |
| W-02 `npm install` / pin MCP | ⚠️ Parcial | `npm ci` (determinista con lockfile). `@playwright/mcp@latest` sigue sin pin (documentado) |
| W-03 rutas absolutas en evidencia | ✅ Resuelto | `sanitize_paths`/`display_path`: relativas al repo o `~/`. Test: `test_evidence_paths_are_relative_for_versioning`. Dogfooding regenerado sin `/home/<user>` |
| W-04 PIPE sin drenar / huérfanos | ✅ Resuelto | Log a `ui-server.log`, `start_new_session=True` y `killpg` en `stop_ui` |
| W-05 setup-node Node 20 | ✅ Resuelto | `actions/setup-node@v7` y `WC_SETUP_NODE=7` en `tests/test-ci-config.sh` |
| W-07 tests faltantes del DoD | ✅ Resuelto | 13 tests de orquestador (install-app, fallo, éxito, timeout, traversal, privacidad) y 6 del doctor |
| W-08 "fuera del payload" inexacto | ✅ Documentado con precisión | Proposal y código aclaran que el harness viaja y `node_modules`/navegadores no |
| W-01 MCP "generic" reporta `configured: true` | ⏳ Pendiente | Requiere decisión de UX (exigir `--ide` o devolver snippet) |
| W-06 archivos no declarados / sin branch | ✅ Resuelto | Commits separados: feature PWRE, discovery refresh y evidencia/review |
| W-09 aprobación humana del override DoR | ⏳ Pendiente | Requiere tu decisión explícita para registrar `.quinoto-spec/approvals/` |

**Gates post-fix:** contrato OK · `lint-shell` 42 scripts clean · **29/29 suites** · `validate-all --strict` 0/0 · `test-review-playwright.sh` 19 checks · orquestador 13/13 · doctor 6/6 · dogfooding Playwright `pass` (9 checks, 2/2 Mermaid, 3 viewports, 0 console errors).

### Follow-up: macOS `/var` -> `/private/var` (run 43480704090)

El primer push dejo `test (macos-latest)` rojo: comparar `str(path)` con un path resuelto falla en macOS porque `/var` es symlink. Era relevante de verdad: `display_path` (el fix de W-03) devolvia rutas **absolutas** en macOS en vez de relativas, o sea la fuga de privacidad seguia viva en Mac.

- `display_path` resuelve `root` antes de comparar.
- Tests comparan con `.resolve()`; nuevo `test_evidence_paths_work_under_symlinked_root` (reproducible en Linux).
- La suite ahora imprime el traceback cuando los unit tests fallan.
