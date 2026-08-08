---
description: Resolver bugs y fixes menores sin necesidad de propuesta formal — rápido, documentado, con tests.
---

# Workflow: Fix

[INSTRUCCIÓN MAESTRA]
Debes corregir el bug o implementar el fix menor descrito por el usuario, documentar los cambios y ejecutar los tests correspondientes. Este workflow está pensado para bugs y fixes que no requieren una propuesta técnica formal.

**Parámetros:**

| Parámetro | Requerido | Descripción |
|-----------|-----------|-------------|
| Descripción del bug/fix | Sí | Qué problema hay y qué comportamiento se espera |
| `--task` `TASK_ID` | No | Si el fix pertenece a una tarea existente en una propuesta |
| `--skip-tests` | No | Omitir ejecución de tests (solo para cambios triviales) |

**Invocación:**

```bash
@quinotospec.fix "El botón de logout no cierra la sesión correctamente"
@quinotospec.fix "Corregir validación de email en el formulario de registro"
@quinotospec.fix --task TSK-AUTH-003 "Agregar manejo de error en el catch block"
@quinotospec.fix --skip-tests "Corregir typo en mensaje de bienvenida"
```

---

## Paso 0 — Análisis del Bug

1. Leer la descripción del bug/fix proporcionada por el usuario.
2. Si se pasó `--task TASK_ID`:
   - Buscar la tarea en `.quinoto-spec/proposals/{PROPOSAL_SLUG}/{US_ID}_tasks.md`
   - Leer el contexto técnico, criterios de aceptación y detalles de implementación
   - El fix debe alinearse con lo definido en la tarea
3. Si NO se pasó `--task`:
   - Es un fix independiente. Crear contexto en `.quinoto-spec/fixes/YYYYMMDD-hhmm-{slug}.md`
   - El archivo de contexto debe contener:
     ```markdown
     # Fix: {slug}
     - **Fecha**: YYYY-MM-DD HH:MM
     - **Descripción**: {descripción del bug}
     - **Comportamiento esperado**: {qué debería pasar}
     - **Comportamiento actual**: {qué pasa ahora}
     - **Stack detectado**: {lenguaje, framework, test runner}
     ```

4. Leer `.quinoto-spec/discovery/01-stack-profile.md` (si existe) para conocer el stack, comandos de test y convenciones.
5. Identificar los archivos involucrados en el bug.
6. **Presentar análisis al usuario antes de tocar código** (BLOQUEANTE):
   - Archivos que se modificarán
   - Causa raíz identificada
   - Solución propuesta (1-2 líneas)
   - Riesgo del cambio (BAJO / MEDIO / ALTO)
   - Preguntar: *"¿Procedo con el fix?"*

---

## Paso 1 — Implementación del Fix

1. Realizar los cambios mínimos necesarios para corregir el bug.
2. Principio de mínima intervención: cambiar solo lo necesario. No aprovechar para refactorizar código no relacionado.
3. Si el cambio es >20 líneas o afecta múltiples archivos, preguntar al usuario si prefiere crear una propuesta formal en su lugar.
4. Mantener consistencia con el estilo y convenciones del código existente.

---

## Paso 2 — Verificación de Tests

> Omitir si `--skip-tests`.

1. Ejecutar el comando de tests del stack detectado:
   - `npm test`, `pytest`, `bundle exec rspec`, `go test ./...`, `cargo test`
2. Si hay tests existentes para los archivos modificados, ejecutarlos específicamente:
   - `npm test -- --testPathPattern=archivo`
   - `pytest tests/test_archivo.py`
3. Si los tests fallan:
   - Verificar que el fallo no sea por el fix mismo (regresión)
   - Corregir hasta que los tests pasen
   - Máximo 2 intentos de corrección automática

---

## Paso 3 — Rollback si Persisten Fallos

Si después de 2 intentos los tests siguen fallando:

1. Ejecutar skill `quinotospec-rollback` para revertir cambios automáticamente.
2. Reportar al usuario el error persistente y sugerir:
   - "El fix puede requerir una propuesta formal más amplia. Usar @quinotospec.create-proposal."
3. NO documentar en changelog (no hubo cambios efectivos).

---

## Paso 4 — Documentación (Changelog)

Una vez aplicado el fix y pasados los tests, ejecutar la skill `quinotospec-update-changelog`:

- **Título**: Fix: {descripción breve del bug corregido}
- **Resumen**:
  - Archivos modificados con formato: `ruta/archivo` — [modificado] — motivo del cambio
  - Causa raíz identificada
  - Solución aplicada (1-2 líneas)
  - Estado de tests: ✅ pasaron / ⚠️ skip-tests

---

## Paso 5 — Mark Done (solo si `--task`)

Si el fix está asociado a una tarea existente (`--task TASK_ID`):

1. Ejecutar skill `quinotospec-mark-done` con el `TASK_ID` correspondiente.
2. Esto actualizará el estado de la tarea, historia y propuesta asociada.

Si el fix es independiente, omitir este paso.

---

## Paso 6 — Limpieza

1. Si se creó un archivo de contexto en `.quinoto-spec/fixes/`, dejarlo como registro histórico.
2. Si el fix fue trivial (typo, formato) y `--skip-tests`, el archivo de contexto es opcional.


