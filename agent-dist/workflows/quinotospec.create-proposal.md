---
description: crear una propuesta independiente
---

Analiza exhaustivamente la información del Discovery (`.quinoto-spec/discovery/`), poniendo atención especial a `00-stack-profile.md` para adaptar la arquitectura y el código al stack del proyecto, y a `07-product-and-agreements.md` para alinear la propuesta con la visión de producto y los acuerdos de trabajo (DoR/DoD). También revisa otras propuestas existentes en `.quinoto-spec/proposals/` para asegurar consistencia global y **detectar posibles conflictos o solapamientos** de alcance (mismos archivos, dominios o flujos afectados); si detectas alguno, documéntalo al inicio de la propuesta bajo `**⚠️ Conflictos Detectados:**`.
El objetivo es generar una Propuesta Técnica específica para: "**{{PROPOSAL_DESCRIPTION}}**".
PROPOSAL_NAME: deriva un nombre a partir de PROPOSAL_DESCRIPTION. Debe estar en español o inglés técnico, en Title Case, descriptivo y conciso (ej. `Rewards Stabilization`, `Payment Timeout Fix`, `Refactor Auth Layer`).
PROPOSAL_SLUG: derivar de PROPOSAL_NAME en lowercase con palabras separadas por guión (ej. `rewards-stabilization`, `payment-timeout-fix`).
DATE_PREFIX: fecha actual en formato YYYYMMDD.
Tu objetivo es generar una Propuesta Técnica específica para este tema, INTEGRADA con el resto del sistema.
Debes crear una carpeta `.quinoto-spec/proposals/{{DATE_PREFIX}}-{{PROPOSAL_SLUG}}/` y generar dentro de ella el archivo `proposal.md` con el siguiente formato esperado:

1. **proposal.md**:
    - **Título**: `# Propuesta Técnica: {{PROPOSAL_NAME}}`
    - **Metadatos iniciales (en este orden)**:
        - `**Prefijo:** {{PREFIX}}`
        - `**Fecha de Creación**: YYYY-MM-DD`
        - `**Estado**: 🟡 Propuesta`
        - `**Prioridad**: P1 | P2 | P3`
        - `**Complejidad**: Baja | Media | Alta`
        - `**Servicios Afectados**: [lista de servicios/sub-proyectos impactados, separados por comas. Ej: auth-service, user-service, gateway]`
    - **Separador**: `---`
    - **Resumen Ejecutivo**: Contexto, objetivo y valor.
    - **Problema Actual**: Lista concreta de fricciones actuales.
    - **Alternativas Consideradas**: Tabla con al menos 2 alternativas evaluadas, sus pros/contras y el motivo por el que se descartaron.
    - **Solución Propuesta**: Descripción clara de la iniciativa y por qué es la opción elegida.
    - **Beneficios**: Impacto en tiempo, calidad, UX/DX o negocio.
    - **Alineación con Producto y Acuerdos**:
        - Visión de Producto.
        - KPIs Impactados.
        - Cumplimiento de DoR con checklist.
    - **Arquitectura y Diseño Técnico**:
        - **Diagrama de secuencia obligatorio en Mermaid** (`sequenceDiagram`) mostrando el flujo principal de la funcionalidad propuesta (actores, servicios, base de datos e integraciones externas involucradas).
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
        - Tests manuales: pasos detallados y resultados esperados.
        - Tests automatizados sugeridos: tipo (unit/integration/e2e), qué cubrir y comando de ejecución.
        - Criterio de éxito medible vinculado al KPI impactado (ej. "Reducción del tiempo de respuesta de X a Y ms").
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
1. Lee el archivo `.quinoto-spec/prefix-registry.md` si existe.
2. Determina un prefijo de 4 letras que represente la propuesta (ej. `REWA` para Rewards, `AUTH` para Auth, `PAYF` para Payment Fix).
   - Debe ser mnemotécnico y estar relacionado con el nombre de la propuesta.
   - Si hay conflicto con un prefijo existente, añade una letra adicional para diferenciarlo (ej. `AUT2`).
3. Añade una nueva fila a la tabla en `.quinoto-spec/prefix-registry.md`: `| {{PREFIX}} | {{PROPOSAL_NAME}} | {{DATE}} |`.
4. En el `proposal.md` generado, incluye una línea al inicio (después del título) que diga: `**Prefijo:** {{PREFIX}}`.

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Proposal Generated: {{PROPOSAL_NAME}}
- **Resumen**: Se generó la propuesta base '{{PROPOSAL_NAME}}' en .quinoto-spec/proposals/{{DATE_PREFIX}}-{{PROPOSAL_SLUG}}/
