---
description: Via rapida para cambios simples — tech-spec ligera, TDD y sin user stories intermedias.
---

# Workflow: Quick Dev

[INSTRUCCIÓN MAESTRA]
Debes implementar un cambio de complejidad **Simple** sin recorrer el ciclo completo de propuesta, user stories y tareas. El objetivo es velocidad con trazabilidad: una tech-spec corta, tests primero y evidencia antes de dar por terminado.

**Cuándo usar este workflow:**

- El `quinotospec-complexity-router` clasificó el cambio como `simple`
- Cambio de 2-3 archivos en un solo servicio, sin DB, auth ni API pública
- No hay propuesta activa que cubra el cambio y no se justifica crear una

**Cuándo NO usar este workflow:**

- El router devuelve `complex` o `enterprise` -> usar `/quinotospec.create-proposal`
- Cambios de esquema de datos, autenticación, API pública o compliance -> mínimo `complex`

**Parámetros:**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| Descripción del cambio | Sí | Qué hay que hacer y por qué |
| `--files` `N` | No | Archivos estimados (para re-ejecutar el router) |
| `--services` `N` | No | Servicios afectados |
| `--override simple` | No | Fuerza el track cuando el usuario lo decide |

**Invocación:**

```bash
@quinotospec.quick-dev "Agregar validación de email en el formulario de contacto"
@quinotospec.quick-dev --files 2 --services 1 "Cachear la respuesta de /health"
```

---

## Paso 0 — Routing y contexto

1. Ejecutar el router:

   ```bash
   python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files {N} --services {N} --json
   ```

2. Si el track resultante es `complex` o `enterprise`, detener y proponer `/quinotospec.create-proposal`.
3. Leer `.quinoto-spec/discovery/01-stack-profile.md` para obtener stack, comandos de test y convenciones.
4. Leer `.quinoto-spec/constitution.md` si existe: sus principios aplican aunque no haya propuesta.

## Paso 1 — Tech-spec ligera

Crear `.quinoto-spec/quick-dev/YYYYMMDD-hhmm-{slug}.md`:

```markdown
# Quick Dev: {slug}
- **Fecha**: YYYY-MM-DD HH:MM
- **Track**: simple (router: {rationale})
- **Objetivo**: {qué cambia y por qué}
- **Archivos previstos**: {lista}
- **Contrato**: {entradas/salidas o comportamiento esperado}
- **Riesgos**: {qué puede romperse}
- **Plan de test**: {tests a escribir}
- **Evidencia esperada**: `.quinoto-spec/evidence/{ID}/`
```

La tech-spec no reemplaza a una propuesta: es un contrato mínimo y desechable para el cambio.

## Paso 2 — TDD

1. Aplicar `quinotospec-tdd`: RED -> GREEN -> REFACTOR.
2. Escribir primero el test que falla y registrar la salida.
3. Implementar el mínimo cambio que lo hace pasar.
4. Refactorizar con la red de seguridad del test.

## Paso 3 — Verificación

1. Ejecutar la suite relevante del stack (`npm test`, `pytest`, `go test ./...`, etc.).
2. Ejecutar `bash scripts/validate-all.sh --strict` si el repositorio usa QuinotoSpec como paquete.
3. Registrar evidencia en `.quinoto-spec/evidence/{ID}/` cuando exista un ID de tarea o fix.
4. Aplicar `quinotospec-verify-before-done` antes de declarar el cambio terminado.

## Paso 4 — Cierre

1. Actualizar el changelog con `/quinotospec.update-changelog`.
2. Si el cambio creció más allá de 3 archivos o tocó DB/auth/API, detener y escalar a propuesta formal.
3. Reportar: archivos tocados, tests ejecutados, evidencia y riesgos residuales.

## Reglas

- No crear user stories ni archivos `*_tasks.md` para un track `simple`.
- No omitir tests ni `verify-before-done`, aunque el cambio sea pequeño.
- Si aparece una dependencia externa nueva o un cambio de contrato público, escalar a `complex`.
- La tech-spec debe vivir en `.quinoto-spec/quick-dev/` y no mezclarse con `proposals/`.
