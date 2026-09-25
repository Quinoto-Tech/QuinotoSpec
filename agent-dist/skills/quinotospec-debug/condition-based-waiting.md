# Condition-based waiting

## Principio

Espera una condición observable, no un tiempo arbitrario.

## Patrón

```text
while ! condición_observable:
  revisar estado
  esperar intervalo_controlado
  if timeout:
    fallar con contexto
```

## Aplicación

- Usa deadlines para que el timeout sea una decisión explícita.
- Lee el estado desde una fuente que represente el resultado.
- Evita polling aggressive que sature el proceso.
- Incluye el último estado observado en el error.
- Para concurrencia, usa locks, señales o barriers cuando el sistema los soporte.

## Comparación

| Enfoque | Riesgo |
|---|---|
| `sleep(100ms)` | Depende de la velocidad de la máquina. |
| Polling con deadline | Puede esperar demasiado si nunca ocurre. |
| Condición + timeout | Expone progreso y un fallo acotado. |

## Test

Inyecta el reloj o la dependencia de espera y prueba éxito, timeout y reintentos sin esperar realmente.
