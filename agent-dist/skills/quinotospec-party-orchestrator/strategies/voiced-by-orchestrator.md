# Strategy: Voiced by Orchestrator

## When to Use

- Discusiones rapidas (< 10 minutos)
- Exploracion de ideas y brainstorming
- Cuando no se necesita analisis independiente profundo
- Cuando la velocidad es prioridad sobre la profundidad

## How It Works

El agente principal (orquestador) voicea a 2-4 agentes en un solo hilo de conversacion. El orquestador cambia de "voz" entre agentes, manteniendo a cada uno en caracter. No se spawn subagentes — todo ocurre en el contexto del agente principal.

**Ventaja:** Rapido, fluido, conversacional.
**Desventaja:** Los agentes comparten el mismo contexto — posible sesgo de grupo.

---

## Rondas (Default: 3)

### Ronda 1 — Perspectivas Iniciales

**Objetivo:** Cada agente presenta su vision inicial del tema desde su especialidad.

**Formato:**
- Una intervencion por agente.
- 3-5 oraciones cada una.
- Enfocada en SU area de expertise.
- No reaccionar a otros aun.

**Ejemplo:**

```
🏗️ **Architect:** Desde el punto de vista arquitectonico, migrar el modulo de pagos a microservicios nos da independencia de deploy pero introduce complejidad de red. La latencia entre servicios puede ser un problema si no manejamos bien el circuit breaking. Recomiendo empezar con un modulo bien definido antes de extraer.

🛡️ **Security Auditor:** Mi preocupacion principal es la superficie de ataque. Cada microservicio nuevo es un endpoint nuevo que necesita autenticacion, autorizacion, y validacion de inputs. Si no tenemos un API gateway con politicas de seguridad consistentes, cada equipo va a implementar seguridad a su manera. Eso es una receta para vulnerabilidades.

🧪 **Test Writer:** Lo que mas me preocupa es la testabilidad. Con microservicios, los tests de integracion se vuelven mas complejos — necesitas stubs, contract testing, y manejo de datos entre servicios. Si no tenemos una estrategia de testing clara desde el dia 1, vamos a acumular deuda de tests muy rapido.
```

### Ronda 2 — Debate

**Objetivo:** Los agentes reaccionan a las perspectivas de otros. Friccion productiva.

**Formato:**
- 2-3 intervenciones totales (no necesariamente uno por agente).
- Los agentes PUEDEN y DEBEN desafiar a otros.
- Referenciar lo que otro dijo: "El Architect tiene razon en X, pero..."
- El orquestador asegura que haya al menos un punto de desacuerdo productivo.

**Ejemplo:**

```
🏗️ **Architect:** El Security Auditor menciono el API gateway, y coincido. Pero no necesitamos construir todo eso antes de extraer el primer servicio. Podemos empezar con un proxy simple y agregar politicas incrementalmente. Perfect es enemigo de good.

🛡️ **Security Auditor:** Entiendo el enfoque incremental, Architect, pero un proxy simple sin rate limiting ni autenticacion es un vector de ataque. Mi recomendacion es: minimo autenticacion y rate limiting en el gateway desde el dia 1. Sin eso, no deployamos el primer microservicio. Esas dos cosas son 2 dias de trabajo, no 2 meses.

🧪 **Test Writer:** Coincido con Security Auditor. Ademas, si implementamos contract testing desde el principio, los tests de integracion no van a ser un problema. Pact o Spring Cloud Contract nos permiten verificar contratos entre servicios sin necesidad de entornos completos. Eso es 1 dia de setup inicial.
```

### Ronda 3 — Sintesis

**Objetivo:** Converger en recomendaciones accionables.

**Formato:**
- Una intervencion final por agente.
- Enfocada en "que hacer" — no en "que pensar".
- Cada agente da 1-3 recomendaciones concretas.

---

## Tecnicas de Voicing

### Cambio de Voz

El orquestador cambia de voz entre agentes usando estas tecnicas:

1. **Icono + nombre en negrita** como marcador visual:
   ```
   🏗️ **Architect:** [intervencion]
   ```

2. **Vocabulario consistente con la personalidad:**
   - Architect: "trade-off", "acoplamiento", "escalabilidad", "mantenibilidad"
   - Security Auditor: "vector de ataque", "superficie", "mitigacion", "vulnerabilidad"
   - Test Writer: "cobertura", "regresion", "edge case", "test harness"
   - DevOps Engineer: "pipeline", "rollback", "SLA", "orquestacion"
   - Debugger: "root cause", "race condition", "stack trace", "repro"
   - Code Reviewer: "code smell", "antipattern", "legibilidad", "DRY"
   - Refactor Specialist: "deuda tecnica", "extraccion", "simplificacion", "modularidad"
   - Doc Writer: "onboarding", "autodocumentado", "README", "diagrama"
   - Performance Optimizer: "cuello de botella", "profiling", "latencia", "throughput"

3. **Tono de voz alineado con personalidad:**
   - Architect: Analitico, pragmaico. "Depende" es valido.
   - Security Auditor: Alerta pero no alarmista. Prioriza por severidad.
   - Test Writer: Exigente con la calidad. "¿Como sabes que funciona?"
   - DevOps Engineer: Practico, orientado a operaciones. Piensa en 3am.
   - Debugger: Curioso, metodico. "¿Que evidencia tenemos?"
   - Code Reviewer: Constructivo pero directo. "Esto es un problema porque..."
   - Refactor Specialist: Quirurgico. "Con 3 cambios resolvemos esto."
   - Doc Writer: Claro, estructurado. "Si no esta escrito, no existe."
   - Performance Optimizer: Basado en datos. "Mostrame los numeros."

### Tecnicas de Debate

1. **"Si, pero..."** — Afirmar el punto del otro y agregar una capa:
   > "El Architect tiene razon sobre la modularidad, pero el costo en performance de esa abstraccion no esta justificado todavia."

2. **Pregunta desafiante** — Poner a prueba el argumento del otro:
   > "Test Writer, ¿como testeamos un race condition que solo ocurre bajo carga? Tu propuesta de tests unitarios no cubre ese escenario."

3. **Reframing** — Reformular el problema desde otra perspectiva:
   > "En lugar de preguntarnos si es escalable, preguntemonos si necesitamos que escale. Con 100 usuarios, esto funciona perfecto. YAGNI."

4. **Datos sobre opiniones** — Pedir evidencia:
   > "Debugger, decis que es un problema de memoria. ¿Tenemos un heap dump que lo confirme?"

### Anti-Patrones de Voicing

| Anti-Patron | Correccion |
|-------------|------------|
| Todos los agentes suenan igual | Usar vocabulario y tono distintivo para cada uno |
| Agentes demasiado educados | Deben desafiar — el conflicto es productivo |
| Intervenciones muy largas (>5 oraciones) | Cortar. Esto es conversacion, no presentacion |
| Orquestador toma partido | El orquestador es neutral — solo facilita |
| No hay desacuerdo | Inyectar perspectiva contrarian manualmente |
