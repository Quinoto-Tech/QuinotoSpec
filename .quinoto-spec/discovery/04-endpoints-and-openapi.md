# Endpoints y OpenAPI: QuinotoSpec

**Discovery Date:** 2026-09-27

Guardar en: .quinoto-spec/discovery/04-endpoints-and-openapi.md

## Veredicto: N/A — este paquete no expone endpoints HTTP

QuinotoSpec **no es un servicio**. No hay servidor web, ni framework HTTP, ni router, ni listener de
ningún tipo. No se encontraron `package.json`, `requirements.txt` con deps de red, ni `Dockerfile`
en el paquete.

Evidencia negativa:
- `install.sh` no contiene `curl`, `wget`, ni invocación de red.
- Los 15 scripts Python usan solo stdlib, sin `socket`/`http`/`urllib`.
- `manifest.json` no declara endpoints ni URLs de servicio.

## OpenAPI

> **Placeholder.** No aplica. Si en el futuro QuinotoSpec expone una API (por ejemplo un servicio
> que valide artefactos), este archivo debe documentar: `openapi: 3.1.0`, `info`,
> `servers`, y un `path` por endpoint con `operationId`, `parameters`, `requestBody` y responses
> tipados. Hoy ese documento no existe y no debe inventarse.

## Lo que sí existe: superficies de CLI

Como no hay red, la "API" del paquete es su **interfaz de línea de comandos**. Estas son las
superficies públicas y estables.

### 1. Instalador principal

```bash
./install.sh [--opencode|--cursor|--claude|--cline|--antigravity|--generic]
             [--global|--root <path>]
             [--yes|-y] [--verify] [--uninstall] [--version] [--help]
```

| Flag | Efecto | Fuente |
|---|---|---|
| `--opencode` | Target `~/.config/opencode/` (global) o `<root>/.opencode/` | `install.sh:829-831` |
| `--cursor` | `~/.cursor/` o `<root>/.cursor/` | `:828` |
| `--claude` | `~/.claude/` o `<root>/.claude/` | `:830` |
| `--cline` | `~/.config/cline/` o `<root>/.cline/` | `:832` |
| `--antigravity` | `~/.gemini/config/` o `<root>/.agents/` | `:827` |
| `--global` | Fuerza instalación global (fija `TARGET_ROOT`) | `:1076-1089` |
| `--root <path>` | Fuerza un directorio destino explícito | `:12` |
| `--yes` / `-y` | No interactivo; sin IDE flag ⇒ default `opencode` | `:1110-1113` |
| `--verify` | Solo verificación; sale 0/1 | `:1053-1073` |
| `--uninstall` | Desinstalación guiada por ownership manifest | `:1041-1047` |

**Contrato de salida**: `0` = éxito · `1` = fallo (dependencias, staging, verificación o commit) ·
`2` no se usa. Sin flags y con TTY ⇒ menú interactivo (`:1115-1137`).

### 2. CLIs de script (invocadas por los agentes)

Todas exponen `--root` y `--json`, y son **read-only salvo donde se indica**.

| Comando | Efecto |
|---|---|
| `contract.py {inspect,validate,changelog}` | Valida/inspecciona artefactos. `--strict` en `validate` |
| `rules_enforce.py` | Dispatcher de gobernanza. `--action`, `--mode strict\|warning`, `--check`, `--json` |
| `evidence_validate.py validate` | Valida evidencia estructurada. `--kind`, `--task-id`, `--require`, `--max-age` |
| `approval_validate.py validate` | Valida aprobación humana registrada. `--approval-id`, `--subject`, `--action` |
| `backup.py {create,verify,list,restore,cleanup}` | ÚNICO que **escribe** (en el store de backups). `--dry-run` en cleanup |
| `extension_manager.py` | Ciclo de vida de extensiones. `--json` |
| `template_resolver.py` | Resolución 4 capas. `--kind`, `--name` |
| `update_agents.py` | Genera `AGENTS.md`. Requiere exactamente uno de `--write` \| `--check` |
| `mimir/{index.py,search.py}` | Índice BM25. `search.py --cite`, `--trace PREFIX` |
| `valkyrie/rank.py` | Scoring de propuestas. `--suggest-next` |
| `jormungandr/check.py` | Detección de ciclos DAG. `exit ≠ 0` si hay ciclo |
| `bifrost/bifrost.py` | Federación multi-repo vía `git notes`. `--init/--status/--sync` |
| `blood-bond/*.py` | Análisis y predicción de patrones de trabajo |
| `huginn-muninn/check.sh` | Entropía. `--json`, emite `S_final` |
| `jormungandr/check.py` | (ver arriba) |

### 3. Contrato de salida JSON

Los CLIs que aceptan `--json` emiten un objeto con esta forma observable:

```json
{
  "ok": true,
  "errors": [],
  "warnings": [],
  "checks": [],
  "data": {}
}
```

Esto es **convencional, no un schema versionado** — no hay `json_schema` ni validación formal. Riesgo
detectado: los agentes dependen de estas claves sin contrato enforceable. Ver
`07-findings-and-recommendations.md`.

## Integraciones externas

Ninguna desde el código del paquete. La única integración documentada en el entorno de uso es
**agentic**: OpenCode, Cursor, Claude Code y compañía, que consumen el payload vía sus propios
mecanismos (hooks, plugins, descubrimiento de archivos).

## Autenticación y autorización

**N/A.** No hay endpoints, por lo tanto no hay auth que revisar.

La "autorización" del lado de los agentes es un concepto distinto y sí existe: `permissions` de
OpenCode y las reglas de gobernanza de `quinotospec-rules.md` (18 reglas, 7 de ellas BLOCKING). Eso
se documenta en `05-data-and-services.md` y `07-findings-and-recommendations.md`.

## Recomendaciones para pruebas de integración

No aplican a endpoints. Lo equivalente para CLIs es lo que ya existe:

- **Unit/integration por script**: los 7 `tests/test-*.py` invocan los scripts por `subprocess` con
  `--json` y asertan `exit ∈ {0,1,2}`.
- **E2E del instalador**: `tests/test-install-e2e.sh` (321 líneas) corre install → verify → manifest →
  rollback inyectado → uninstall, en un sandbox `mktemp -d`.
- **Smoke de release**: `scripts/smoke-release.sh` extrae el tarball y corre install/verify/uninstall.

Cobertura funcional adicional que valdría la pena (no existe hoy):
1. **Contrato de salida JSON** — test que valide las claves de `--json` de cada CLI (hoy nadie lo
   comprueba; los tests solo miran el exit code).
2. **Detección de versión del host** — el instalador no consulta la versión de OpenCode/Cursor, así
   que no puede advertir de un desajuste de API (la causa del incidente documentado en `07`).

## 🔗 Referencias

- `05-data-and-services.md` — servicios y modelo de datos
- `06-devops-ci-security.md` — CI y superficie de ataque
- `install.sh` — implementación de la CLI principal
