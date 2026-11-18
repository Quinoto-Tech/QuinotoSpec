# Plan de Tareas (Validator Path Resolution — US-VPAT-k4m7-002)

**Proposal ID:** 2026-11-17-validator-path-resolution
**Prefijo:** VPAT-k4m7
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-VPAT-k4m7-003 | Config | Auditoría de los ~108 archivos con `agent-dist/` | Clasificar cada ocurrencia `agent-dist/` en `.md` del payload: (a) comando ejecutable a reescribir, (b) referencia semántica "repo fuente" que requiere exclusión documentada. Salida: lista de exclusiones respaldada por el suite. Registrar evidencia en `.quinoto-spec/evidence/TSK-VPAT-k4m7-003/`. | US-VPAT-k4m7-002 | installer | agent-dist/workflows/*.md, agent-dist/skills/*/SKILL.md (solo lectura; resultado en tests/test-installed-paths.sh) | S | P1 | TSK-VPAT-k4m7-001 | [x] |
| TSK-VPAT-k4m7-004 | Backend | `normalize_staged_paths` en install.sh + wiring | Nueva función `normalize_staged_paths <candidate> <install_root>`: `sed "s\|agent-dist/\|$INSTALL_ROOT/\|g"` y `s\|\bagent-dist\b\|$INSTALL_ROOT\|g` acotado a `.md` de `workflows/commands, skills, rules, bootstrap, templates, agents, config`; escaping de `&`, delimitador `|`, quoting estricto, preservar endings. Wire post-staging y pre-manifest. GREEN de TSK-001. | US-VPAT-k4m7-002 | installer | install.sh, tests/test-installed-paths.sh | M | P1 | TSK-VPAT-k4m7-001, TSK-VPAT-k4m7-003 | [x] |
| TSK-VPAT-k4m7-005 | Test | E2E del preflight del bootstrap instalado | Aserción de criterio de aceptación: en el fixture instalado, extraer el comando de preflight del bootstrap, verificar que el script referenciado existe y `contract.py validate --root <fixture> --strict` corre exit 0. Casos de idempotencia y de ruta con espacios/`&`. | US-VPAT-k4m7-002 | installer | tests/test-installed-paths.sh | S | P1 | TSK-VPAT-k4m7-004 | [x] |
