---
description: crear una propuesta independiente
---

Analiza exhaustivamente la información del Discovery (`.quinoto-spec/discovery/`), poniendo atención especial a `07-product-and-agreements.md` para alinear la propuesta con la visión de producto y los acuerdos de trabajo (DoR/DoD). También revisa otras propuestas existentes en `.quinoto-spec/proposals/` para asegurar consistencia global.
El objetivo es generar una Propuesta Técnica específica para: "**{{PROPOSAL_DESCRIPTION}}**".
PROPOSAL_NAME: inveta un nombre a partir de PROPOSAL_DESCRIPTION
Tu objetivo es generar una Propuesta Técnica específica para este tema, INTEGRADA con el resto del sistema.
Debes crear una carpeta `.quinoto-spec/proposals/{{PROPOSAL_SLUG}}/` y generar dentro de ella el archivo `proposal.md`:

1. **proposal.md**:
    - **Título**: Propuesta Técnica: {{PROPOSAL_NAME}}.
    - **Resumen Ejecutivo**: Descripción de esta iniciativa específica.
    - **Arquitectura/Diseño**: Detalles técnicos de cómo implementar esta propuesta.
    - **Riesgos y Mitigaciones**.

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