# Cómo inspeccionar QuinotoSpec 3.2.0

Esta guía explica cómo revisar el release `3.2.0` sin modificar el checkout principal. La release está marcada como **beta/RC** y su tag local es `v3.2.0`.

## Qué contiene el release

La forma más segura de consultar el release es a través del tag, no de archivos sueltos del directorio de trabajo.

| Fuente | Para qué sirve |
|---|---|
| `v3.2.0` | Identifica el snapshot inmutable del release |
| `e3e4f31` | Commit actualmente asociado al tag `v3.2.0` |
| `.version` | Confirma la versión canónica del paquete |
| `manifest.json` | Confirma versión, inventario, estado beta/RC y fases |
| `CHANGELOG.md` | Resume qué cambió en la release |
| `agent-dist/bootstrap/quinotospec-bootstrap.md` | Muestra la integración de Party Mode |
| `/tmp/quinotospec-dist/` | Artefacto local generado; es temporal y puede reconstruirse |

El release incluye F3.2, Party Mode integrado en el bootstrap. **No** significa que F3.1 o F3.3 estén terminadas.

## 1. Confirmar que el checkout está en 3.2.0

Ejecuta desde la raíz del repositorio:

```bash
git status --short
git describe --tags --exact-match HEAD
git show --no-patch --format=fuller v3.2.0
```

Resultados esperados:

- `git status --short` no debe mostrar cambios si quieres inspeccionar el release sin modificaciones.
- `git describe --tags --exact-match HEAD` debe devolver `v3.2.0`.
- El commit esperado actualmente es `e3e4f31`.

Si el checkout tiene cambios posteriores, no los mezcles con la inspección del release. Usa un worktree o un archivo temporal como se explica abajo.

## 2. Ver el tag sin cambiar el checkout actual

Git permite leer cualquier archivo exactamente como estaba en el tag:

```bash
git show v3.2.0:.version
git show v3.2.0:manifest.json
git show v3.2.0:CHANGELOG.md | less
git show v3.2.0:agent-dist/bootstrap/quinotospec-bootstrap.md | less
```

Para ver el cambio del commit de release:

```bash
git show --stat --oneline v3.2.0
git show --format=fuller --no-ext-diff v3.2.0
git diff v3.2.0^..v3.2.0 --stat
```

Para listar los archivos incluidos en el tag:

```bash
git ls-tree -r --name-only v3.2.0
```

## 3. Abrir 3.2.0 en VS Code sin tocar `HEAD`

Crea una copia temporal del tag y ábrela con el comando `code`:

```bash
RELEASE_DIR="$(mktemp -d /tmp/quinotospec-3.2.0.XXXXXX)"
git archive v3.2.0 | tar -x -C "$RELEASE_DIR"
code "$RELEASE_DIR"
```

La copia contiene exactamente los archivos del tag, pero no es un worktree Git. Si prefieres conservar el historial y comparar ramas, usa un worktree:

```bash
git worktree add --detach /tmp/quinotospec-3.2.0-worktree v3.2.0
code /tmp/quinotospec-3.2.0-worktree
```

Cuando termines de inspeccionar el worktree, retíralo sin borrar el checkout principal:

```bash
git worktree remove /tmp/quinotospec-3.2.0-worktree
```

## 4. Revisar las partes nuevas de F3.2

Desde el tag, abre o consulta estos archivos:

```bash
git show v3.2.0:agent-dist/bootstrap/quinotospec-bootstrap.md
git show v3.2.0:agent-dist/workflows/quinotospec.party-mode.md
git show v3.2.0:agent-dist/skills/quinotospec-party-orchestrator/SKILL.md
git show v3.2.0:tests/test-bootstrap.sh
```

Comprueba especialmente que el bootstrap referencia:

```text
/quinotospec.party-mode
--subagents
```

La prueba de bootstrap verifica que esas dos referencias estén disponibles en el contexto de inicio de sesión.

## 5. Reconstruir y verificar el paquete 3.2.0

El directorio `/tmp/quinotospec-dist/` no es una fuente permanente. Genera de nuevo el tarball desde la copia exacta del tag:

```bash
DIST_DIR="$(mktemp -d /tmp/quinotospec-dist-3.2.0.XXXXXX)"
(cd "$RELEASE_DIR" && bash scripts/package-release.sh 3.2.0 "$DIST_DIR")
bash "$RELEASE_DIR/scripts/smoke-release.sh" "$DIST_DIR/quinotospec-3.2.0.tar.gz"
```

Verifica el checksum y lista el contenido:

```bash
(cd "$DIST_DIR" && sha256sum -c quinotospec-3.2.0.tar.gz.sha256)
tar -tzf "$DIST_DIR/quinotospec-3.2.0.tar.gz" | less
```

## 6. Probar la instalación en un proyecto aislado

Crea un proyecto temporal y ejecuta el installer desde la copia del release:

```bash
PROJECT_DIR="$(mktemp -d /tmp/quinotospec-project-3.2.0.XXXXXX)"
(cd "$PROJECT_DIR" && bash "$RELEASE_DIR/install.sh" --opencode --yes)
```

Después revisa el contexto instalado:

```bash
cat "$PROJECT_DIR/.opencode/commands/quinotospec.party-mode.md"
cat "$PROJECT_DIR/AGENTS.md"
```

El installer es transaccional y deja el manifest de ownership en `.quinoto-spec/ownership.json`. No borres ese manifest manualmente.

## 7. Comparar 3.2.0 con el trabajo posterior

Desde el checkout actual:

```bash
git log --oneline v3.2.0..HEAD
git diff --stat v3.2.0..HEAD
git diff v3.2.0..HEAD -- README.md AGENTS.md docs/ V3_ROADMAP.md
```

Si `git log v3.2.0..HEAD` no devuelve commits, el checkout actual es exactamente el release. Si devuelve commits, estás viendo trabajo posterior y debes usar `git show v3.2.0:<archivo>` para consultar la versión publicada.

## Comandos rápidos

```bash
# Identidad del release
git rev-parse v3.2.0^{commit}
git show --no-patch --format='%h %s' v3.2.0

# Versión y estado
git show v3.2.0:.version
git show v3.2.0:manifest.json

# Changelog
git show v3.2.0:CHANGELOG.md

# Bootstrap y Party Mode
git show v3.2.0:agent-dist/bootstrap/quinotospec-bootstrap.md
git show v3.2.0:agent-dist/workflows/quinotospec.party-mode.md

# Validación desde una copia del tag
(cd "$RELEASE_DIR" && bash scripts/validate-all.sh --strict)
```

## Diferencia entre release y fase

- **3.2.0** es la versión empaquetada y etiquetada.
- **F3.2** es la línea Party Mode, incluida en esa versión.
- **F3.1** (personalidades/TOML) y **F3.3** (`quinotospec-help`) siguen pendientes.
- El tag `v3.2.0` es la referencia para código; el changelog es la referencia para el resumen de cambios.
