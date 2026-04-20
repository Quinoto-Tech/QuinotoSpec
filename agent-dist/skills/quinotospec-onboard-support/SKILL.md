---
name: quinotospec-onboard-support
description: Especificaciones para generar el documento de onboarding orientado a equipos de soporte técnico, help desk o atención al cliente técnica. Foco en comportamiento observable del sistema, endpoints relevantes, servicios externos e identificación de puntos de falla comunes.
---

# Skill: Onboard Soporte

Aplica estas especificaciones al generar el documento de onboarding cuando el ROL seleccionado es **Soporte**.

## Audiencia

Personas de soporte técnico, help desk nivel 1/2, o atención al cliente técnica. Deben entender qué hace el sistema desde la perspectiva del usuario final, saber identificar dónde puede fallar, y conocer qué información recopilar ante un incidente. No necesariamente escriben código, pero pueden leer logs y manejar herramientas técnicas básicas.

## Tono y Estilo

- Claro y operacional. Orientado a "qué hacer cuando pasa X".
- Usar listas de verificación y tablas de decisión.
- Incluir ejemplos de mensajes de error comunes cuando se pueda inferir del codebase o discovery.
- Destacar con ⚠️ los puntos de falla más frecuentes o críticos.

## Secciones a Incluir y Nivel de Detalle

| Sección | Nivel | Instrucción |
|---|---|---|
| ¿Qué es este proyecto? | Alto | 4-5 oraciones. Describir desde la perspectiva del usuario final: qué puede hacer, qué espera recibir, qué no contempla el sistema. |
| Cómo levantar el proyecto | Omitir | No incluir. Reemplazar por nota: "El deployment lo gestiona el equipo de desarrollo/DevOps. Para consultas de entorno, escalar al equipo técnico." |
| Arquitectura del Sistema | Medio | Descripción funcional de los componentes como "cajas negras": qué reciben como entrada y qué producen como salida. Sin código. Incluir diagrama Mermaid si existe, con anotaciones en lenguaje operacional. |
| Endpoints Principales | Máximo | Tabla completa con método, ruta, descripción funcional, qué significa cada código de respuesta (200, 400, 401, 404, 500) para el usuario. |
| Modelos de Datos Clave | Medio | Solo los modelos que el equipo de soporte necesita para identificar registros del usuario (ej. User, Order, Session). Incluir los campos identificadores clave (ID, email, estado). |
| Estado Actual del Proyecto | Bajo | Solo mencionar si hay propuestas activas que puedan afectar comportamiento del sistema próximamente. |
| Acuerdos del Equipo (DoR/DoD) | Omitir | No relevante para soporte. |
| Actividad Reciente | Alto | Últimos 10 cambios del changelog — importante para correlacionar incidentes con deploys recientes. |
| Primeros Pasos Sugeridos | Alto | 6 pasos orientados a entender el sistema desde el lado del usuario y prepararse para atender tickets. |
| Recursos y Documentación | Medio | Solo los recursos útiles para soporte. |

## Sección Extra: Guía de Incidentes Comunes

Incluir siempre esta sección para soporte, generándola a partir de lo que se pueda inferir del codebase, endpoints y servicios externos detectados:

```markdown
## 🚨 Guía de Incidentes Comunes

### Cómo escalar un incidente

1. Recopilar: ID de usuario afectado, timestamp del error, mensaje de error exacto, endpoint o acción que ejecutaba.
2. Verificar el changelog reciente — ¿hubo un deploy en las últimas horas?
3. Si el error es 5xx → escalar a desarrollo inmediatamente con los datos recopilados.
4. Si el error es 4xx → verificar que el usuario tenga los permisos correctos / datos válidos.

### Servicios externos que pueden fallar

| Servicio | Propósito | Síntoma de falla | Acción |
|---|---|---|---|
| [servicio detectado en 05-data-and-services.md] | [qué hace] | [cómo se manifiesta] | [escalar a / verificar] |

### Variables de entorno críticas para producción

[Listar de 06-devops-ci-security.md las variables más críticas cuya ausencia causa fallas catastróficas. No incluir valores, solo nombres y consecuencia de su ausencia.]
```

## Primeros Pasos — Plantilla para Soporte

1. [ ] Leer la sección "¿Qué es este proyecto?" para entender qué puede y no puede hacer el sistema.
2. [ ] Familiarizarse con los endpoints principales y sus códigos de respuesta.
3. [ ] Identificar los servicios externos integrados (ver tabla en "Guía de Incidentes Comunes").
4. [ ] Revisar el changelog reciente para saber qué cambió recientemente en el sistema.
5. [ ] Solicitar acceso de solo lectura a los logs de producción al equipo de DevOps.
6. [ ] Generar un ticket de prueba y verificar que el flujo completo funcione correctamente.

## Lo que NO incluir

- Comandos de desarrollo o configuración local.
- Arquitectura interna detallada o patrones de diseño.
- Acuerdos del equipo de desarrollo (DoR/DoD).
- Detalles de implementación de modelos de datos más allá de los campos identificadores.
