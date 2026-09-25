# Anti-patrones de testing

## Mock del comportamiento en vez de integración real

**Síntoma**: todos los tests pasan porque cada dependencia devuelve el valor esperado.

**Problema**: el mock no demuestra que el código real integra correctamente.

**Corrección**: usa el límite público, una fixture real o un contrato de integración para la prueba crítica. Mantén mocks solo en límites externos inevitables.

## Test que solo prueba al test

**Síntoma**: el test pasa aunque la función cambie o desaparezca.

**Problema**: se afirma una implementación interna sin comportamiento.

**Corrección**: prueba entradas, salidas y errores observables. Evita leer rutas privadas o estados internos.

## Exceso de mocks

**Síntoma**: el objeto bajo prueba queda rodeado de mocks con configuración extensa.

**Problema**: la prueba se acopla al grafo y falla por refactors irrelevantes.

**Corrección**: reduce el número de límites mockeados y prefiere datos reales pequeños.

## Tests interdependientes

**Síntoma**: un test necesita ejecutar otro test o depende del orden de la suite.

**Problema**: el resultado depende del estado compartido.

**Corrección**: crea fixtures y limpieza por test; no uses `only`, `skip` ni orden implícito.

## Tests lentos

**Síntoma**: la suite tarda minutos por esperar red, disco o procesos reales.

**Problema**: el equipo evita ejecutar la suite y los fallos llegan tarde.

**Corrección**: separa unit tests de integración, usa dependencias controladas y marca claramente el alcance de cada test.

## Tests flaky

**Síntoma**: el mismo commit falla y pasa sin cambios.

**Problema**: la señal y el orden externo contaminan el resultado.

**Corrección**: elimina la aleatoriedad no sembrada, espera condiciones reales y registra el comando que reproduce el fallo.

## Sobre-testing de implementación

**Síntoma**: cambiar un nombre privado rompe muchos tests.

**Problema**: el contrato público no está separado del detalle.

**Corrección**: prueba comportamiento, evita aserciones sobre llamadas internas y conserva un punto de separación mínimo cuando sea necesario.

## Test sin criterio de aceptación

**Síntoma**: el test afirma que “funciona” sin una condición concreta.

**Problema**: cualquier resultado puede justificarse después.

**Corrección**: escribe primero el criterio de aceptación y tradúcelo a una entrada, salida y error verificable.

## Checklist

- [ ] El test falla sin la implementación.
- [ ] El fallo corresponde al comportamiento requerido.
- [ ] La prueba no depende del orden.
- [ ] El tiempo y los recursos externos están controlados.
- [ ] El test sobrevive a un refactor interno.
- [ ] Existe evidencia del comando ejecutado.
