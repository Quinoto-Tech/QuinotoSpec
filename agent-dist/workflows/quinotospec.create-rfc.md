---
description: crear un RFC proposal-ready en modo conversacional (compatible con create-tasks --from-rfc)
---

Objetivo: crear un RFC nuevo usando el template oficial, guiando al usuario con preguntas iterativas y dejandolo listo para derivar una propuesta QuinotoSpec.

Regla principal:
- El flujo es interactivo: pregunta una cosa por vez, espera respuesta y confirma antes de avanzar.
- Si el usuario ya dio un dato, no lo vuelvas a pedir.
- Si falta informacion, no generes el archivo hasta tener confirmacion final.

Preguntas obligatorias (en este orden):
1. `TITLE`: "Cual es el titulo del RFC?"
2. `SLUG`: proponer kebab-case en base al titulo y preguntar: "Uso este slug: <slug>?"
3. `AUTHOR`: "Quien es el autor responsable?"
4. `REVIEWERS`: "Quienes son los revisores? (separados por coma)"
5. `REFERENCE`: "Que issue/ticket/documento lo referencia?"
6. `PRIORITY`: "Prioridad sugerida? (P1/P2/P3)"
7. `COMPLEXITY`: "Complejidad estimada? (Baja/Media/Alta)"
8. `AFFECTED_SERVICES`: "Que servicios impacta? (separados por coma)"
9. `PREFIX` (para tareas): "Cual es el prefijo QuinotoSpec para IDs de historias/tareas (formato `MNEM-xxxx`, ej. `AUTH-a1b2`)? Debe figurar en `.quinoto-spec/prefix-registry.md` o acordarse antes de registrarlo."

Confirmacion final obligatoria:
- Antes de escribir archivos, mostrar resumen:
  - Titulo
  - Slug
  - Autor
  - Revisores
  - Referencia
  - Prioridad
  - Complejidad
  - Servicios afectados
  - Prefijo QuinotoSpec (US/TSK)
- Preguntar: "Confirmas que genero el RFC con estos datos? (si/no)"
- Si responde "no", corregir solo los campos indicados y volver a confirmar.

Generacion del RFC:
1. Usa el template base `.cursor/templates/rfc-template.md`.
2. Genera `RFC_ID` con formato `RFC-YYYYMMDD-{{SLUG_UPPER}}` (ejemplo: `RFC-20260427-FEATURE-FLAGS`).
3. Si `.quinoto-spec/rfc/` no existe, crealo.
4. Crea `.quinoto-spec/rfc/{{RFC_ID}}-{{SLUG}}.md`.
5. Reemplaza placeholders del template:
   - `{{RFC_ID}}`
   - `{{TITLE}}`
   - `{{SLUG}}`
   - `{{AUTHOR}}`
   - `{{DATE}}` (YYYY-MM-DD)
   - `{{REVIEWERS}}`
   - `{{REFERENCE}}`
   - `{{PRIORITY}}`
   - `{{COMPLEXITY}}`
   - `{{AFFECTED_SERVICES}}`
   - `{{PREFIX}}` (si el template lo declara; si no, el prefijo solo va en la seccion de User Stories del paso 9).
6. Leer discovery consolidado como base minima de contexto:
   - `.quinoto-spec/discovery/02-overview.md`
   - `.quinoto-spec/discovery/03-architecture.md`
   - `.quinoto-spec/discovery/04-endpoints-and-openapi.md`
   - `.quinoto-spec/discovery/07-findings-and-recommendations.md`
   - `.quinoto-spec/discovery/08-product-and-agreements.md`
7. Completar el RFC con la data relevada interactivamente + discovery (no dejarlo en placeholders):
   - `1. Contexto`: problema actual concreto del stack/servicio.
   - `2. Objetivo`: resultado medible esperado.
   - `4. Propuesta`: solucion tecnica inicial coherente con arquitectura vigente.
   - `6. Impacto tecnico`: servicios, contratos y dependencias impactadas.
   - `7. Plan de implementacion`: fases iniciales y orden sugerido.
   - `8. Riesgos y mitigaciones`: al menos 3 riesgos reales con mitigacion.
   - `9. Plan de pruebas`: unit/integration/e2e y criterio de exito.
8. Mantener estructura de secciones intacta y completar la seccion "Proposal Seed" para que `quinotospec.create-proposal` pueda usar este RFC como input directo.
9. **Obligatorio para `quinotospec.create-tasks`**: Incluir al final del RFC (antes de anexos si los hay) la seccion con heading **exacto**:

   `## User Stories (entrada para create-tasks)`

   Contenido minimo:
   - Una linea: `**Prefijo (QuinotoSpec):** {{PREFIX}}` (el valor de `PREFIX` de la pregunta 9).
   - Una tabla con el **mismo formato** que `quinotospec.create-user-stories` (columnas: ID, User Story, Criterios de Aceptacion, Prioridad, Estimacion, Servicio). Los IDs deben seguir `US-{{PREFIX}}-001`, `US-{{PREFIX}}-002`, etc. (igual que en `create-user-stories`: si el prefijo es `AUTH-a1b2`, el primer ID es `US-AUTH-a1b2-001`).

10. Enviar al usuario la ruta final del RFC generado, un resumen de 3 bullets con decisiones clave, y la **linea de comando sugerida** para generar tareas:

   `@quinotospec.create-tasks --from-rfc .quinoto-spec/rfc/{{RFC_ID}}-{{SLUG}}.md`

   (ajustar la ruta al archivo real creado en el paso 4).

Resultado esperado:
- El usuario es guiado paso a paso y valida los datos antes de crear el archivo.
- RFC creado en `.quinoto-spec/rfc/` con estructura uniforme, contenido inicial no vacio y compatible con derivacion a propuesta.
- La seccion `## User Stories (entrada para create-tasks)` permite ejecutar `quinotospec.create-tasks --from-rfc <ruta-al-rfc.md>` sin pasar antes por `proposal.md` / `user-stories.md` en carpeta de propuesta.
