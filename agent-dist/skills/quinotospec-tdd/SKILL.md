---
name: quinotospec-tdd
description: Usar antes de escribir código de producción para aplicar TDD con ciclo RED-GREEN-REFACTOR y evidencia verificable.
---

# Skill: QuinotoSpec TDD

## Iron Law

**No escribas código de producción sin observar primero un test mínimo que falle por la razón esperada.**

Una tarea de documentación, configuración o migración puede omitir TDD solo cuando el cambio no altera comportamiento ejecutable. En ese caso registra la justificación y usa una verificación apropiada.

## RED-GREEN-REFACTOR

1. **RED**: escribe un test mínimo para el comportamiento requerido y ejecútalo. Guarda comando, salida y motivo del fallo.
2. **GREEN**: implementa solo lo necesario para que el test pase. No agregues capacidades futuras.
3. **REFACTOR**: mejora nombres, estructura y duplicación sin cambiar comportamiento. Ejecuta nuevamente los tests afectados.
4. Ejecuta la suite relevante y registra el resultado.

## Evidencia mínima

```text
Test: <ruta:test>
Comando: <comando>
Resultado RED: falló porque <razón esperada>
Comando GREEN: <comando>
Resultado GREEN: pasó
Suite: <comando y resultado>
```

Un test que falla por una importación rota, una configuración inválida o un error del entorno no cuenta como RED válido. Corrige el andamiaje y vuelve a observar el fallo funcional.

## Registro verificable

Guarda un registro JSON en `.quinoto-spec/evidence/{{TASK_ID}}/tdd.json` con `schema_version`, `task_id`, `recorded_at`, `expected_failure`, `observed_failure` y los bloques `red`, `green` y `suite`. Cada bloque incluye `command`, `status`, `exit_code` y `output`.

```bash
python3 -B agent-dist/skills/quinotospec-rules-enforce/evidence_validate.py validate \
  --root . --kind tdd --task-id {{TASK_ID}} --require --json
```

El validador comprueba estructura, tipos, exit codes y frescura; no ejecuta el comando por ti. Un registro stale o un RED con exit code `0` bloquea.

## Matriz de aplicación

| Cambio | TDD | Evidencia mínima |
|---|---:|---|
| Lógica de producción | Obligatorio | Test falla antes y pasa después |
| API o integración | Obligatorio | Test de contrato o regresión |
| Bug | Obligatorio | Test de regresión que reproduce el bug |
| Documentación | Opcional | Revisión de links, sintaxis y renderizado |
| Configuración | Condicional | Test de configuración o validación determinista |
| Migración | Obligatorio | Test de migración y datos preservados |

## Racionalizaciones

| Racionalización | Por qué es inválida |
|---|---|
| “El cambio es trivial” | Los bugs triviales también necesitan regresión. |
| “Ya conozco el código” | El test documenta el comportamiento y descubre supuestos. |
| “Es difícil probar eso” | Reduce el alcance o usa un test en el límite correcto. |
| “El test lo haré después” | Sin RED no hay prueba de que el test guíe la implementación. |
| “La suite completa tarda” | Ejecuta primero el test focalizado y la suite completa al final. |
| “El fallo no es del cambio” | Reproduce el fallo y demuestra la línea base. |
| “El mock representa todo” | Un mock no demuestra integración; usa límites reales donde sea posible. |
| “La documentación no necesita test” | Valida enlaces, ejemplos y comandos ejecutables. |
| “El código funciona en mi máquina” | La evidencia debe repetir el resultado en el entorno del proyecto. |
| “Después haré el refactor” | Refactoriza con la suite en verde, no como deuda oculta. |
| “El error está en el test” | Investiga la causa antes de cambiar la expectativa. |
| “Una prueba manual basta” | Las regresiones futuras necesitan una prueba automática repetible. |

## Red Flags

1. Implementar antes de crear el test.
2. No conservar la salida RED.
3. Hacer que el test pase sin tocar producción.
4. Usar `skip`, `xfail` o mocks para ocultar el fallo.
5. Cambiar expectativas para acomodar una implementación incorrecta.
6. Ejecutar solo la suite completa sin focalizar el riesgo.
7. No detectar el test runner del proyecto.
8. Afirmar cobertura sin comando y resultado.
9. Probar una implementación existente en vez de comportamiento.
10. Mezclar refactor amplio con el fix.
11. Ignorar errores de entorno y llamarlos regresión.
12. Marcar la tarea completada sin evidencia fresca.

## Checklist de verificación

- [ ] El test describe comportamiento observable.
- [ ] El RED falla por la razón esperada.
- [ ] La implementación mínima hace pasar el test.
- [ ] No se introdujeron cambios fuera del alcance.
- [ ] Los tests focalizados pasan.
- [ ] La suite relevante pasa.
- [ ] El refactor conserva el comportamiento.
- [ ] La evidencia quedó registrada para revisión.

## Cuando no sabes cómo testear

1. Reduce el caso al límite más pequeño: entrada, transformación y salida.
2. Separa el comportamiento que falla de la infraestructura necesaria para ejecutarlo.
3. Prueba primero el límite público más cercano.
4. Si el problema es concurrencia, tiempo o proceso, usa un fake con control explícito.
5. Si no existe un límite testeable, pausa y propón el cambio de diseño necesario.

## Integración con debugging

Cuando una prueba falle después de varios intentos, cambia a `quinotospec-debug`. No apliques un parche intuitivo: registra hipótesis, experimentos y causa raíz antes de modificar producción.

## Referencias

- `testing-anti-patterns.md`
- `examples/tdd-typescript.md`
- `examples/tdd-python.md`
- `examples/tdd-rust.md`
