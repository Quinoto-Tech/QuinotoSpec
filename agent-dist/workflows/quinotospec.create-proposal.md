---
description: crear una propuesta independiente
---

Analiza exhaustivamente la información del Discovery (`.quinoto-spec/discovery/`), poniendo atención especial a `00-stack-profile.md` para adaptar la arquitectura y el código al stack del proyecto, y a `07-product-and-agreements.md` para alinear la propuesta con la visión de producto y los acuerdos de trabajo (DoR/DoD). También revisa otras propuestas existentes en `.quinoto-spec/proposals/` para asegurar consistencia global.
El objetivo es generar una Propuesta Técnica específica para: "**{{PROPOSAL_DESCRIPTION}}**".
PROPOSAL_NAME: inveta un nombre a partir de PROPOSAL_DESCRIPTION
Tu objetivo es generar una Propuesta Técnica específica para este tema, INTEGRADA con el resto del sistema.
Debes crear una carpeta `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/` y generar dentro de ella el archivo `proposal.md` con el siguiente formato esperado:

1. **proposal.md**:
    - **Título**: `# Propuesta Técnica: {{PROPOSAL_NAME}}`
    - **Metadatos iniciales (en este orden)**:
        - `**Prefijo:** {{PREFIX}}`
        - `**Fecha de Creación**: YYYY-MM-DD`
        - `**Estado**: 🟡 Propuesta`
        - `**Prioridad**: P1 | P2 | P3`
        - `**Complejidad**: Baja | Media | Alta`
    - **Separador**: `---`
    - **Resumen Ejecutivo**: Contexto, objetivo y valor.
    - **Problema Actual**: Lista concreta de fricciones actuales.
    - **Solución Propuesta**: Descripción clara de la iniciativa.
    - **Beneficios**: Impacto en tiempo, calidad, UX/DX o negocio.
    - **Alineación con Producto y Acuerdos**:
        - Visión de Producto.
        - KPIs Impactados.
        - Cumplimiento de DoR con checklist.
    - **Arquitectura y Diseño Técnico**:
        - Diagrama `mermaid` del flujo.
        - Estructura/variables principales.
        - Flujo de ejecución paso a paso.
    - **Especificación Técnica Detallada**:
        - Bloques de código relevantes.
        - Ubicaciones de archivos y permisos.
    - **Riesgos y Mitigaciones**:
        - Tabla de riesgos + estrategias de mitigación.
    - **Plan de Implementación**:
        - Fases con tiempos estimados.
    - **Criterios de Aceptación (DoD)**:
        - Checklist por implementación, testing y documentación.
    - **Plan de Verificación**:
        - Tests manuales con pasos y resultados esperados.
    - **Impacto en el Sistema**:
        - Archivos nuevos/modificados.
        - Dependencias y tooling requerido.
    - **Roadmap Futuro (Opcional)**:
        - Mejoras potenciales.
    - **Conclusión**:
        - Síntesis y próximos pasos.
        - `**Aprobación Requerida**`, `**Estimación Total**`, `**Prioridad**`, `**Fecha Límite Sugerida**`.

**Instrucciones de Ejecución:**
- Crea los directorios necesarios.
- Escribe en español técnico.
- SOLO genera el archivo `proposal.md`. No generes historias ni tareas.

**Gestión de Prefijos (CRÍTICO):**
1. Lee el archivo `.quinoto-spec/prefix-registry.md`.
2. Genera un prefijo único de 3-4 letras (ej. `ABC`, `PROJ`) que NO exista en la tabla.
3. Añade una nueva fila a la tabla en `.quinoto-spec/prefix-registry.md`: `| {{PREFIX}} | {{PROPOSAL_NAME}} | {{DATE}} |`.
4. En el `proposal.md` generado, incluye una línea al inicio (después del título) que diga: `**Prefijo:** {{PREFIX}}`.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Proposal Generated: {{PROPOSAL_NAME}}
- **Resumen**: Se generó la propuesta base '{{PROPOSAL_NAME}}' en .quinoto-spec/proposals/{{PROPOSAL_SLUG}}/
