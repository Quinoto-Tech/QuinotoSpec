---
description: crear una propuesta independiente
---

# Workflow: Create Proposal

Analiza exhaustivamente la información del Discovery (`.quinoto-spec/discovery/`), poniendo atención especial a `01-stack-profile.md` para adaptar la arquitectura y el código al stack del proyecto, y a `08-product-and-agreements.md` para alinear la propuesta con la visión de producto y los acuerdos de trabajo (DoR/DoD). También revisa otras propuestas existentes en `.quinoto-spec/proposals/` para asegurar consistencia global y **detectar posibles conflictos o solapamientos** de alcance (mismos archivos, dominios o flujos afectados); si detectas alguno, documéntalo al inicio de la propuesta bajo `**⚠️ Conflictos Detectados:**`.
El objetivo es generar una Propuesta Técnica específica para: "**{{PROPOSAL_DESCRIPTION}}**".

**Flags:**
- `--party [agents]`: Ejecuta Party Mode con los agentes especificados ANTES de generar la propuesta. El debate multi-agente enriquece la propuesta con perspectivas cruzadas. Si no se especifican agentes, se auto-seleccionan los mas relevantes segun el tema.
- `--party-output <path>`: Donde guardar la transcripcion del Party Mode (default: `.quinoto-spec/proposals/{{DATE_PREFIX}}-{{PROPOSAL_SLUG}}/party-analysis.md`)

PROPOSAL_NAME: deriva un nombre a partir de PROPOSAL_DESCRIPTION. Debe estar en español o inglés técnico, en Title Case, descriptivo y conciso (ej. `Rewards Stabilization`, `Payment Timeout Fix`, `Refactor Auth Layer`).
PROPOSAL_SLUG: derivar de PROPOSAL_NAME en lowercase con palabras separadas por guión (ej. `rewards-stabilization`, `payment-timeout-fix`).
DATE_PREFIX: fecha actual en formato YYYYMMDD.
Tu objetivo es generar una Propuesta Técnica específica para este tema, INTEGRADA con el resto del sistema.

**Paso 0 — Party Mode (opcional, solo si `--party`):**

Si el usuario paso el flag `--party`, ejecuta Party Mode ANTES de generar la propuesta:

1. **Resolver agentes:**
   - Si `--party` incluye lista de agentes (ej. `--party architect,security-auditor`), usar esos.
   - Si `--party` se paso sin agentes, auto-seleccionar 2-4 agentes basado en `PROPOSAL_DESCRIPTION`:
     - Propuestas de arquitectura → architect, devops-engineer, performance-optimizer
     - Propuestas de seguridad → security-auditor, architect, devops-engineer
     - Propuestas de refactor → refactor-specialist, test-writer, code-reviewer
     - Propuestas de features → architect, test-writer, security-auditor
     - Sin clasificar → architect, security-auditor, test-writer (default)

2. **Ejecutar Party Mode:**
   ```
   @quinotospec.party-mode "{{PROPOSAL_DESCRIPTION}}" \
     --agents {{AGENT_LIST}} \
     --rounds 2 \
     --output .quinoto-spec/proposals/{{DATE_PREFIX}}-{{PROPOSAL_SLUG}}/party-analysis.md
   ```
   - Ronda 1: Cada agente analiza el problema y propone enfoque
   - Ronda 2: Debate — los agentes reaccionan, desafian y refinan

3. **Extraer conclusiones del party:**
   - Puntos de consenso (todos coincidieron)
   - Puntos de disenso (friccion productiva)
   - Recomendaciones accionables
   - Riesgos identificados desde cada especialidad

4. **Usar en la propuesta:**
   - Las conclusiones del party alimentan directamente las secciones de la propuesta:
     - `Resumen Ejecutivo` ← vision consensuada
     - `Alternativas Consideradas` ← enfoques debatidos en el party
     - `Riesgos y Mitigaciones` ← riesgos identificados por cada agente
     - `Plan de Verificación` ← criterios de exito sugeridos por test-writer y security-auditor
   - Incluir seccion `Party Mode Analysis` en proposal.md con:
     ```markdown
     ## Party Mode Analysis
     
     > Esta propuesta fue debatida por un consejo de agentes especializados antes de ser redactada.
     > Ver transcripcion completa en `party-analysis.md`.
     
     ### Agentes Participantes
     {{AGENT_LIST}}
     
     ### Consenso
     {{CONSENSUS_POINTS}}
     
     ### Disenso Productivo
     {{DISSENSUS_POINTS}}
     ```

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
        - `**Party Mode**: ✅ Consejo multi-agente | — No ejecutado`
    - **Separador**: `---`
    - **Party Mode Analysis** (SOLO si `--party`): Transcripcion resumida del consejo de agentes — consenso, disenso, recomendaciones. Ver seccion `Party Mode Analysis` arriba para formato.
    - **Resumen Ejecutivo**: Contexto, objetivo y valor. Si hubo Party Mode, incorporar la vision consensuada del consejo.
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
        - Resumen ejecutivo de cambios por dominio (ver abajo). NO incluye especificaciones completas — los detalles viven en `delta-specs/`.
        - Por cada dominio afectado, incluir un bloque:
          ```
          ### {{dominio}}
          - **AGREGA**: {{resumen de nuevos requerimientos}} → ver `delta-specs/{{dominio}}/spec.md#added-requirements`
          - **MODIFICA**: {{resumen de cambios}} → ver `delta-specs/{{dominio}}/spec.md#modified-requirements`
          - **ELIMINA**: {{resumen de eliminaciones}} → ver `delta-specs/{{dominio}}/spec.md#removed-requirements`
          ```
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
- Genera el archivo `proposal.md` y los archivos `delta-specs/` correspondientes. No generes historias ni tareas.

**Paso Adicional — Generar Delta Specs:**

Despues de generar `proposal.md`, crea los archivos de especificacion delta en formato ADDED/MODIFIED/REMOVED/RENAMED:

1. **Identificar dominios/servicios afectados** desde `**Servicios Afectados:**` en proposal.md.
2. **Por cada dominio afectado:**
   - Crea el directorio `.quinoto-spec/proposals/{{DATE_PREFIX}}-{{PROPOSAL_SLUG}}/delta-specs/{{dominio}}/`
   - Crea el archivo `spec.md` usando el template `delta-spec-template.md`.
   - Lee `.quinoto-spec/specs/{{dominio}}/spec.md` si existe (para contexto de requerimientos actuales).
3. **Llenar el delta spec:**
   - **ADDED Requirements**: Nuevas capacidades que esta propuesta introduce. Una por cada funcionalidad nueva identificada en la propuesta.
   - **MODIFIED Requirements**: Solo si `specs/{{dominio}}/spec.md` existe, identificar requerimientos existentes que cambian. Incluir `Was:` (texto anterior) y `Reason:` (motivo).
   - **REMOVED Requirements**: Solo si `specs/{{dominio}}/spec.md` existe, identificar requerimientos a eliminar. Incluir `Reason:` y `Migration:` (como manejar la eliminacion).
   - **RENAMED Requirements**: Solo si `specs/{{dominio}}/spec.md` existe e identificas renombres necesarios.
4. Si `.quinoto-spec/specs/` no existe o esta vacio, solo usa ADDED — no hay base para MODIFIED/REMOVED/RENAMED.
5. Si un dominio no tiene cambios, no crear archivo spec para ese dominio.
6. **Resumen en proposal.md**: La seccion `Especificacion Tecnica Detallada` de proposal.md debe contener un resumen ejecutivo con referencias a los delta-specs, NO la especificacion completa.

**Gestion de Prefijos (CRITICO):**
1. Lee el archivo `.quinoto-spec/prefix-registry.md` si existe.
2. Determina un prefijo que combine un mnemonico de 4 letras + un sufijo unico de 4 caracteres alfanumericos (ej. `AUTH-a1b2`, `REWA-c3d4`, `PAYF-x9y0`).
   - El mnemonico debe representar la propuesta (ej. `REWA` para Rewards).
   - El sufijo garantiza la idempotencia y evita colisiones en entornos multi-usuario.
3. **Validacion en Tiempo Real**: Antes de registrar el prefijo:
   - Verifica que no exista ya en `prefix-registry.md` (ni el mnemonico completo ni el prefijo completo)
   - Si el mnemonico existe con diferente sufijo, sugiere reutilizarlo: "El mnemonico AUTH ya existe como AUTH-a1b2. ¿Reutilizar AUTH-{nuevo}?"
   - Si el prefijo completo existe, genera un nuevo sufijo automaticamente
4. Anade una nueva fila a la tabla en `.quinoto-spec/prefix-registry.md`: `| {{PREFIX}} | {{PROPOSAL_NAME}} | {{DATE}} |`.
5. En el `proposal.md` generado, incluye una linea al inicio (despues del titulo) que diga: `**Prefijo:** {{PREFIX}}`.

**Deteccion de Conflictos con Propuestas Existentes:**
Antes de finalizar la propuesta, ejecuta un check de conflictos:
1. Lee todas las propuestas activas en `.quinoto-spec/proposals/*/proposal.md`
2. Compara "Servicios Afectados" con los de propuestas activas
3. Compara archivos mencionados en "Archivos Afectados"
4. Si detectas solapamiento:
   - Documentalo bajo `**Conflictos Detectados:**` al inicio de la propuesta
   - Sugiere al usuario: "Esta propuesta solapa con {propuesta_existente} en {area}. ¿Continuar o ajustar alcance?"
5. Si no hay conflictos, indica: `**Conflictos Detectados:** Ninguno`

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completada, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Proposal Generated: {{PROPOSAL_NAME}}{{#if PARTY}} (Party Mode: {{AGENT_COUNT}} agentes){{/if}}
- **Resumen**: Se generó la propuesta base '{{PROPOSAL_NAME}}' en .quinoto-spec/proposals/{{DATE_PREFIX}}-{{PROPOSAL_SLUG}}/. {{#if PARTY}}Precedida por Party Mode con {{AGENT_COUNT}} agentes — ver party-analysis.md.{{/if}}`
