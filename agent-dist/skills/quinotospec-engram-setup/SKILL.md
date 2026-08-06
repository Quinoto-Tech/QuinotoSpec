---
name: quinotospec-engram-setup
description: Detecta Engram, lo instala si es necesario, configura el MCP server para OpenCode y establece ENGRAM_DATA_DIR dentro de .quinoto-spec/engram/.
---

# Quinotospec Engram Setup

Esta skill configura **Engram** (sistema de memoria persistente para agentes de IA) como dependencia por defecto del proyecto QuinotoSpec. Engram permite a los agentes recordar decisiones, arquitectura, bugs corregidos y contexto entre sesiones.

**Quick reference:** Engram es un binario Go con SQLite + FTS5 que expone herramientas MCP (`mem_save`, `mem_search`, `mem_context`, etc.) para persistir memoria de proyecto.

## Paso 1 — Detectar si Engram esta instalado

1. Ejecutar `which engram` o `engram version`.
2. Si esta instalado → mostrar version y continuar al Paso 3.
3. Si NO esta instalado → continuar al Paso 2.

## Paso 2 — Instalar Engram

Ofrecer opciones de instalacion segun el sistema operativo:

```bash
# macOS / Linux (Homebrew)
brew install gentleman-programming/tap/engram

# Linux (descarga directa)
# Ver https://github.com/Gentleman-Programming/engram/releases
```

Si el sistema no tiene Homebrew y no es Linux, recomendar descarga manual desde GitHub Releases.

Verificar instalacion: `engram version`

## Paso 3 — Configurar Engram para OpenCode

Ejecutar el comando de setup nativo de Engram:

```bash
engram setup opencode
```

Esto agrega la configuracion MCP en `~/.config/opencode/` para que el agente pueda invocar herramientas de memoria (`mem_save`, `mem_search`, etc.).

## Paso 4 — Configurar ENGRAM_DATA_DIR en el proyecto

Establecer el directorio de datos de Engram dentro del proyecto para que la memoria viaje con el codigo:

```bash
mkdir -p .quinoto-spec/engram
```

Agregar a `.gitignore` del proyecto:

```gitignore
# Engram memory data
.quinoto-spec/engram/
```

Esto asegura que la base de datos SQLite con las memorias del proyecto esta disponible para cualquier desarrollador que clone el repo, una vez que ejecute `quinotospec.init`.

## Paso 5 — Verificar configuracion

Ejecutar verificacion:

```bash
ENGRAM_DATA_DIR=.quinoto-spec/engram engram doctor
```

Confirmar que:
- La base de datos SQLite se creo correctamente en `.quinoto-spec/engram/engram.db`
- FTS5 (full-text search) esta activo
- No hay errores de permisos

## Paso 6 — Inicializar proyecto en Engram

```bash
ENGRAM_DATA_DIR=.quinoto-spec/engram engram search "quinotospec" --project quinotospec
```

Si el proyecto no existe, se crea automaticamente al guardar la primera memoria.

## Paso 7 — Reportar resultado

Mostrar al usuario:

```
✅ Engram configurado correctamente

   - Binario:   $(engram version)
   - MCP:       ~/.config/opencode/mcp.json actualizado
   - Base:      .quinoto-spec/engram/engram.db
   - Proyecto:  quinotospec
   
   Los agentes ahora pueden usar:
     - mem_save     → Guardar decisiones, bugs, hallazgos
     - mem_search   → Buscar memoria antes de iniciar workflows
     - mem_context  → Recuperar contexto de sesion anterior

   Memoria viaja con el proyecto en .quinoto-spec/engram/
```

## Environment Variables

| Variable | Valor por defecto | Descripcion |
|----------|-------------------|-------------|
| `ENGRAM_DATA_DIR` | `.quinoto-spec/engram` | Directorio de la base SQLite |
| `ENGRAM_PROJECT` | nombre del proyecto | Project name en Engram |

## Notas

- Engram usa **SQLite local** como fuente de verdad. No requiere servidor ni Docker.
- La configuracion MCP (`engram mcp`) se ejecuta como subproceso stdio del agente — no necesita `engram serve` corriendo.
- Para compartir memoria entre maquinas, usar `engram sync` + git, o Engram Cloud (opcional).
- Ver documentacion completa: https://github.com/Gentleman-Programming/engram
