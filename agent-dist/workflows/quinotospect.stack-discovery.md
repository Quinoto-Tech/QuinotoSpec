---
description: Generar documentación de descubrimiento del stack del proyecto distrubuido en diferentes carpetas en .quinoto-spec/discovery
---

Dentro de todas las carpetas del root debe existir */.quinoto-spec/discovery, de no ser así no realizar la tarea 

Explora el proyecto completo y genera 7 archivos Markdown independientes dentro de .quinoto-spec/discovery con los siguientes nombres EXACTOS (dentro del proyecto):
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
- Incluir listings de carpetas de los proyectos en el root general
- Incluir placeholders para diagramas en Mermaid cuando corresponda (ej.: flujo, arquitectura, ER) y notas sobre qué debería contener cada diagrama.
- Generar contenido accionable y conciso: checklists, comandos sugeridos, y prioridades (alta/media/baja).


0) 00-stack-profile.md
- Lee todos los archivos */.quinoto-spec/discovery/00-stack-profile.md
- resume la información

1) 01-overview.md
- Lee todos los archivos */.quinoto-spec/discovery/01-overview.md
- resume la información
- Lista rápida de riesgos y puntos críticos identificados.

2) 02-architecture.md
- Lee todos los archivos */.quinoto-spec/discovery/02-architecture.md
- Estudia como se comunican los diferentes componentes y su proposito general
- Flujo de datos entre componentes, incluir cualquirer tipo de persistencia, no incluir servicios externos
- crear un apartado con los servicios externos (los que no figuran en el root pero estan dentro de  */.quinoto-spec/discovery/02-architecture.md)
- apliar los diagramas de secuencia que ya exiten en los archivos  */.quinoto-spec/discovery/02-architecture.md
- Componentes reutilizables e integraciones internas.

3) 03-endpoints-and-openapi.md
- Lee todos los archivos */.quinoto-spec/discovery/03-endpoints-and-openapi.md
- resume la información
- Lista rápida de riesgos y puntos críticos identificados.

4) 04-data-and-services.md
- Lee todos los archivos */.quinoto-spec/discovery/04-data-and-services.md
- resume la información
- Lista rápida de riesgos y puntos críticos identificados.

5) 05-devops-ci-security.md
- Lee todos los archivos */.quinoto-spec/discovery/05-devops-ci-security.md
- resume la información
- Lista rápida de riesgos y puntos críticos identificados.

6) 06-findings-and-recommendations.md
- Lee todos los archivos */.quinoto-spec/discovery/06-findings-and-recommendations.md
- resume la información
- Lista rápida de riesgos y puntos críticos identificados.

7) 07-product-and-agreements.md
- Lee todos los archivos */.quinoto-spec/discovery/06-findings-and-recommendations.md
- resume la información


Al final de la ejecución:
- Especifica que cada archivo se guarde exactamente en .quinoto-spec/discovery/ con los nombres arriba indicados.
- Si faltan datos que solo pueden obtenerse ejecutando la app o leyendo archivos, anotar claramente qué comandos o permisos se necesitan para completar la documentación.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada la generación de archivos, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Discovery Executed
- **Resumen**: Se exploró el proyecto y se generaron los archivos de especificación en .quinoto-spec/discovery/