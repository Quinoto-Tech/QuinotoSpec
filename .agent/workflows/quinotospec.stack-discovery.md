---
description: Generar documentación de descubrimiento del stack consolidado para proyectos distribuidos en múltiples sub-carpetas
---

Este workflow consolida los discoveries de múltiples sub-proyectos en un único `.quinoto-spec/discovery/`.

**Precondición OBLIGATORIA**: Dentro de todas las carpetas del root debe existir `*/.quinoto-spec/discovery/`. De no ser así, **detener el proceso** y listar qué carpetas no tienen discovery para que el usuario ejecute `quinotospec.discovery` en cada una.

---

## Paso 0 — Inventario de servicios

Antes de comenzar, escanea el root y lista todas las carpetas que contienen `/.quinoto-spec/discovery`. Para cada una, lee el campo `**Discovery Date:**` en su `00-stack-profile.md`. Genera el inventario:

| Servicio | Ruta | Stack Principal | Discovery Date | Estado |
| --- | --- | --- | --- | --- |
| [nombre] | [ruta relativa] | [lenguaje/framework] | [YYYY-MM-DD] | ✅ Fresco / ⚠️ Viejo |

Marcar como **⚠️ Viejo** si el `Discovery Date` tiene más de **30 días** de antigüedad (o si el campo no existe).

**Si hay servicios con discovery ⚠️ Viejo:**
- Notificar al usuario: *"Los siguientes servicios tienen un discovery desactualizado: [lista]. Se recomienda ejecutar `@quinotospec.refresh-discovery` para cada uno antes de consolidar."*
- Esperar confirmación del usuario:
  - **Opción A — Refrescar primero (recomendado)**: Para cada servicio viejo, ejecutar el workflow `quinotospec.refresh-discovery` pasando el `SERVICE_PATH` correspondiente. Continuar con la consolidación una vez que todos estén frescos.
  - **Opción B — Consolidar de todas formas**: Continuar con los datos actuales y documentar en `01-overview.md` qué servicios tienen discovery potencialmente desactualizado.

Este inventario queda documentado al inicio de los archivos consolidados y en el changelog.

---

## Generación de archivos consolidados

Explora el proyecto completo y genera 7 archivos Markdown independientes en `.quinoto-spec/discovery/` con los siguientes nombres EXACTOS:
- 00-stack-profile.md
- 01-overview.md
- 02-architecture.md
- 03-endpoints-and-openapi.md
- 04-data-and-services.md
- 05-devops-ci-security.md
- 06-findings-and-recommendations.md
- 07-product-and-agreements.md

**Instrucciones generales (aplican a todos los archivos):**
- Escribir en español, formato claro y profesional.
- Cada archivo debe comenzar con un título H1 y listar los servicios consolidados.
- Usar subsecciones (H2/H3) para organizar hallazgos: Resumen, Detalle, Recomendaciones.
- Incluir listado de carpetas de los proyectos en el root general.
- **Generar siempre diagramas de secuencia en Mermaid** (`sequenceDiagram`) para los flujos principales entre servicios. Para diagramas que no se puedan inferir con certeza, usar placeholder indicando qué debe contener.
- Generar contenido accionable y conciso: checklists, comandos sugeridos, y prioridades (alta/media/baja).

---

### 0) 00-stack-profile.md
- Lee todos los `*/.quinoto-spec/discovery/00-stack-profile.md`.
- Genera una **tabla comparativa de stacks** por servicio:

| Servicio | Lenguaje | Framework | Versión | Package Manager | Test Runner |
| --- | --- | --- | --- | --- | --- |

- Detecta y documenta **inconsistencias**: versiones distintas del mismo lenguaje, herramientas incompatibles, falta de estandarización entre servicios.
- **Auto-estandarización**: Si se detectan 2 o más inconsistencias de stack entre servicios, notifica al usuario y sugiere ejecutar `@quinotospec.create-proposal` con la descripción: *"Stack Standardization — [detalle de inconsistencia]"* para generar automáticamente una propuesta de estandarización.

### 1) 01-overview.md
- Lee todos los `*/.quinoto-spec/discovery/01-overview.md`.
- Resumen ejecutivo del sistema distribuido: qué hace cada servicio, su rol y cómo se relacionan.
- Lista rápida de riesgos y puntos críticos identificados a nivel global.

### 2) 02-architecture.md
- Lee todos los `*/.quinoto-spec/discovery/02-architecture.md`.
- **Diagrama de secuencia consolidado** (`sequenceDiagram`) mostrando cómo se comunican TODOS los servicios entre sí, incluyendo cualquier tipo de persistencia. **No incluir servicios externos en este diagrama.**
- Sección separada de **Servicios Externos** (los que no figuran en el root pero están referenciados en los archivos de architecture de los sub-proyectos).
- Ampliar y unificar los diagramas de secuencia existentes en los archivos individuales.
- Componentes reutilizables e integraciones internas cross-servicio.

### 3) 03-endpoints-and-openapi.md
- Lee todos los `*/.quinoto-spec/discovery/03-endpoints-and-openapi.md`.
- Consolidar todos los endpoints por servicio.
- **Detectar solapamientos**: rutas iguales expuestas por más de un servicio con contratos distintos.
- Lista rápida de riesgos (endpoints sin autenticación, rutas duplicadas, inconsistencias de contrato).

### 4) 04-data-and-services.md
- Lee todos los `*/.quinoto-spec/discovery/04-data-and-services.md`.
- Consolidar modelos de datos y servicios externos por sub-proyecto.
- **Detectar duplicación de datos**: entidades similares o con el mismo nombre en distintos servicios.
- Lista rápida de riesgos y puntos críticos identificados.

### 5) 05-devops-ci-security.md
- Lee todos los `*/.quinoto-spec/discovery/05-devops-ci-security.md`.
- Consolidar configuraciones de CI/CD y prácticas de seguridad.
- **Verificar consistencia entre servicios**: ¿Todos usan el mismo pipeline? ¿Las prácticas de gestión de secretos son uniformes?
- Lista rápida de vulnerabilidades detectadas y prioridades de remediación cross-servicio.

### 6) 06-findings-and-recommendations.md
- Lee todos los `*/.quinoto-spec/discovery/06-findings-and-recommendations.md`.
- Consolidar todos los hallazgos individuales.
- **Agregar una sección de inconsistencias cross-servicios** detectadas en los pasos anteriores (stack, endpoints, datos, seguridad).
- Lista priorizada de recomendaciones con owner sugerido por servicio.

### 7) 07-product-and-agreements.md
- Lee todos los `*/.quinoto-spec/discovery/07-product-and-agreements.md`.
- Consolidar la visión de producto global: objetivos comunes, KPIs compartidos y acuerdos transversales.

---

## Paso Final — Dependency Graph

Una vez generados los 7 archivos, ejecuta el workflow `quinotospec.dependency-graph` para generar `.quinoto-spec/discovery/00-dependency-graph.md` con el mapa de dependencias inter-servicio y la detección de contract drift.

---

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la generación de archivos, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Stack Discovery Consolidated
- **Resumen**: Se consolidó el discovery de N servicios ([lista de nombres]) en `.quinoto-spec/discovery/`.
