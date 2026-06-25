---
description: Inicializa la estructura .quinoto-spec/ desde cero sin ejecutar discovery completo. Crea directorios, archivos template y prepara el proyecto para usar QuinotoSpec. Si el proyecto está vacío, ofrece un wizard interactivo para generar un scaffold con el stack tecnológico deseado.
---

Objetivo: crear la estructura base de `.quinoto-spec/` en un proyecto nuevo, dejándolo listo para ejecutar `@quinotospec.discovery` como siguiente paso. No ejecuta discovery ni analiza el código — solo crea el esqueleto de directorios y archivos mínimos. Si el directorio está vacío (sin código ni archivos de configuración), el workflow ofrece generar un scaffold del proyecto.

## Precondiciones

- El directorio de trabajo será la raíz del proyecto.
- Si `.quinoto-spec/` ya existe, el workflow se detiene a menos que se use `--force`.

---

### Paso 1 — Verificar estado actual

1. Verificar si `.quinoto-spec/` ya existe.
2. Si existe y NO se usó `--force`:
   - Detener y mostrar: *"`.quinoto-spec/` ya existe. Usá `--force` para reinicializar (se preserva discovery y proposals existentes)."*
3. Si existe y se usó `--force`:
   - Advertir que se sobrescribirán archivos de configuración (no discovery ni proposals).
   - Pedir confirmación.

---

### Paso 2 — Detectar si el proyecto está vacío

Revisar si el directorio contiene marcadores de un proyecto existente. Un proyecto se considera **existente** si contiene al menos uno de los siguientes:

- `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`, `Gemfile`, `requirements.txt`, `Makefile`, `build.gradle`, `pom.xml`, `Dockerfile`, `docker-compose.yml`, `CMakeLists.txt`, `setup.py`, `setup.cfg`, `mix.exs`
- Directorios `src/`, `lib/`, `app/`, `include/`
- Archivos de código fuente: `*.py`, `*.js`, `*.ts`, `*.go`, `*.rs`, `*.rb`, `*.java`, `*.kt`, `*.cs`, `*.c`, `*.cpp`, `*.h`, `*.ex`, `*.exs`

**Si el proyecto NO está vacío:**
- Saltear los Pasos 3 y 4.
- Continuar directamente en el Paso 5 (Crear estructura de directorios).

**Si el proyecto ESTÁ vacío y se usó `--no-scaffold`:**
- Saltear los Pasos 3 y 4.
- Continuar directamente en el Paso 5.

**Si el proyecto ESTÁ vacío y se usó `--stack` (ej. `--stack python:fastapi:poetry:pytest:sqlite`):**
- Saltear el Paso 3 (wizard).
- Usar los valores del flag para el Paso 4 (scaffold).
- Validar que los valores sean válidos para el lenguaje elegido. Si algún valor no es válido, preguntar solo ese campo con el wizard.

**Si el proyecto ESTÁ vacío y NO se usó `--no-scaffold` ni `--stack`:**
- Continuar al Paso 3 (wizard interactivo).

---

### Paso 3 — Wizard interactivo de stack tecnológico

Presentar las preguntas **una a la vez**, bloqueando hasta recibir respuesta del usuario. No avanzar a la siguiente pregunta sin respuesta.

---

#### Pregunta 1 — Lenguaje principal

> **¿Qué lenguaje de programación querés usar para el proyecto?**
>
> 1. Python
> 2. JavaScript / TypeScript (Node.js)
> 3. Go
> 4. Rust
> 5. Ruby
> 6. Otro (especificar)

Esperar respuesta. Si elige "Otro", pedir que ingrese el nombre del lenguaje manualmente y continuar con preguntas de texto libre para los siguientes pasos.

---

#### Pregunta 2 — Framework

Mostrar opciones según el lenguaje elegido en P1.

**Si Python:**
> **¿Qué framework querés usar?**
>
> 1. FastAPI
> 2. Django
> 3. Flask
> 4. Litestar
> 5. Ninguno

**Si JavaScript / TypeScript:**
> **¿Qué framework querés usar?**
>
> 1. Next.js
> 2. Express
> 3. NestJS
> 4. React (Vite)
> 5. Vue (Vite)
> 6. Ninguno

**Si Go:**
> **¿Qué framework/router querés usar?**
>
> 1. Chi
> 2. Gin
> 3. Fiber
> 4. Echo
> 5. Ninguno (stdlib net/http)

**Si Rust:**
> **¿Qué framework querés usar?**
>
> 1. Actix Web
> 2. Axum
> 3. Rocket
> 4. Ninguno

**Si Ruby:**
> **¿Qué framework querés usar?**
>
> 1. Rails
> 2. Sinatra
> 3. Ninguno

**Si Otro (texto libre):**
> **¿Qué framework querés usar? (Escribí el nombre o "ninguno")**

Esperar respuesta.

---

#### Pregunta 3 — Package manager

Mostrar opciones según el lenguaje. Si el lenguaje tiene un solo package manager dominante, usar ese por defecto y saltear la pregunta.

**Si Python:**
> **¿Qué gestor de paquetes querés usar?**
>
> 1. Poetry
> 2. pip (requirements.txt o pyproject.toml)
> 3. uv

**Si JavaScript / TypeScript:**
> **¿Qué gestor de paquetes querés usar?**
>
> 1. npm
> 2. yarn
> 3. pnpm
> 4. bun

**Si Go:** Usar `go mod` (por defecto, no preguntar).

**Si Rust:** Usar `cargo` (por defecto, no preguntar).

**Si Ruby:** Usar `bundler` (por defecto, no preguntar).

**Si Otro (texto libre):**
> **¿Qué gestor de paquetes querés usar? (Escribí el nombre)**

Esperar respuesta.

---

#### Pregunta 4 — Framework de testing

Mostrar opciones según el lenguaje.

**Si Python:**
> **¿Qué framework de testing querés usar?**
>
> 1. pytest
> 2. unittest
> 3. Ninguno

**Si JavaScript / TypeScript:**
> **¿Qué framework de testing querés usar?**
>
> 1. Jest
> 2. Vitest
> 3. Ninguno

**Si Go:**
> **¿Qué framework de testing querés usar?**
>
> 1. testing (stdlib)
> 2. testify
> 3. Ninguno

**Si Rust:**
> **¿Qué framework de testing querés usar?**
>
> 1. cargo test (stdlib)
> 2. rstest
> 3. Ninguno

**Si Ruby:**
> **¿Qué framework de testing querés usar?**
>
> 1. RSpec
> 2. Minitest
> 3. Ninguno

**Si Otro (texto libre):**
> **¿Qué framework de testing querés usar? (escribí el nombre o "ninguno")**

Esperar respuesta.

---

#### Pregunta 5 — Base de datos

> **¿Qué base de datos querés usar? (Opcional)**
>
> 1. SQLite
> 2. PostgreSQL
> 3. MySQL
> 4. MongoDB
> 5. Ninguna (sin base de datos)

Esperar respuesta.

---

#### Pregunta 6 — Type checking (solo si aplica)

**Si JavaScript / TypeScript fue elegido en P1:**
> **¿Querés usar TypeScript o JavaScript plano?**
>
> 1. TypeScript (con tipado estricto)
> 2. JavaScript plano

**Si Python fue elegido en P1:**
> **¿Querés usar type checking con mypy?**
>
> 1. Sí, con mypy
> 2. Sin type checking

Otros lenguajes: saltear esta pregunta.

---

#### Confirmación final

Mostrar un resumen de todo lo seleccionado y pedir confirmación:

```
Resumen del stack:
  - Lenguaje:     {{LENGUAJE}}
  - Framework:    {{FRAMEWORK}}
  - Paquetes:     {{PACKAGE_MANAGER}}
  - Testing:      {{TESTING}}
  - Base de datos: {{DATABASE}}
  - Type check:   {{TYPE_CHECK}}

¿Continuar con este stack? (si/no)
```

Si responde "no", reiniciar el wizard desde la Pregunta 1.

Si responde "si", continuar al Paso 4.

---

### Paso 4 — Generar scaffold del proyecto

Ejecutar los comandos correspondientes según el stack elegido.

#### Comandos de inicialización por stack

| Lenguaje | Gestor | Comando base |
|----------|--------|-------------|
| Python | Poetry | `poetry new --name <nombre> .` |
| Python | pip | `mkdir -p src tests && echo "" > src/__init__.py && echo "" > tests/__init__.py` |
| Python | uv | `uv init --name <nombre>` |
| JS/TS | npm | `npm init -y` |
| JS/TS | yarn | `yarn init -y` |
| JS/TS | pnpm | `pnpm init` |
| JS/TS | bun | `bun init -y` |
| Go | go mod | `go mod init <nombre>` |
| Rust | cargo | `cargo init --name <nombre>` |
| Ruby | bundler | `bundle init` |

#### Instalación de framework

| Lenguaje | Framework | Gestor | Comando |
|----------|-----------|--------|---------|
| Python | FastAPI | Poetry | `poetry add fastapi uvicorn` |
| Python | FastAPI | pip | `mkdir -p src && echo "fastapi\nuvicorn" > requirements.txt` |
| Python | FastAPI | uv | `uv add fastapi uvicorn` |
| Python | Django | Poetry | `poetry add django` + `poetry run django-admin startproject core .` |
| Python | Django | pip | `pip install django` + `django-admin startproject core .` |
| Python | Django | uv | `uv add django` + `uv run django-admin startproject core .` |
| Python | Flask | Poetry | `poetry add flask` |
| Python | Flask | pip | `echo "flask" > requirements.txt` |
| Python | Flask | uv | `uv add flask` |
| JS/TS | Next.js | npm | `npx create-next-app@latest . --typescript` |
| JS/TS | Next.js | yarn | `yarn create next-app . --typescript` |
| JS/TS | Next.js | pnpm | `pnpm create next-app@latest . --typescript` |
| JS/TS | Express | npm | Instalar manual: `npm install express` + `npm install -D typescript @types/node @types/express` (si TS) |
| JS/TS | NestJS | npm | `npx @nestjs/cli new .` |
| JS/TS | React | npm | `npm create vite@latest . -- --template react-ts` (o `react` para JS) |
| JS/TS | Vue | npm | `npm create vite@latest . -- --template vue-ts` (o `vue` para JS) |
| Go | Chi | go mod | `go get github.com/go-chi/chi/v5` |
| Go | Gin | go mod | `go get github.com/gin-gonic/gin` |
| Go | Fiber | go mod | `go get github.com/gofiber/fiber/v2` |
| Go | Echo | go mod | `go get github.com/labstack/echo/v4` |
| Rust | Actix | cargo | Agregar `actix-web` y `actix-rt` a `Cargo.toml` |
| Rust | Axum | cargo | Agregar `axum` y `tokio` a `Cargo.toml` |
| Rust | Rocket | cargo | Agregar `rocket` a `Cargo.toml` |
| Ruby | Rails | bundler | `rails new .` |
| Ruby | Sinatra | bundler | Agregar `gem "sinatra"` al `Gemfile` |

#### Instalación de testing

| Lenguaje | Testing | Gestor | Comando |
|----------|---------|--------|---------|
| Python | pytest | Poetry | `poetry add --dev pytest` |
| Python | pytest | pip | `echo "pytest" >> requirements-dev.txt` |
| Python | pytest | uv | `uv add --dev pytest` |
| JS/TS | Jest | npm | `npm install -D jest @types/jest ts-jest` (si TS) |
| JS/TS | Vitest | npm | `npm install -D vitest` |
| Go | testify | go mod | `go get github.com/stretchr/testify` |
| Rust | rstest | cargo | Agregar `rstest` a `dev-dependencies` en `Cargo.toml` |
| Ruby | RSpec | bundler | Agregar `gem "rspec"` al `Gemfile` + `bundle install` + `rails generate rspec:install` (si Rails) |

#### Generar `.gitignore`

Crear un `.gitignore` en la raíz adaptado al stack. Usar contenido estándar de [gitignore.io](https://www.toptal.com/developers/gitignore) para el lenguaje y framework elegidos.

Al menos debe incluir entradas para:
- El lenguaje específico (ej. `__pycache__/`, `node_modules/`, `target/`, `vendor/`)
- El editor/IDE común (`.vscode/`, `.idea/`)
- El sistema operativo (`.DS_Store`, `Thumbs.db`)
- Archivos de entorno (`.env`, `.env.local`)
- El directorio `.quinoto-spec/` (siempre)

#### Generar `README.md`

Crear un `README.md` básico con:

```markdown
# {{NOMBRE_DEL_PROYECTO}}

## Stack

- **Lenguaje:** {{LENGUAJE}}
- **Framework:** {{FRAMEWORK}}
- **Gestor de paquetes:** {{PACKAGE_MANAGER}}
- **Testing:** {{TESTING}}
{{SI_HAY_DB}}- **Base de datos:** {{DATABASE}}
{{SI_HAY_TYPECHECK}}- **Type checking:** {{TYPE_CHECK}}

## Setup

{{COMANDOS_DE_INSTALACION}}

{{COMANDO_DE_EJECUCION}}

## Testing

{{COMANDO_DE_TESTING}}

## Estructura

```
{{ESTRUCTURA_DE_DIRECTORIOS}}
```
```

El nombre del proyecto se deriva del nombre del directorio actual (`basename $(pwd)`), o se le pregunta al usuario si el directorio tiene un nombre genérico (ej. `project`, `new-project`, `my-app`).

---

### Paso 5 — Crear estructura de directorios

Crear la siguiente estructura:

```
.quinoto-spec/
├── schema.yaml
├── specs/
│   └── README.md
├── discovery/
│   └── README.md
├── proposals/
├── scripts/
├── rfc/
└── changelog/
    └── .gitignore
```

### Schema YAML

Crear `.quinoto-spec/schema.yaml` copiando `agent-dist/templates/schema-template.yaml`:

El schema define el DAG de artefactos (propuesta, delta-specs, design, user-stories, tareas) y sus dependencias. El artifact engine (`quinotospec-artifact-engine`) usa este schema para calcular estado (done/ready/blocked).

Personalizacion: `@quinotospec.schema-fork` permite adaptar el schema al flujo del equipo.

### Specs README

El `specs/README.md` debe contener:

```markdown
# Specs — Source of Truth

Este directorio contiene la especificacion canonica del sistema, organizada por dominio/servicio.

Cada subdirectorio representa un dominio (ej. `auth/`, `payments/`, `ui/`) y contiene un `spec.md` con los requerimientos actuales del sistema.

## Formato

Los specs usan el formato de requerimientos con escenarios GIVEN/WHEN/THEN (opcionales):

### Requirement: Name
The system SHALL...

#### Scenario: Name (optional)
- **GIVEN** precondition
- **WHEN** action
- **THEN** expected outcome

## Actualizacion

Los specs se actualizan automaticamente al archivar propuestas que contienen `delta-specs/`.
Ver `@quinotospec.archive` para detalles del engine de merge.

## Inicializacion

Para proyectos existentes sin specs/, ejecuta `@quinotospec.specs-init` para generar specs iniciales desde el discovery o propuestas existentes.
```

El `discovery/README.md` debe contener:

```markdown
# Discovery

Ejecutá `@quinotospec.discovery` para generar los 8 archivos de documentación del proyecto.
```

---

### Paso 6 — Crear prefix-registry.md

Crear `.quinoto-spec/prefix-registry.md` con la tabla vacía:

```markdown
# Registro de Prefijos

| Prefijo | Propuesta | Fecha de Registro |
|---------|-----------|-------------------|
```

---

### Paso 7 — Crear changelog/ y .gitignore (v2)

Crear el directorio `.quinoto-spec/changelog/` con un `.gitignore` que excluya INDEX.md:

```bash
mkdir -p .quinoto-spec/changelog
```

Crear `.quinoto-spec/changelog/.gitignore`:

```gitignore
INDEX.md
```

**Nota sobre el formato:** QuinotoSpec usa formato v2 (append-only) por defecto. Cada entrada es un archivo separado `changelog/YYYY-MM-DD-PREFIX-SLUG.md`. INDEX.md es regenerable y gitignored — nunca se commitea.

Si se requiere compatibilidad con versiones anteriores de QuinotoSpec (v2.4.0 o anterior), agregar también `.quinoto-spec/quinoto-spec-changelog.md` (formato v1 legacy). La skill `quinotospec-update-changelog` detecta automáticamente el formato activo.

Crear la primera entrada con autodetección v2:

Usar la skill `quinotospec-update-changelog` para crear la primera entrada en `changelog/`:
- **Título**: QuinotoSpec Initialized
- **Resumen**: Se creó la estructura base de `.quinoto-spec/` y el directorio `changelog/` (formato v2).

**Si se generó scaffold**, agregar al resumen:
- Se generó scaffold del proyecto con: {{LENGUAJE}} + {{FRAMEWORK}} ({{PACKAGE_MANAGER}})

---

### Paso 8 — Copiar AGENTS.md (opcional)

Si se usa `--with-agents` y no existe `AGENTS.md` en la raíz del proyecto:
1. Buscar `AGENTS.md` en el paquete QuinotoSpec instalado.
2. Copiarlo a la raíz del proyecto.
3. Si no se encuentra el archivo fuente, advertir y continuar.

---

### Paso 9 — Resumen y próximos pasos

Mostrar al usuario:

**Si se generó scaffold:**
```
✓ Scaffold generado con {{LENGUAJE}} + {{FRAMEWORK}} ({{PACKAGE_MANAGER}})
✓ .gitignore y README.md creados
✓ Estructura QuinotoSpec inicializada en .quinoto-spec/
✓ specs/ creado — esperando inicializacion

Próximos pasos:
  1. @quinotospec.specs-init        → Inicializar specs desde discovery
  2. @quinotospec.discovery         → Documentar el proyecto
  3. Completar discovery/08-product-and-agreements.md
  4. @quinotospec.create-proposal   → Las propuestas generaran delta-specs/
```

**Si NO se generó scaffold (proyecto existente):**
```
✓ Estructura QuinotoSpec inicializada en .quinoto-spec/
✓ specs/ creado — esperando inicializacion

Próximos pasos:
  1. @quinotospec.specs-init        → Inicializar specs desde discovery
  2. @quinotospec.discovery         → Documentar el proyecto (si no ejecutado)
  3. Completar discovery/08-product-and-agreements.md
  4. @quinotospec.create-proposal   → Las propuestas generaran delta-specs/
```

---

### Paso 10 — Verificar Changelog

Verificar que la entrada se creó correctamente:

- Si v2: `ls .quinoto-spec/changelog/` debe mostrar un archivo `2026-06-12-ZZZZ-quinotospec-initialized.md` (o similar).
- Si se forzó v1: `.quinoto-spec/quinoto-spec-changelog.md` debe existir con la entrada correspondiente.

---

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--force` | Reinicializar aunque `.quinoto-spec/` ya exista (preserva discovery y proposals) |
| `--with-agents` | Copiar `AGENTS.md` a la raíz del proyecto |
| `--stack <stack>` | Especificar stack directamente sin wizard interactivo. Formato: `lenguaje:framework:package-manager:testing:database`. Ej: `python:fastapi:poetry:pytest:sqlite`. Usar `none` para campos opcionales. Solo funciona en proyecto vacío. |
| `--no-scaffold` | Saltear detección de proyecto vacío y wizard. Solo crea estructura `.quinoto-spec/`. Comportamiento clásico. |

---

## Ejemplos

```
# Proyecto existente: solo crea estructura .quinoto-spec/
@quinotospec.init

# Proyecto existente: estructura + AGENTS.md
@quinotospec.init --with-agents

# Forzar reinicialización
@quinotospec.init --force

# Proyecto vacío: wizard interactivo de stack
@quinotospec.init

# Proyecto vacío: saltar wizard, solo estructura .quinoto-spec/
@quinotospec.init --no-scaffold

# Proyecto vacío: stack directo, sin preguntas
@quinotospec.init --stack python:fastapi:poetry:pytest:sqlite

# Proyecto vacío: Go sin framework ni base de datos
@quinotospec.init --stack go:none:go_mod:stdlib:none

# Proyecto vacío: Next.js con TypeScript, Vitest, sin DB
@quinotospec.init --stack typescript:nextjs:pnpm:vitest:none

# Proyecto vacío: scaffold + AGENTS.md
@quinotospec.init --with-agents --stack ruby:rails:bundler:rspec:postgresql
```
