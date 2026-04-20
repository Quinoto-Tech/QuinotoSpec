---
name: quinotospec-onboard-developer
description: Especificaciones para generar el documento de onboarding orientado a desarrolladores (frontend, backend o fullstack). Foco en setup técnico, arquitectura, código y flujo de trabajo.
---

# Skill: Onboard Desarrollador

Aplica estas especificaciones al generar el documento de onboarding cuando el ROL seleccionado es **Desarrollador**.

## Audiencia

Desarrolladores que van a escribir código en el proyecto. Puede ser frontend, backend o fullstack. Tienen experiencia técnica; no necesitan explicaciones de conceptos básicos de desarrollo, pero sí del contexto específico de este proyecto.

## Tono y Estilo

- Directo y técnico. Sin rodeos.
- Usar bloques de código para todo comando, snippet o ejemplo.
- Nombrar archivos con rutas relativas exactas.
- Preferir ejemplos reales del codebase sobre descripciones abstractas.

## Secciones a Incluir y Nivel de Detalle

| Sección | Nivel | Instrucción |
|---|---|---|
| ¿Qué es este proyecto? | Bajo | 2-3 oraciones. Solo el contexto mínimo necesario para entender la arquitectura. |
| Cómo levantar el proyecto | Máximo | Todos los comandos, variables de entorno con ejemplo de valores (no secretos reales), flags relevantes, cómo correr en modo debug, cómo correr un test específico. |
| Arquitectura del Sistema | Máximo | Descripción de cada capa con responsabilidades. Patrones de diseño usados. Tabla de componentes con rutas de archivos clave. Diagrama Mermaid obligatorio. Mencionar dónde está el entry point. |
| Endpoints Principales | Alto | Tabla con método, ruta, descripción, auth y ejemplo de request/response para los más importantes. |
| Modelos de Datos Clave | Alto | Hasta 5 modelos con todos sus campos, tipos y relaciones. Mencionar el ORM o cliente de BD usado. |
| Estado Actual del Proyecto | Medio | Tabla de propuestas activas + lista de tareas `[ ]` pendientes de mayor prioridad. |
| Acuerdos del Equipo (DoR/DoD) | Alto | Especialmente el DoD — es bloqueante para mergear. |
| Actividad Reciente | Bajo | Últimos 5 registros del changelog. |
| Primeros Pasos Sugeridos | Máximo | 7 pasos orientados a escribir código sin romper nada. |
| Recursos y Documentación | Alto | Tabla completa + agregar rutas de archivos de configuración clave (linter, tsconfig, etc. según stack). |

## Primeros Pasos — Plantilla para Desarrollador

Adaptar al contexto real, pero respetar este orden:

1. [ ] Clonar el repo y levantar el proyecto localmente (`[comando dev]`).
2. [ ] Correr la suite de tests completa y verificar que pasen (`[comando test]`).
3. [ ] Leer `03-architecture.md` para entender el mapa del código.
4. [ ] Leer los DoD en `08-product-and-agreements.md` — aplican a cada tarea que cierres.
5. [ ] Revisar la convención de branches: `feature/{{TASK_ID}}-descripcion-kebab-case`.
6. [ ] Leer la propuesta activa de mayor prioridad — te da el "por qué" detrás del código que vas a tocar.
7. [ ] Elegir una tarea `[ ]` pendiente de baja complejidad como primera contribución y ejecutar `@quinotospec.apply`.

## Sección Extra: Flujo de Trabajo del Equipo

Incluir siempre esta sección para desarrolladores:

```markdown
## ⚙️ Flujo de Trabajo

1. Elegir tarea → `@quinotospec.apply TASK_ID`
2. El agente crea el branch automáticamente: `feature/{{TASK_ID}}-descripcion`
3. Escribir código + tests
4. Verificar DoD antes de PR
5. Ejecutar `@quinotospec.pre-commit` (si está disponible) como check rápido
6. Crear PR y ejecutar `@quinotospec.review` para revisión asistida
7. Merge → `@quinotospec-mark-done` cierra la tarea automáticamente
```

## Lo que NO incluir

- Visión de producto o roadmap de negocio (no es relevante para el día 1).
- Detalle de CI/CD más allá de cómo correr tests localmente.
- Información de soporte o tickets.
