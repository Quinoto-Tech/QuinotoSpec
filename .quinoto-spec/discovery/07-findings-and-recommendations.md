# Hallazgos y Recomendaciones: QuinotoSpec

**Discovery Date:** 2026-09-27

Guardar en: .quinoto-spec/discovery/07-findings-and-recommendations.md

## Resumen ejecutivo

QuinotoSpec está **sólido donde más cuesta**: gobernanza ejecutable, instalación transaccional con
ownership por hash, y una suite de 20 tests que corre en CI sobre 2 SO × 2 versiones de Python.

El punto débil es **otro y es sistémico**: la integración con el host (el IDE). El instalador no
consulta la versión del IDE de destino, así que puede instalar artefactos contra un contrato de API
que ya cambió — y lo hace **sin ninguna señal**. Eso ya se convirtió en un incidente real y
verificable en OpenCode. Todo lo demás en este documento es menor al lado de eso.

| Severidad | Cantidad |
|---|---|
| 🔴 Crítica | 2 |
| 🟠 Media | 4 |
| 🟡 Baja | 6 |

---

## 🔴 CRÍTICA

### F-01 · El plugin de OpenCode usa un contrato de API obsoleto

**Severidad:** Crítica · **Owner sugerido:** refactor-specialist · **Estado:** mitigado manualmente, **sin fix en el paquete**

`agent-dist/plugins/opencode/quinotospec-plugin.js` exporta el contrato de plugin **v1**:

```js
// engram.ts (idéntico patrón):  export const Engram: Plugin = async (ctx) => {...}
// quinotospec-plugin.js:113-115:
module.exports = QuinotoSpecBootstrapPlugin;
module.exports.default = QuinotoSpecBootstrapPlugin;   // ← default es una FUNCIÓN
```

OpenCode **v2.0.16** valida el módulo contra:

```js
default: { id: string, effect: fn } | { id: string, setup: fn }
```

y falla en **cada arranque del servidor**. Evidencia en `~/.local/share/opencode/log/opencode.log`
(9 fallos, `run=dadcba65` / `run=9016ee45`):

| timestamp | target | ref | SchemaError |
|---|---|---|---|
| 2026-09-25 12:34:29 | `engram.ts` | `err_e5e24291` | `Missing key at ["default"]` |
| 2026-09-25 13:01:40 | `engram.ts` | `err_7751d75a` | `Missing key at ["default"]` |
| 2026-09-25 13:01:40 | `quinotospec-plugin.js` | `err_93feb9c4` | `Expected object at ["default"]` |
| 2026-09-27 15:18:54 | `engram.ts` | `err_a099146a` | `Missing key at ["default"]` |
| 2026-09-27 15:18:54 | `quinotospec-plugin.js` | `err_741eb0f0` | `Expected object at ["default"]` |
| 2026-09-27 15:18:55 | `engram.ts` | `err_925ac354` | `Missing key at ["default"]` |
| 2026-09-27 15:18:55 | `quinotospec-plugin.js` | `err_56335f83` | `Expected object at ["default"]` |
| 2026-09-27 15:20:01 | `engram.ts` | `err_d3b99bf1` | `Missing key at ["default"]` |
| 2026-09-27 15:20:01 | `quinotospec-plugin.js` | `err_b7f57ee6` | `Expected object at ["default"]` |

**Por qué los dos archivos fallan distinto** — la distinction es instructiva:
- `engram.ts` no tiene `default` en absoluto ⇒ `Missing key`
- `quinotospec-plugin.js` sí tiene `default`, pero es una función ⇒ `Expected object`

**Por qué TypeScript no avisó**: los tipos publicados de `@opencode-ai/plugin` (1.4.9 en el config
dir, 1.18.32 en el runtime dir) **siguen declarando la forma v1**:

```ts
export type PluginModule = { id?: string; server: Plugin; tui?: never };
```

O sea, el paquete oficial de tipos está desalineado del runtime. Un plugin puede compilar limpio y
fallar en carga.

**Impacto funcional**: en OpenCode v2 el plugin era el **único** camino para que `rules/` y
`bootstrap/` llegaran al agente. Sin él (y dado que `config.instructions` es no-op en v2), el
Bootstrap de sesión **no ocurre**.

**Estado actual**: mitigado a mano renombrando los archivos a `*.disabled`. El MCP de Engram sigue
funcionando (cubría la memoria), pero **el Bootstrap de QuinotoSpec no está inyectándose**.

**Recomendación**: ver F-01 en "Acciones inmediatas". El fix de fondo es reemplazar el plugin por
mecanismo nativo (`AGENTS.md`), no portarlo.

### F-02 · El `AGENTS.md` global se escribe donde OpenCode no lo lee

**Severidad:** Crítica · **Owner sugerido:** refactor-specialist

Con `--opencode --global`, `TARGET_ROOT` se fija a `$HOME/.config` (`install.sh:1086-1088`) y el
`AGENTS.md` generado se mueve a `$TARGET_ROOT/AGENTS.md` (`install.sh:1237`):

```bash
# install.sh:1086-1088
else
    TARGET_ROOT="$HOME/.config"      # opencode cae en el "else"
fi

# install.sh:1237
mv "$STAGED_AGENTS" "$TARGET_ROOT/AGENTS.md"    # → ~/.config/AGENTS.md
```

Pero OpenCode v2 solo carga como instrucciones globales **`~/.config/opencode/AGENTS.md`**.

**Verificado empíricamente** en esta máquina (instalación real `--opencode --global`, 201 archivos
owned):

```
EXISTE: /home/barba/.config/AGENTS.md (162 lineas)
NO:     /home/barba/.config/opencode/AGENTS.md
```

`verify_installation` (`:666-672`) solo comprueba que el archivo exista en `$target_root` — nunca que
la ruta sea la que el IDE lee. **El bug es invisible para el instalador.**

**Relación con F-01**: son el mismo defecto de diseño vistos desde dos ángulos. El plugin inyectaba
`bootstrap/` y `rules/` (fallando), y el mecanismo de reserva `AGENTS.md` está en la ruta equivocada.
**QuinotoSpec no tiene hoy ningún mecanismo funcional de Bootstrap en OpenCode v2.**

**Nota**: el mismo patrón afecta a `--cursor --global` (`TARGET_ROOT=$HOME` ⇒ `~/AGENTS.md`).
`--claude --global` sí es correcto (`~/.claude/AGENTS.md`).

---

## 🟠 MEDIA

### F-03 · La suite de tests está acoplada al plugin

**Owner sugerido:** test-writer

Eliminar el plugin rompe asserts en **3 suites + 2 checks de validación + 2 jobs de CI**:

| Ubicación | Assert |
|---|---|
| `tests/test-bootstrap.sh:27` | El artefacto `quinotospec-plugin.js` existe |
| `tests/test-bootstrap.sh:85-90` | `node --check` del plugin |
| `tests/test-bootstrap.sh:91-113` | **Contrato funcional en Node**: `toolAliases`, `config.skills.paths`, `config.instructions`, inyección en `messages[0].content` |
| `tests/test-install.sh:109` | `agent-dist/plugins` está entre los directorios esperados |
| `tests/test-install.sh:145` | El archivo del plugin está en las 24 rutas críticas |
| `tests/test-install-e2e.sh:144-148` | El plugin aplanado en `plugins/` |
| `tests/test-install-e2e.sh:157-161` | `--verify` pasa (⇒ `install.sh:641-645` falla sin plugin) |
| `tests/test-install-e2e.sh:163-185` | Hashes del ownership manifest ⇒ `install.sh:320-321` |
| `scripts/validate-all.sh:124` | `RUNTIME_FILES` incluye el plugin |
| `scripts/validate-all.sh:150` | `node --check` del plugin |
| `.github/workflows/ci.yml:86` | Job `lint-runtime` |
| `.github/workflows/ci.yml:154` | Job `structure` |

> El test de `test-bootstrap.sh:91-113` es el más valioso del set: es el único que verifica el
> **comportamiento** del plugin en runtime, no su existencia. Si se reemplaza el plugin por
> `AGENTS.md`, hay que escribir su equivalente para el mecanismo nuevo, no solo borrar el assert.

### F-04 · `install.sh` nunca consulta la versión del IDE de destino

**Owner sugerido:** architect

Es la **causa raíz** de que F-01 fuera indetectable. `check_dependencies` (`:507-561`) valida bash,
git y python — nada del IDE. El instalador escribe un plugin sin poder saber si su contrato sigue
siendo válido.

Agregar un chequeo de versión en pre-flight (p. ej. leer la versión del host si es detectable) convertiría
un fallo silencioso en un error accionable en el momento de instalar.

### F-05 · `hooks-opencode.json` es un artefacto muerto

**Owner sugerido:** doc-writer

`agent-dist/hooks/hooks-opencode.json` declara:
```json
{ "platform": "opencode", "events": ["session.start","session.compacted"],
  "command": "./agent-dist/hooks/session-start.sh" }
```

Ningún runtime lo lee: no está en ninguna ruta de descubrimiento de OpenCode, y su `command` apunta a
`./agent-dist/...`, **ruta que no existe post-instalación** (el archivo se copia a `hooks/`, según
`install.sh:722`). Solo se copia y se valida como JSON válido
(`validate-all.sh:123`, `test-bootstrap.sh:24,49`). El adaptador real de OpenCode es el plugin.

Candidato a eliminación, o a convertir en un artefacto real.

### F-06 · No hay auto-descubrimiento de tests

**Owner sugerido:** test-writer

`tests/run-all-tests.sh:42-61` es una **lista hardcodeada de 20 suites**. Agregar
`tests/test-nuevo.sh` no lo ejecuta nadie. Sin `Makefile`, `pytest.ini`, `conftest.py` ni `tox.ini`.

Riesgo concreto: alguien escribe un test, cree que corre en CI, y no corre. Debería colapsar a un
`for f in tests/test-*.sh` o añadir un check en `validate-all.sh` que detecte tests no registrados.

---

## 🟡 BAJA

### F-07 · `--strict` requiere Node pese a declararse opcional

`validate-all.sh:156-159` degrada a warning si falta Node, pero `:191` vuelve fatal cualquier warning
bajo `--strict`. Como `ci.yml:26` y `:42` usan `--strict`, **en la práctica el gate exige Node**.

### F-08 · `__pycache__/*.pyc` versionados

13 archivos `.pyc` (cpython-314) presentes en el árbol de `agent-dist/skills/`. `package-release.sh:21-31`
los excluye del tarball y `install.sh:1190` usa `python3 -B`, pero ensucian el árbol y el `.gitignore`
no los cubre en todas las rutas.

### F-09 · Fixtures muertos

`tests/fixtures/{node-project,python-project,empty-project}` no los lee ningún test. Servían para
demostrar stack-detect; ahora son peso muerto (y `python-project/requirements.txt` podría confundir
una auditoría de dependencias).

### F-10 · Campo `external_config` escrito y nunca leído

Se escribe en el ownership manifest (`:337-351`) y se registra en 3 sitios, pero **nadie lo consume**:
`uninstall` usa `hook_commands` + `ide` (`:946-978`). Código muerto que además sugiere una capacidad
que no existe.

### F-11 · El contrato de salida `--json` no está versionado

Los CLIs devuelven `{ok, errors, warnings, checks, data}` por convención. No hay JSON Schema ni
validación. Los agentes dependen de esas claves sin contrato enforceable. Los tests solo miran el
`exit code`, nunca el contenido del JSON.

### F-12 · Sin lock de concurrencia

Dos instalaciones simultáneas al mismo target colisionarían. El staging es único (`mktemp -d`), pero el
commit es **dos** `mv` (`:1216-1222`) y no atómico entre ambos. Ventana de inconsistencia en caso de
fallo entre los dos.

---

## Acciones inmediatas

### 1. Arreglar el Bootstrap de OpenCode (resuelve F-01 + F-02) 🔴

El plugin es **innecesario en v2**. Verificado contra la documentación oficial de v2:

| Artefacto | Ruta instalada | ¿Descubierto nativamente en v2? |
|---|---|---|
| Skills | `skills/` | ✅ global `~/.config/opencode/skills` |
| Agents | `agents/*.md` | ✅ `~/.config/opencode/agents/<name>.md` |
| Commands | `commands/*.md` | ✅ `~/.config/opencode/commands/` |
| Rules | `rules/quinotospec-rules.md` | ❌ **no** |
| Bootstrap | `bootstrap/quinotospec-bootstrap.md` | ❌ **no** |

Y el mecanismo que el plugin usaba está muerto por diseño:

> "The V2 config schema accepts an `instructions` array, but V2 does not currently resolve its files,
> glob patterns, or URLs. This configuration does not add instructions to the model yet."
> — [opencode.ai/v2/docs/instructions](https://opencode.ai/v2/docs/instructions)

**Camino recomendado**: usar `AGENTS.md`, que es el mecanismo nativo de instrucciones en v2
(`~/.config/opencode/AGENTS.md` para global, `<proyecto>/AGENTS.md` para proyecto). Eso resuelve
F-01 (el plugin desaparece) y F-02 (la ruta correcta) de una sola pasada, con **menos piezas** y sin
depender de una API que todavía no está documentada públicamente (`/build/plugins` devuelve 404).

**Trabajo asociado**: actualizar los asserts de F-03 y reemplazar el test funcional de
`test-bootstrap.sh:91-113` por uno del mecanismo nuevo.

### 2. Chequeo de versión del host en pre-flight (F-04) 🟠

Convertir el fallo silencioso en error accionable. Complementa la acción 1: aunque se elimine el
plugin, faltará chequear versiones para el futuro.

### 3. Limpieza de artefactos muertos (F-05, F-08, F-09, F-10) 🟡

Barato, bajo riesgo, mejora la señal del repo. Requiere update de `manifest.json`, `validate-all.sh`,
tests y docs.

## Roadmap de mejoras

### Corto plazo (1–2 días)

| # | Acción | Resuelve |
|---|---|---|
| A1 | Propuesta para migrar el Bootstrap de OpenCode a `AGENTS.md` | F-01, F-02 |
| A2 | Test que verifique la ruta de `AGENTS.md` **por IDE**, no solo su existencia | F-02 |
| A3 | Quitar `hooks-opencode.json` o hacerlo funcional | F-05 |
| A4 | `.gitignore` para `__pycache__`; borrar `.pyc` versionados | F-08 |
| A5 | Borrar fixtures muertos | F-09 |
| A6 | Eliminar `external_config` o implementarlo | F-10 |

### Mediano plazo (1–2 semanas)

| # | Acción | Resuelve |
|---|---|---|
| B1 | Chequeo de versión del IDE host en `check_dependencies` | F-04 |
| B2 | Auto-descubrimiento de tests + check de tests no registrados | F-06 |
| B3 | Test funcional del mecanismo de Bootstrap nuevo (reemplaza `test-bootstrap.sh:91-113`) | F-03 |
| B4 | JSON Schema para la salida `--json` de los CLIs + test de contrato | F-11 |
| B5 | Documentar en `docs/TROUBLESHOOTING.md` cómo detectar desajuste de versión del host | F-04 |

### Largo plazo (1 mes+)

| # | Acción | Resuelve |
|---|---|---|
| C1 | Lock de concurrencia en el instalador | F-12 |
| C2 | Extraer el "contrato de versión de host" a un archivo único **del que** plugin y docs lean, para que no vuelvan a divergir | F-01, F-04 |
| C3 | Migrar `V3_ROADMAP.md` (1585 líneas, mayor parte ya ejecutada) a un estado vivo más chico | deuda de docs |

## Optimizaciones de rendimiento y accesibilidad

**Rendimiento**: no aplica en el sentido clásico. La única métrica operativa es el **tiempo de
instalación** y la **frecuencia de fallos de carga de plugins** — esta última es exactamente F-01.

**Accesibilidad / DX** (más relevante que performance aquí):
- `README.md` (43 KB) y `README_EN.md` (40 KB) son extensos; el índice navegable importa.
- `V3_ROADMAP.md` tiene 1585 líneas y mezcla ejecutado/pendiente — cuesta saber qué está vivo.
- Los mensajes de error del instalador son claros y accionables ✅ (usa `print_error` a stderr).
- Falta un `docs/TROUBLESHOOTING.md` entry para "el plugin de OpenCode no carga" — el síntoma que
  acabamos de diagnosticar a mano.

## Checklist de seguimiento

| ID | Severidad | Acción | Owner | Estado |
|---|---|---|---|---|
| F-01 | 🔴 | Bootstrap de OpenCode vía `AGENTS.md` | refactor-specialist | Mitigado a mano, **sin fix** |
| F-02 | 🔴 | `AGENTS.md` global a la ruta correcta por IDE | refactor-specialist | ❌ Abierto |
| F-03 | 🟠 | Desacoplar tests del plugin | test-writer | ❌ Abierto (depende de F-01) |
| F-04 | 🟠 | Chequeo de versión del host | architect | ❌ Abierto |
| F-05 | 🟠 | Eliminar `hooks-opencode.json` muerto | doc-writer | ❌ Abierto |
| F-06 | 🟠 | Auto-descubrimiento de tests | test-writer | ❌ Abierto |
| F-07 | 🟡 | Resolver la contradicción de Node en `--strict` | devops-engineer | ❌ Abierto |
| F-08 | 🟡 | `.gitignore` para `__pycache__` | devops-engineer | ❌ Abierto |
| F-09 | 🟡 | Eliminar fixtures muertos | test-writer | ❌ Abierto |
| F-10 | 🟡 | `external_config`: quitar o implementar | refactor-specialist | ❌ Abierto |
| F-11 | 🟡 | JSON Schema para salida de CLIs | architect | ❌ Abierto |
| F-12 | 🟡 | Lock de concurrencia | architect | ❌ Abierto |

## 🔗 Referencias

- `02-overview.md` — riesgos resumidos
- `03-architecture.md` — por qué el plugin era la única vía del Bootstrap
- `06-devops-ci-security.md` — superficie de ataque y auditoría de dependencias
- Evidencia en log: `~/.local/share/opencode/log/opencode.log` (línea 186837 y vecinas)
