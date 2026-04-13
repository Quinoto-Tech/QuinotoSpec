```skill
---
name: Onboard — Producto / Negocio
description: Especificaciones para generar el documento de onboarding orientado a perfiles de producto, negocio o management. Foco en qué hace el sistema, por qué, para quién y en qué estado está el roadmap.
---

# Skill: Onboard Producto / Negocio

Aplica estas especificaciones al generar el documento de onboarding cuando el ROL seleccionado es **Producto/Negocio**.

## Audiencia

Product Managers, Product Owners, stakeholders de negocio, managers, analistas funcionales. No escriben código pero toman decisiones sobre qué construir, cuándo y por qué. Necesitan entender el estado del proyecto, los acuerdos del equipo y el roadmap sin necesidad de entender la implementación técnica.

## Tono y Estilo

- Lenguaje accesible, orientado a valor y resultados.
- Evitar acrónimos técnicos sin explicación. Si aparece uno, definirlo en una nota al pie o entre paréntesis.
- Usar analogías de negocio cuando sea útil.
- Priorizar tablas resumen sobre listas largas.
- Destacar con **negrita** los conceptos que impactan decisiones de producto.

## Secciones a Incluir y Nivel de Detalle

| Sección | Nivel | Instrucción |
|---|---|---|
| ¿Qué es este proyecto? | Máximo | 5-7 oraciones. Contexto de negocio, usuarios objetivo, propuesta de valor, métricas de éxito si existen. |
| Cómo levantar el proyecto | Omitir | No incluir. Reemplazar por: "Para consultas técnicas sobre el entorno, contactar al equipo de desarrollo." |
| Arquitectura del Sistema | Mínimo | Solo un párrafo en lenguaje de negocio describiendo las piezas principales como "módulos funcionales" (ej. "el módulo de pagos", "el servicio de notificaciones"). Sin código, sin diagramas técnicos. |
| Endpoints Principales | Omitir | No incluir. |
| Modelos de Datos Clave | Omitir | No incluir. |
| Estado Actual del Proyecto | Máximo | Tabla de propuestas activas con estado, prioridad y descripción de valor de negocio. Tabla de propuestas completadas (archivadas) como historial de lo entregado. |
| Acuerdos del Equipo (DoR/DoD) | Máximo | Este es el corazón del documento para este perfil. Explicar el DoR como "qué necesita estar listo para que el equipo pueda empezar a trabajar en algo" y el DoD como "qué condiciones deben cumplirse para considerar algo terminado". |
| Actividad Reciente | Alto | Últimos 10 registros del changelog en lenguaje de negocio (el generador debe traducir los títulos técnicos al impacto funcional cuando sea posible). |
| Primeros Pasos Sugeridos | Máximo | 6 pasos orientados a entender el contexto de producto y participar en el proceso. |
| Recursos y Documentación | Medio | Solo los recursos relevantes para producto: `07-product-and-agreements.md`, `PROJECT_STATUS.md`, propuestas activas. Omitir referencias técnicas. |

## Sección Extra: Roadmap y Valor Entregado

Incluir siempre esta sección para perfiles de producto, ubicada después de "Estado Actual del Proyecto":

```markdown
## 📦 Valor Entregado

[Leer el changelog completo y sumar el "Human Time" ahorrado de cada entrada. Presentar como:]

- **Total de tiempo ahorrado con IA**: [N horas] desde el inicio del proyecto.
- **Propuestas completadas**: [N] iniciativas entregadas.
- **Velocidad actual**: [N] tareas completadas en los últimos 30 días.

## 🗺️ Roadmap Visible

| Estado | Propuesta | Prioridad | Impacto Esperado |
|---|---|---|---|
| 🟢 En Curso | [nombre] | P1 | [descripción de valor] |
| 🟡 Planificada | [nombre] | P2 | [descripción de valor] |
| ✅ Completada | [nombre] | — | [descripción de valor] |
```

## Primeros Pasos — Plantilla para Producto/Negocio

1. [ ] Leer la visión del producto en `.quinoto-spec/discovery/07-product-and-agreements.md`.
2. [ ] Revisar las propuestas activas en `.quinoto-spec/proposals/` para entender qué está en construcción.
3. [ ] Ejecutar `@quinotospec.status` para ver el dashboard actualizado del estado del proyecto.
4. [ ] Leer el DoR y DoD del equipo — son los acuerdos que hacen que el trabajo fluya correctamente.
5. [ ] Identificar si hay propuestas en estado `🟡 Propuesta` que necesiten tu aprobación o input de negocio.
6. [ ] Agendar una reunión con el Tech Lead para repasar el roadmap y prioridades.

## Lo que NO incluir

- Comandos de terminal o configuración de entorno.
- Detalles de implementación técnica.
- Modelos de datos, endpoints o arquitectura de software.
- Referencias a skills o workflows del agente (salvo `@quinotospec.status` que es de lectura pura).
```
