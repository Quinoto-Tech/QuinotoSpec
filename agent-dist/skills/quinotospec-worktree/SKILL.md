---
name: quinotospec-worktree
description: Aislar la implementación en un worktree Git seguro, reutilizando el aislamiento existente y verificando una baseline limpia.
---

# Skill: QuinotoSpec Worktree

Usa esta skill cuando `quinotospec.apply` solicite `USE_WORKTREE=true` o cuando el usuario pida aislar una implementación en un worktree Git. La skill es prompt-only: valida y guía las operaciones, pero no debe inventar una API nativa ni ocultar errores del proyecto.

## Índice

- [Contrato de entrada](#contrato-de-entrada)
- [Flujo de decisión](#flujo-de-decisión)
- [Project Setup](#project-setup)
- [Baseline limpia](#baseline-limpia)
- [Fallback sandbox](#fallback-sandbox)
- [Seguridad y límites](#seguridad-y-límites)
- [Integración con Apply](#integración-con-apply)

## Contrato de entrada

- `TASK_ID`: tarea canónica ya resuelta por Apply.
- `BRANCH_NAME`: nombre de branch ya resuelto por Apply.
- `BASE_REF`: referencia base explícita; no la adivines si el repositorio no la define.
- `USE_WORKTREE`: booleano; por defecto `false`.
- `WORKTREE_PATH`: ruta opcional; si falta, selecciona la primera ubicación segura según la prioridad de este documento.

Valida los valores contra el repositorio antes de usarlos. Rechaza rutas con `..`, separadores inesperados, saltos de línea, NUL y nombres de branch que no cumplan la convención del proyecto. No uses `eval`.

## Flujo de decisión

### Step 0: Detectar aislamiento existente

Desde la raíz del repositorio, ejecuta:

```bash
repo_root=$(git rev-parse --show-toplevel)
git_dir=$(git rev-parse --git-dir)
git_common=$(git rev-parse --git-common-dir)
```

Normaliza las tres rutas a rutas absolutas antes de compararlas. Si `GIT_DIR != GIT_COMMON`, el checkout ya es un linked worktree: no crees otro, reutiliza el contexto existente y registra la ruta y el branch actuales.

Si el directorio no es un repositorio Git, detén el flujo y reporta el bloqueo.

### Step 1: Preferir herramientas nativas

1. Detecta si el IDE o agente expone una herramienta nativa de worktree.
2. Pásale la raíz, `TASK_ID`, `BRANCH_NAME`, `BASE_REF` y la ruta solicitada.
3. Verifica el resultado con `git rev-parse --show-toplevel`, `git status --short`, `git branch --show-current` y la comparación `GIT_DIR`/`GIT_COMMON`.
4. Solo continúa si la herramienta devuelve un checkout aislado y verificable.

Si la herramienta nativa no existe, no la simules: pasa al fallback de Git.

### Step 2: Usar `git worktree` como fallback

Antes de crear nada:

1. Comprueba `git rev-parse --show-toplevel` y `git status --short`.
2. Si hay cambios no commiteados, no hagas `stash`, copia ni limpieza automática. Pregunta al usuario y documenta el bloqueo.
3. Comprueba que el branch no esté ya checked out en otro worktree.
4. Selecciona el primer directorio seguro de esta prioridad:
   - `.worktrees/`
   - `worktrees/`
   - `~/.config/quinotospec/worktrees/`
5. Para cada candidato dentro del repositorio, ejecuta antes de crear:
   ```bash
   git check-ignore -q -- "$WORKTREE_PATH"
   ```
   Si no está ignorado, detén el flujo y pide una decisión; no edites `.gitignore` silenciosamente.
6. Verifica que el destino no sea un symlink inesperado, que sus permisos sean privados y que no contenga secretos o datos de otro proyecto.
7. Crea el worktree con el branch resuelto, sin `--force`:
   ```bash
   git worktree add -b "$BRANCH_NAME" "$WORKTREE_PATH" "$BASE_REF"
   ```
   Si el branch ya existe y está libre, adjúntalo sin crear otro branch. Nunca dupliques la creación del branch con `git checkout -b`.
8. Cambia explícitamente el contexto operativo al worktree creado y repite las verificaciones del Step 0.

## Project Setup

Después de aislar el workspace:

1. Lee `.quinoto-spec/discovery/01-stack-profile.md`.
2. Si falta o está obsoleto, ejecuta `quinotospec-stack-detect` y no inventes comandos.
3. Pide confirmación antes de descargar dependencias o ejecutar scripts de instalación del proyecto objetivo.
4. Tras la confirmación, ejecuta el comando de instalación definido por el stack y su lockfile (`npm ci`, `pnpm install --frozen-lockfile`, `poetry install`, `bundle install`, `go mod download` o `cargo fetch`); no inventes flags.
5. No confundas la instalación de dependencias del proyecto con `install.sh`, que instala QuinotoSpec en el IDE.

## Baseline limpia

Antes de TDD, ejecuta el comando de tests del `01-stack-profile.md` en el worktree:

- `npm test` para el stack detectado;
- `pytest`;
- `bundle exec rspec`;
- `go test ./...`;
- `cargo test`;
- o el comando específico declarado por el proyecto.

La baseline debe pasar antes de escribir el test RED. Si falla por entorno, instalación o regresión existente, detén el Apply y usa `quinotospec-debug`; una baseline fallida no es un RED TDD.

Reporta al usuario la ruta, el branch, la base, el stack detectado y el resultado de la baseline.

## Fallback sandbox

Si aparece un error de permisos al usar un candidato local o la ubicación global:

1. No uses `chmod 777`, escalamiento de privilegios ni una ruta compartida.
2. Crea un sandbox privado con `mktemp -d` bajo `${TMPDIR:-/tmp}` y permisos `700`.
3. Verifica que no contenga secretos, datos de IDE ni archivos de otro proyecto.
4. Reintenta solo la creación del worktree en ese sandbox; no copies cambios no commiteados automáticamente.
5. Si el sandbox también falla, detén el flujo y reporta el error exacto.

## Seguridad y límites

- No ejecutes `git push`, `git merge`, `git worktree remove`, `git worktree prune`, `git branch -D`, `rm -rf` ni limpieza automática.
- No uses `--force`, `--detach` silencioso, `stash` automático ni `chmod 777`.
- No elimines ni modifiques `.gitignore` sin autorización.
- No copies `.env`, credenciales, tokens ni configuración ignorada del checkout original.
- Verifica siempre la raíz real del repositorio antes de cada acción sensible.
- Una limpieza posterior requiere confirmación explícita y revisión de cambios no commiteados.

## Integración con Apply

Si `USE_WORKTREE=false`, Apply continúa en el checkout actual. Si `USE_WORKTREE=true`, el orden obligatorio es:

1. contrato canónico y contexto;
2. gate constitucional;
3. worktree y baseline limpia;
4. `quinotospec-receive-review` si el cambio proviene de feedback;
5. `quinotospec-tdd`, implementación, debug y verificación en esa misma ruta;
6. changelog y `quinotospec-mark-done` en ese mismo contexto.

No implementes en el checkout original después de crear un worktree. Si no puedes cambiar el contexto, detén el trabajo.
