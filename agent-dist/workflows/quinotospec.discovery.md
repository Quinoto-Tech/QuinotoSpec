---
description: Generar documentación de descubrimiento del proyecto en .quinoto-spec/discovery
---

Explora el proyecto completo y genera 7 archivos Markdown independientes dentro de .quinoto-spec/discovery con los siguientes nombres EXACTOS:
- 00-stack-profile.md
- 01-overview.md
- 02-architecture.md
- 03-endpoints-and-openapi.md
- 04-data-and-services.md
- 05-devops-ci-security.md
- 06-findings-and-recommendations.md
- 07-product-and-agreements.md

Instrucciones generales (aplican a todos los archivos):
- Escribir en español, formato claro y profesional.
- Cada archivo debe comenzar con un título H1, una breve descripción y una "ruta de guardado" al inicio, por ejemplo: "Guardar en: .quinoto-spec/discovery/01-overview.md".
- Usar subsecciones (H2/H3) para organizar hallazgos: Resumen, Detalle, Pasos para reproducir/ejecutar, Recomendaciones.
- Incluir listings de archivos/carpetas relevantes con rutas relativas, comandos para ejecutar la aplicación (dev/build/test), y ejemplos de salida cuando aplique.
- Incluir placeholders para diagramas en Mermaid cuando corresponda (ej.: flujo, arquitectura, ER) y notas sobre qué debería contener cada diagrama.
- Generar contenido accionable y conciso: checklists, comandos sugeridos, y prioridades (alta/media/baja).
- Detecta y documenta frameworks, librerías y versiones (package.json, requirements, etc.).
- Detecta y documenta pruebas automatizadas y cómo ejecutarlas.
Contenido por archivo:

0) 00-stack-profile.md
- **Skill Requerida**: Ejecuta primero la skill `quinotospec-stack-detect`.
- Identificación precisa del stack tecnológico (Lenguaje, Frameworks, Package Manager, Test Runner).
- Detalla los Coding Standards detectados (ej. Service Layer, Hooks, etc.).

1) 01-overview.md
- Resumen ejecutivo del proyecto (qué hace, contexto, lenguaje/plataforma).
- Información del repositorio: estructura de carpetas principales y archivos de entrada.
- Comandos básicos (dev, build, test) y pre-requisitos de entorno.
- Lista rápida de riesgos y puntos críticos identificados.

2) 02-architecture.md
- Diagrama conceptual (Mermaid placeholder) y descripción de la arquitectura (capas, módulos, responsabilidades).
- Patrón(es) de diseño observados.
- Flujo de datos entre componentes (placeholder de diagrama de secuencia).
- Componentes reutilizables e integraciones internas.

3) 03-endpoints-and-openapi.md
- Mapeo de endpoints REST y GraphQL detectados (ruta, método, parámetros, respuesta esperada).
- Generar un OpenAPI/Swagger mínimo (YAML o JSON) con los endpoints principales detectados y ejemplos de request/response.
- Notas sobre autenticación/autorización en endpoints.
- Recomendaciones para pruebas de integración de API.

4) 04-data-and-services.md
- Documentación de bases de datos y esquemas (tablas/colecciones principales, campos importantes).
- Servicios externos integrados y sus propósitos (APIs, proveedores, SDKs).
- Estructura de estado global (si aplica) y modelos de datos.
- Scripts de migración, seeds, y acceso a datos (cómo correrlos).

5) 05-devops-ci-security.md
- Configuración de entorno de desarrollo y variables sensibles requeridas.
- Pipelines de CI/CD detectados (GitHub Actions, GitLab CI, etc.) y pasos de despliegue.
- Scripts de automatización y cron jobs detectados.
- Revisión rápida de prácticas de seguridad (gestión de secretos, políticas CORS, validaciones).
- Estrategias de backup, versionado y recuperación respecto a datos y despliegues.

6) 06-findings-and-recommendations.md
- Informe detallado de descubrimientos: vulnerabilidades, deuda técnica, puntos de mejora (priorizados).
- Sugerencias de acciones inmediatas y roadmap de mejoras (corto, medio, largo plazo).
- Posibles optimizaciones de rendimiento y accesibilidad.
- Checklist de seguimiento y owner sugerido para cada ítem.

7) 07-product-and-agreements.md
- **Visión de Producto**: Encabezado y espacio vacío (o breve placeholder) para describir el propósito.
- **Business Goals/KPIs**: Encabezado y bullet points vacíos para que el equipo complete.
- **Definition of Ready (DoR) / Definition of Done (DoD)**: Solo los títulos de sección. NO generes las listas de chequeo predefinidas. Debe quedar vacío para que el equipo defina sus propios acuerdos.
- **Nota**: Este archivo es una plantilla vacía para ser completada por "Humanos".

Al final del prompt:
- Especifica que cada archivo se guarde exactamente en .quinoto-spec/discovery/ con los nombres arriba indicados.
- Si faltan datos que solo pueden obtenerse ejecutando la app o leyendo archivos, anotar claramente qué comandos o permisos se necesitan para completar la documentación.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la generación de archivos, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Discovery Executed
- **Resumen**: Se exploró el proyecto y se generaron los archivos de especificación en .quinoto-spec/discovery/