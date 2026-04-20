```skill
---
name: Onboard — General
description: Especificaciones para generar el documento de onboarding en modo General. Audiencia mixta, cobertura equilibrada de todas las áreas del proyecto.
---

# Skill: Onboard General

Aplica estas especificaciones al generar el documento de onboarding cuando el ROL seleccionado es **General**.

## Audiencia

Cualquier persona que necesite una visión completa del proyecto sin un foco técnico o de negocio específico. Puede ser un nuevo integrante que aún no tiene rol definido, un stakeholder externo, o alguien revisando el proyecto por primera vez.

## Tono y Estilo

- Lenguaje claro y profesional, sin jerga excesiva.
- Cuando se use un término técnico, definirlo brevemente la primera vez que aparece.
- Oraciones cortas. Párrafos de máximo 4 líneas.
- Usar listas y tablas siempre que sea posible en lugar de texto continuo.

## Secciones a Incluir y Nivel de Detalle

| Sección | Nivel | Instrucción |
|---|---|---|
| ¿Qué es este proyecto? | Alto | 4-6 oraciones. Incluir para quién existe y qué problema resuelve. |
| Cómo levantar el proyecto | Medio | Comandos básicos, pre-requisitos y variables de entorno. Sin profundizar en flags avanzados. |
| Arquitectura del Sistema | Medio | Descripción de capas en 2-3 párrafos + tabla de componentes. Incluir diagrama Mermaid si existe. Omitir detalles de implementación interna. |
| Endpoints Principales | Bajo | Máximo 8 endpoints. Solo ruta, método y descripción de una línea. Omitir payloads detallados. |
| Modelos de Datos Clave | Bajo | Máximo 3 modelos, solo campos más importantes. |
| Estado Actual del Proyecto | Alto | Tabla completa de propuestas activas con estado, prioridad y progreso. |
| Acuerdos del Equipo (DoR/DoD) | Medio | Incluir completo si existe. Si no existe, solo advertencia. |
| Actividad Reciente | Medio | Últimos 7 registros del changelog. |
| Primeros Pasos Sugeridos | Alto | 6 pasos balanceados: 2 técnicos, 2 de contexto de negocio, 2 de proceso del equipo. |
| Recursos y Documentación | Alto | Incluir tabla completa. |

## Primeros Pasos — Plantilla para ROL General

Generar esta lista adaptada al contexto real del proyecto:

1. [ ] Levantar el proyecto localmente y correr los tests.
2. [ ] Leer el `README.md` y la visión del producto en `08-product-and-agreements.md`.
3. [ ] Revisar el dashboard del proyecto con `@quinotospec.status`.
4. [ ] Leer la propuesta activa de mayor prioridad en `.quinoto-spec/proposals/`.
5. [ ] Conocer los acuerdos del equipo (DoR/DoD).
6. [ ] Identificar a quién consultar por área revisando los `Servicios Afectados` de cada propuesta.

## Lo que NO incluir

- Detalle de implementación de endpoints (payloads, esquemas completos).
- Scripts de migración o seeds.
- Configuración avanzada de CI/CD.
- Detalles de vulnerabilidades de seguridad.
```
