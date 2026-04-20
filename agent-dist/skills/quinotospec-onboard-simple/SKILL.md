---
name: quinotospec-onboard-simple
description: Especificaciones para generar el documento de onboarding en lenguaje extremadamente simple, sin jerga técnica, con analogías cotidianas y paso a paso. Para personas que se incorporan a un equipo de tecnología sin background técnico previo.
---

# Skill: Onboard Simple

Aplica estas especificaciones al generar el documento de onboarding cuando el ROL seleccionado es **"Tengo un IQ muy bajo y necesito entender"**.

> **Nota interna**: Este modo no es despectivo — es el modo de máxima claridad. Está diseñado para personas completamente nuevas en el mundo del software que necesitan entender qué pasa en el proyecto sin sentirse perdidas. El objetivo es que cualquier persona, sin importar su background, pueda leer este documento y saber qué hace el sistema, por qué existe y cómo encaja en el equipo.

## Audiencia

Alguien que se incorpora a un equipo de tecnología sin background técnico previo. Puede ser un nuevo integrante de un área de negocio, un pasante, una persona en transición de carrera, o simplemente alguien que aprende mejor con explicaciones directas y analogías simples.

## Tono y Estilo

- **Frases cortas**. Máximo 15 palabras por oración.
- **Sin siglas sin explicar**. Si aparece "API", explicar: "una API es como un menú de restaurante — le decís qué querés y te trae el resultado".
- **Usar analogías del mundo real** para conceptos técnicos. Ver tabla de analogías más abajo.
- **Sin asumir conocimiento previo**. Explicar todo desde cero.
- **Usar emojis** para marcar secciones y puntos importantes — aportan contexto visual.
- **Cada sección debe empezar con una frase de por qué importa** antes de explicar el qué.
- **Evitar**: arquitectura, endpoint, deploy, stack, framework, pipeline, schema, payload, ORM, CRUD, git branch, merge, PR. Si son inevitable, explicarlos en el momento.

## Tabla de Analogías Obligatorias

Usar estas analogías cuando aparezcan los conceptos correspondientes:

| Concepto técnico | Analogía a usar |
|---|---|
| API / Endpoint | Menú de restaurante: pedís algo, te traen el resultado |
| Base de datos | Planilla de Excel gigante donde se guarda todo |
| Servidor | Una computadora que siempre está prendida y responde pedidos |
| Deploy / Despliegue | Como publicar una actualización en el teléfono |
| Branch (rama de git) | Un borrador del documento, separado de la versión oficial |
| Test / Prueba | Un chequeo automático que verifica que nada esté roto |
| Propuesta técnica | Un plan escrito de "qué vamos a construir y por qué" |
| Tarea / Task | Un ítem de la lista de quehaceres del equipo |
| Variable de entorno | Una contraseña o configuración secreta que el programa necesita para funcionar |
| Arquitectura | La forma en que están organizadas las piezas del sistema |

## Secciones a Incluir y Nivel de Detalle

| Sección | Nivel | Instrucción |
|---|---|---|
| ¿Qué es este proyecto? | Máximo | Explicar como si se lo contaras a alguien en un ascensor. Qué problema resuelve. Para quién. Con qué resultado. |
| Cómo levantar el proyecto | Solo si aplica | Si la persona necesita ejecutar algo, incluir los comandos con explicación de cada uno en lenguaje simple. Si no aplica, omitir. |
| Arquitectura del Sistema | Mínimo | Describir el sistema como partes de una máquina o edificio. "Hay tres partes principales: la que el usuario ve (como la fachada), la que procesa los pedidos (como la cocina), y la que guarda los datos (como el almacén)." |
| Endpoints Principales | Muy bajo | Solo mencionar las "acciones" más importantes que el sistema puede hacer, en lenguaje de usuario: "El sistema puede registrar usuarios, procesar pagos, enviar notificaciones." |
| Modelos de Datos Clave | Omitir | No incluir. Demasiado técnico para esta audiencia. |
| Estado Actual del Proyecto | Alto | Explicar qué se está construyendo ahora y qué ya está listo. En lenguaje de progreso, no técnico. |
| Acuerdos del Equipo (DoR/DoD) | Medio | Explicar en lenguaje simple: "El equipo tiene dos listas de chequeo. Una para saber cuándo algo está listo para empezar. Otra para saber cuándo algo está realmente terminado." |
| Actividad Reciente | Medio | Últimos 5 cambios, con descripción en lenguaje simple de qué cambió. |
| Primeros Pasos Sugeridos | Máximo | 5 pasos muy concretos, numerados, sin ambigüedad. Cada paso con una frase de "por qué esto importa". |
| Recursos y Documentación | Mínimo | Solo 3 recursos máximo, con explicación de para qué sirve cada uno. |

## Estructura del Documento

El documento debe comenzar con esta introducción antes de cualquier sección:

```markdown
# 👋 Bienvenido/a al equipo

> Este documento existe para que entiendas rápido qué hace este proyecto y cómo funciona el equipo.
> No necesitás saber programar para entenderlo. Está escrito en lenguaje simple, a propósito.
> Si algo no se entiende, eso es un problema del documento — no tuyo. Pedile al equipo que lo mejore.
```

## Primeros Pasos — Plantilla Simple

1. [ ] **Primero** — Leer este documento completo de principio a fin (sí, todo). Llevate una hora si hace falta.
2. [ ] **Segundo** — Pedile a alguien del equipo que te muestre el sistema funcionando en vivo. Ver es entender.
3. [ ] **Tercero** — Leer qué está construyendo el equipo ahora mismo. Está en `.quinoto-spec/proposals/`.
4. [ ] **Cuarto** — Preguntar sin miedo. En este equipo, las preguntas hacen el trabajo mejor.
5. [ ] **Quinto** — Encontrar tu primera contribución: algo pequeño que puedas hacer para entender cómo funciona el proceso.

## Lo que NUNCA incluir en este modo

- Comandos de terminal sin explicación.
- Diagramas técnicos complejos.
- Tablas con más de 4 columnas.
- Siglas sin definición.
- Más de 3 niveles de anidamiento en listas.
- Cualquier bloque de código que no sea absolutamente esencial.
