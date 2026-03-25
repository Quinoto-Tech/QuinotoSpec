---
description: Realizar un análisis profundo de riesgos y cuellos de botella en un flujo específico.
---

Este workflow utiliza el agente `Risk Detector` y la skill `expert-flow-analyzer` para auditar un flujo de la aplicación.

### Pasos del Workflow:

1. **Identificación del Target**:
   - Define el punto de entrada (Ej: `POST /api/orders/`).
   - El `Risk Detector` debe mapear el archivo de URL y la Vista correspondiente.

2. **Mapeo de Flujo (Deep Trace)**:
   - Recorrer el flujo desde la Vista hasta los Modelos/Servicios.
   - Identificar llamadas a bases de datos (SQL/ORM).
   - Identificar llamadas a servicios externos (APIs, Redis, Celery).

3. **Análisis de Impacto**:
   - **Riesgo de Rendimiento**: Detectar queries N+1, falta de índices, o procesos pesados en el hilo principal.
   - **Riesgo de Fiabilidad**: Buscar falta de manejo de excepciones en integraciones críticas.
   - **Riesgo de Seguridad**: Verificar validaciones de entrada y permisos.

4. **Generación de Reporte**:
   - Crear un archivo en `.quinoto-spec/analysis/YYYYMMDD-risk-report-[nombre-flujo].md`.
   - Incluir un diagrama Mermaid del flujo analizado.
   - Clasificar los hallazgos por severidad (Crítica, Alta, Media, Baja).

5. **Actualización de Changelog**:
   - Ejecutar la skill `quinotospec-update-changelog`.
   - **Acción**: Risk Analysis Performed.
   - **Resumen**: Análisis de riesgos completado para el flujo [nombre-flujo].
