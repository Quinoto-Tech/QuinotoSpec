---
name: quinotospec-quick-dev
description: Vía rápida para cambios Simple — tech-spec ligera, TDD RED-GREEN-REFACTOR y verificación antes de done, sin user stories.
---

# Skill: Quinotospec Quick Dev

> Velocidad con trazabilidad: una tech-spec corta, tests primero y evidencia antes de dar por terminado.

> **Fuente de verdad de ejecución:** `agent-dist/workflows/quinotospec.quick-dev.md`. Esta skill documenta la vía rápida para invocarla como capacidad; cualquier divergencia se resuelve sincronizando este archivo con el workflow.

## Cuando usar

- El `quinotospec-complexity-router` clasificó el cambio como `simple`
- Cambio de 2-3 archivos en un solo servicio, sin DB, auth ni API pública
- No hay propuesta activa que cubra el cambio y no se justifica crear una

## Cuando NO usar

- El router devuelve `complex` o `enterprise` -> usar `/quinotospec.create-proposal` (o `/quinotospec.flow`)
- Cambios de esquema de datos, autenticación, API pública o compliance -> mínimo `complex`

## Invocación

```bash
@quinotospec.quick-dev "Agregar validación de email en el formulario de contacto"
@quinotospec.quick-dev --files 2 --services 1 "Cachear la respuesta de /health"
```

## Pasos de Ejecución

### 1. Routing y contexto
- Ejecutar `python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files {N} --services {N} --json`.
- Si el track es `complex` o `enterprise`, detener y proponer `/quinotospec.create-proposal`.
- Leer `.quinoto-spec/discovery/01-stack-profile.md` (stack, comandos de test, convenciones) y `.quinoto-spec/constitution.md` si existe.

### 2. Tech-spec ligera
Crear `.quinoto-spec/quick-dev/YYYYMMDD-hhmm-{slug}.md` con: objetivo, archivos previstos, contrato (entradas/salidas), riesgos, plan de test y evidencia esperada. No reemplaza a una propuesta: es un contrato mínimo y desechable.

### 3. TDD
Aplicar `quinotospec-tdd`: RED -> GREEN -> REFACTOR, registrando comando y salida de cada fase.

### 4. Verificación
- Suite relevante del stack + `bash scripts/validate-all.sh --strict` si el repo usa QuinotoSpec como paquete.
- Registrar evidencia en `.quinoto-spec/evidence/{ID}/` cuando exista un ID de tarea o fix.
- Aplicar `quinotospec-verify-before-done` antes de declarar terminado.

### 5. Cierre
- Actualizar changelog con `/quinotospec.update-changelog`.
- Si el cambio creció a más de 3 archivos o tocó DB/auth/API, escalar a propuesta formal.
- Reportar archivos tocados, tests ejecutados, evidencia y riesgos residuales.

## Reglas

- No crear user stories ni archivos `*_tasks.md` para un track `simple`.
- No omitir tests ni `verify-before-done`, aunque el cambio sea pequeño.
- Dependencia externa nueva o cambio de contrato público -> escalar a `complex`.
- La tech-spec vive en `.quinoto-spec/quick-dev/` y no se mezcla con `proposals/`.
