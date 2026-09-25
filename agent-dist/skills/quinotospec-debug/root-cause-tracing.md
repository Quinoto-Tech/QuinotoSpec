# Root-cause tracing

## Flujo

1. Dibuja el camino desde la entrada hasta el síntoma.
2. Marca el primer punto donde el valor, estado o control se desvía.
3. Traza hacia atrás quién introduce el valor incorrecto.
4. Sigue la llamada hasta el límite que puede corregirlo.
5. Corrige ese límite y observa si el síntoma desaparece sin parches posteriores.

## Preguntas

- ¿Qué valor debería existir y cuál existe?
- ¿Quién lo transforma por última vez correctamente?
- ¿Qué estado compartido cambió antes del fallo?
- ¿La primera desviación está antes del stack trace?
- ¿El error depende de orden, tiempo, proceso o datos externos?

## Evidencia

| Punto | Valor esperado | Valor observado | Fuente |
|---|---|---|---|
| Entrada | | | |
| Primer límite incorrecto | | | |
| Causa raíz | | | |
| Síntoma | | | |

No corrijas el primer stack frame que aparece si solo muestra dónde se dispara el síntoma.
