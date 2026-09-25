---
name: quinotospec-debug
description: Usar cuando una prueba, ejecución o regresión falla para reproducir, localizar la causa raíz y corregir con evidencia.
---

# Skill: QuinotoSpec Debug

## Iron Law

**No apliques un parche hasta tener una hipótesis reproducible y evidencia que identifique la causa raíz.**

Un hotfix sin causa raíz puede ocultar el defecto, mover el fallo o crear una segunda regresión.

## Método de cuatro fases

### 1. Reproducir

- Captura el comando exacto, entrada, entorno y salida.
- Reduce el caso a un test o fixture mínimo.
- Confirma la línea base y la frecuencia del fallo.
- Si no puedes reproducirlo, no cambies producción todavía.

### 2. Localizar

- Traza la entrada desde el límite público hasta el primer valor incorrecto.
- Revisa logs, trazas de pila, límites, estado compartido y llamadas externas.
- Separa el síntoma del punto donde se origina.
- Usa `root-cause-tracing.md` cuando el flujo cruce varios módulos.

### 3. Formular y probar hipótesis

Escribe una hipótesis falsable:

```text
Si <condición> es la causa, entonces <observación> cambiará al <experimento>.
```

- Cambia una variable por experimento.
- Registra resultado, expectativa y conclusión.
- No mezcles varios cambios en un experimento.
- Tras tres hipótesis fallidas, detén los parches locales y pregunta si la arquitectura o el contrato es incorrecto.

### 4. Corregir y verificar

1. Escribe o ajusta un test que falle por la causa raíz.
2. Implementa la corrección mínima en la capa responsable.
3. Ejecuta el test focalizado, la suite afectada y los comandos de calidad.
4. Añade defensa en profundidad solo si el límite necesita protección.
5. Registra causa raíz, corrección y evidencia.

## Registro verificable

Guarda un registro JSON en `.quinoto-spec/evidence/{{TASK_ID}}/debug.json` con `schema_version`, `task_id`, `recorded_at`, `reproduction`, `hypothesis`, `experiment`, `root_cause` y `regression`. Los bloques de ejecución incluyen `command`, `status`, `exit_code` y `output`; la regresión debe terminar en `passed`.

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py validate \
  --root . --kind debug --task-id {{TASK_ID}} --require --json
```

El validador comprueba estructura y frescura; no demuestra por sí solo que el comando haya sido ejecutado. Un hotfix sin causa raíz o regresión queda bloqueado.

## Racionalizaciones

| Racionalización | Corrección |
|---|---|
| “El error es obvio” | Reproduce y muestra la evidencia. |
| “Cambiaré esta línea y pruebo” | Formula una hipótesis antes del cambio. |
| “El test intermitente no cuenta” | Investiga estado, orden y sincronización. |
| “Es un problema del entorno” | Aísla el entorno y prueba la línea base. |
| “El warning es la causa” | Distingue warning, síntoma y causa raíz. |
| “Patch rápido y sigo” | El fix rápido puede retirar el guard y ocultar el defecto. |
| “Después agrego el test” | El test de regresión precede al fix. |
| “Tres intentos no son Architectural” | Tres hipótesis fallidas activan revisión de arquitectura. |

## Red Flags

1. Cambiar código sin reproducir el fallo.
2. Aplicar retries o sleep sin explicar la causa.
3. Silenciar el test o el log que molesta.
4. Modificar varias capas en el mismo intento.
5. Declarar causa raíz a partir de una suposición.
6. Borrar el test que falla.
7. Ignorar una intermitencia.
8. Corregir el síntoma en la UI sin seguir el flujo.
9. Prometer que el fallo no puede repetirse sin datos.
10. Dejar el workaround sin test de regresión.
11. Reportar éxito solo porque el mensaje de error desapareció.

## Cuando no sabes qué probar

- Reduce entradas y dependencias hasta que el fallo sea determinista.
- Compara una ejecución que falla con una que pasa.
- Usa `defense-in-depth.md` para decidir dónde colocar validaciones.
- Usa `condition-based-waiting.md` para procesos, colas y concurrencia.
- Si el fallo desaparece al repetir, no lo declares resuelto: mide frecuencia y estado.

## Integración con TDD

El bug comienza con RED: un test de regresión que falla por el defecto. Si el RED no es posible, documenta por qué y define la evidencia mínima antes del fix.

## Referencias

- `root-cause-tracing.md`
- `defense-in-depth.md`
- `condition-based-waiting.md`
