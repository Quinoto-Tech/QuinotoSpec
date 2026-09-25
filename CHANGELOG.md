# Changelog - QuinotoSpec

Todos los cambios notables en el paquete QuinotoSpec serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.2.0] - 2026-09-25 - Warband: Hird Edition (Beta/RC)

### Summary
- Release 3.2.0 con la integración de F3.2 en el contexto de inicio de sesión.
- La release mantiene el estado beta/RC; F3.1 y F3.3 permanecen fuera de este incremento.

### Added
- **Party Mode F3.2.5**: `/quinotospec.party-mode` y el modo `--subagents` ahora están referenciados por el bootstrap de sesión.
- **Prueba de bootstrap**: verifica que Party Mode y sus opciones estén disponibles al iniciar sesión.

### Changed
- **Versión**: bump semver de `3.1.0` a `3.2.0` en manifest, installer, plugin Cursor, `.version` y documentación.
- **Inventario**: 43 workflows, 86 skills, 18 reglas, 9 agentes y 13 templates; no se agregan componentes de F3.1/F3.3.
- **Estado de fases**: F3.2 y la infraestructura F3.4 de esta release quedan completas; F3.1 y F3.3 siguen pendientes.
- **Validación**: release package, smoke test, bootstrap y suite completa pasan antes de publicar.

### Known limitations
- La capacidad de orchestrar agentes y ejecutar subagentes depende del IDE y sus herramientas.
- Las extensiones siguen siendo locales, sin firma ni descarga remota.
- La release permanece beta/RC por límites operativos externos.

**Tiempo Ahorrado**: ~1h (IA: ~15min vs Humano: ~1h)

---

## [3.1.0] - 2026-09-25 - Warband: Hird Edition (Beta/RC)

### Summary
- Cierre de la Fase 2: extensibilidad local, presets, resolución de templates y generación dinámica de `AGENTS.md`.
- F2.5 sincroniza la versión, la documentación y el inventario del paquete; la release conserva su estado beta/RC.

### Added
- **Extensiones y presets F2.3**: extension manager transaccional, presets, catálogos locales, manifests y hooks explícitos.
- **AGENTS dinámico F2.4**: `config.yaml`, template, workflow y generador atómico; el installer genera el archivo durante staging.
- **Documentación de contribución F2.5**: guía para publicar y mantener extensiones sin red ni ejecución remota de hooks.

### Changed
- **Versión**: bump semver de `3.0.0` a `3.1.0` en manifest, installer, plugin Cursor y `.version`.
- **Inventario**: 43 workflows, 86 skills, 18 reglas, 9 agentes y 13 templates.
- **Estado de fases**: Gate 0 y Fase 2 marcados como completos; larelease permanece beta/RC por límites operativos externos.
- **Validación**: la suite completa mantiene 20 suites, contrato estricto, release smoke y checks estáticos.

### Known limitations
- Las extensiones son locales y los hooks solo se ejecutan con confirmación explícita; no hay descarga remota ni firma de paquetes.
- La identidad humana, disaster recovery multi-repo y endurecimiento de permisos siguen fuera del alcance.
- Worktrees y algunas capacidades Nordic mantienen límites prompt-only, experimentales o de demostración.

**Tiempo Ahorrado**: ~6h (IA: ~45min vs Humano: ~6h)

---

## [3.0.0] - 2026-09-24 - Warband: Hird Edition (Beta/RC)

### Summary
- Cierre de la Fase 1: contrato canónico de artefactos, disciplina de ingeniería, constitution, recepción verificable de feedback y aislamiento opcional con worktrees.
- Release candidate de Hird Edition; Gate 0 completa sus gates observables y conserva límites operativos externos.

### Added
- **Artifact contract**: parser y validador canónico read-only para proposals, user stories, tasks, IDs, estados, relaciones y changelog v1/v2.
- **Bootstrap de sesión**: hooks para OpenCode, Cursor, Claude Code y Generic, con plugin OpenCode y manifest de Cursor.
- **Disciplina de ingeniería**: skills TDD, Debug, Verify Before Done, Constitution, Receive Review y Worktree.
- **Constitution**: principios verificables con aprobación explícita y gates de Apply, Review y Archive.
- **Worktrees**: detección de aislamiento existente, herramientas nativas, fallback Git, permisos seguros, sandbox y baseline limpia.
- **Governance gate G0.1**: dispatcher read-only con salida JSON para contrato, prefijo, changelog, acuerdo de producto, branches, rutas protegidas y configuración crítica.
- **Backup engine G0.2**: snapshots SHA-256, manifest verificable, staging/rename atómico, restore con backup de seguridad y cleanup seguro.
- **Evidence gate G0.2b**: validador read-only para registros frescos y tipados de TDD, Debug y Verify-Before-Done; la ejecución real y las decisiones humanas siguen explícitas.
- **Human approval gate G0.2c**: validador read-only para decisiones humanas `approved`, `rejected` o `deferred`, con scope, acción, responsable, fecha y justificación obligatorios.
- **Transactional installer**: staging sibling, verificación previa al commit, manifest de ownership con SHA-256, rollback de configuración/AGENTS.md y uninstall selectivo que conserva archivos ajenos.
- **Release package gate**: `package-release.sh` genera tarball sin caches y checksum SHA-256; `smoke-release.sh` instala, verifica, inspecciona ownership y desinstala desde el artefacto extraído.

### Changed
- **Inventario**: 40 workflows, 83 skills, 18 reglas, 9 agentes y 9 templates.
- **Installer y runtime**: soporte de IDEs, hooks, plugins, bootstrap, preservation de configuración y verificación post-instalación.
- **Validación**: contrato estricto, dispatcher de gobernanza read-only, evidencia TDD/debug/verify, aprobaciones humanas estructuradas, motor de backup, installer transaccional y release package gate integrados en CI, `validate-all.sh` y 18 suites de pruebas.
- **Documentación**: README ES/EN, AGENTS.md, arquitectura y roadmap sincronizados con la línea base de Fase 1.

### Known limitations
- TDD, Debug y Verify tienen validación estructural de evidencia; Constitution, Receive Review y Worktree conservan componentes prompt-only.
- El validador no ejecuta comandos ni reemplaza decisiones humanas explícitas.
- El installer ya es transaccional y ownership-safe; disaster recovery multi-repo y endurecimiento de permisos siguen fuera de alcance.
- Gate 0 queda completo; el release mantiene beta/RC por disaster recovery multi-repo, helpers experimentales y límites de identidad fuera del paquete.

**Tiempo Ahorrado**: ~30h (IA: ~3h vs Humano: ~30h)

---

## [2.7.0] - 2026-09-05 - Warband: Nórdicas

### Summary
v2.7.0 es la edición "Warband: Nórdicas" — 7 nuevas skills de gobernanza, observabilidad y federación que elevan el framework a 76 skills.

### Added
- **Norns** (`quinotospec-norns`): Las Tejedoras del Destino — versionado atómico y changelog semver sin drift. Sincroniza versión en todos los docs y valida sin dejar desfases
- **Huginn & Muninn** (`quinotospec-huginn-muninn`): Los Cuervos de Odin — observabilidad continua de entropía y drift. Cron Tiwaz + contract drift alerting sin intervención manual
- **Skald** (`quinotospec-skald`): El Poeta de la Corte — docs viva sin duplicación. Unifica onboard-* y sincroniza README bilingüe desde fuente única
- **Jormungandr** (`quinotospec-jormungandr`): La Serpiente del Mundo — detección de ciclos en DAG de artefactos y grafo de imports
- **Valkyrie** (`quinotospec-valkyrie`): La Electora de los Caídos — triage inteligente de propuestas (qué vive, qué muere, qué va a Valhalla)
- **Bifrost** (`quinotospec-bifrost`): El Puente Arcoíris — federación multi-repo con schema federado y git notes sync
- **Mimir** (`quinotospec-mimir`): La Cabeza Sabia — índice BM25 cita-exacta sobre discovery/specs/proposals, responde por qué con file:line

### Changed
- **Infrastructure**: Actualizados badges, versiones, conteos (39 workflows, 76 skills, 13 reglas), README ES/EN, AGENTS.md, docs/ARCHITECTURE.md con las 7 sagas nórdicas

---

## [2.6.0] - 2026-07-17

### Added
- **Post de anuncio `docs/posts/v2.6.0-tiwaz-rune-post.md`**: Anuncio oficial del Tiwaz Rune v2.6.0 — entropia de Shannon, proxies de deuda tecnica y plan de remediacion

### Changed
- **Infrastructure**: Actualizados badges, versiones, conteos (39 workflows, 76 skills, 13 reglas), install.sh, manifest.json — soporte Antigravity (AGY)

### Summary
v2.6.0 es la edicion "Yggdrasil - Tiwaz Rune": el analisis formal de entropia con metricas de Shannon y proxies de deuda tecnica es ahora el feature insignia estadistico del framework. Incluye anuncio en formato post para difusion.

---

## [2.5.0] - 2026-06-12

### Added
- **The Tiwaz Rune** (`@quinotospec.tiwaz-rune`): Análisis formal de entropía de código con métricas de Shannon (v2) y proxies de deuda técnica (v1). Genera score compuesto, hallazgos por dimensión, plan de remediación priorizado y métricas de seguimiento
- **Entropy Calculator** (`quinotospec-entropy-calculator`): Skill que provee fórmulas, heurísticas por stack y comandos para calcular métricas de entropía formales y proxies
- **Template `tiwaz-rune-report-template.md`**: Template para reportes de entropía con frontmatter YAML, tablas de scores, gráficos ASCII y plan de remediación
- **Changelog v2 (Append-Only)**: Nuevo formato de changelog con archivos individuales en `.quinoto-spec/changelog/YYYY-MM-DD-PREFIX-SLUG.md` — elimina merge conflicts en equipos multi-agente
- **Template `changelog-entry-template.md`**: Template para entradas v2 con placeholders de fecha, título, resumen y métricas
- **Workflow `@quinotospec.changelog-view`**: Vista consolidada que combina entradas v2 y v1 con filtros por fecha, prefijo y texto
- **INDEX.md regenerable**: Tabla de contenido auto-generada en `changelog/INDEX.md`, gitignored, nunca commiteada

### Changed
- **`quinotospec-update-changelog`**: Auto-detección de formato (v1 si solo existe quinoto-spec-changelog.md, v2 si existe changelog/). Modo v2 crea archivos individuales y regenera INDEX.md
- **`@quinotospec.init`**: Crea directorio `changelog/` con `.gitignore` en la estructura base
- **Infrastructure**: Actualizados badges, versiones, conteos (37 workflows, 29 skills), AGENTS.md, validate-all.sh, ARCHITECTURE.md, install.sh

### Compatibility
- **Backward compatible**: Si solo existe `quinoto-spec-changelog.md`, la skill usa formato v1 automáticamente
- **Coexistencia**: v1 y v2 pueden convivir — changelog-view detecta duplicados y prioriza v2

---

## [2.4.0] - 2026-06-11

### Added
- **Party Mode** (`@quinotospec.party-mode`): Mesa redonda multi-agente donde los agentes discuten, debaten y colaboran en caracter sobre un tema
- **Party Orchestrator** (`quinotospec-party-orchestrator`): Skill orquestador con monitoreo de salud de la discusion (groupthink, impasse, dominacion)
- **Voiced by Orchestrator** (`voiced-by-orchestrator.md`): Estrategia rapida — el agente principal voicea 2-4 agentes en un solo hilo. Tecnicas de voicing, vocabulario por especialidad, anti-patrones
- **Spawned Subagents** (`spawned-subagents.md`): Estrategia profunda — cada agente es un subagente independiente con contexto aislado. Rondas paralelas y secuenciales
- **`--party` flag en `create-proposal`**: Party Mode se integra como paso previo a la generacion de la propuesta. El consejo debate antes de redactar — conclusiones alimentan automaticamente Resumen, Alternativas, Riesgos y Plan de Verificacion
- **`--party` flag en `create-rfc`**: Party Mode se integra en la fase de Contexto y Propuesta del RFC. Consenso, disenso y recomendaciones del consejo enriquecen el RFC generado

### Changed
- **Infrastructure**: Actualizados badges, versiones, conteos (36 workflows, 29 skills), AGENTS.md, validate-all.sh, ARCHITECTURE.md, install.sh

### Resumen Consolidado v2.1.0 → v2.4.0
- **+3 workflows**: specs-init, schema-fork, party-mode
- **+2 skills**: artifact-engine, party-orchestrator (+ 2 strategy files)
- **+2 templates**: delta-spec-template.md, schema-template.yaml
- **+1 directorio**: agent-dist/agents/ refactorizado con personalidades para Party Mode
- **Delta Specs**: Sistema completo de especificaciones incrementales con engine de merge
- **Artifact DAG**: Schema YAML con dependencias formales y topological sort
- **Party Mode**: Mesa redonda multi-agente con dos modos de ejecucion

---

## [2.3.0] - 2026-06-11

### Added
- **Artifact Dependency Graph Engine** (`quinotospec-artifact-engine`): Computa estado del DAG de artefactos basado en schema YAML — determina que artefactos estan listos, bloqueados o completados
- **Schema YAML** (`schema-template.yaml`): Define formalmente artefactos, dependencias, templates e instrucciones. Soporta topological sort
- **Workflow `@quinotospec.schema-fork`**: Permite crear schemas personalizados agregando/eliminando artefactos o saltando opcionales

### Changed
- **`@quinotospec.status`**: Integra artifact engine — muestra tabla de estado de artefactos (done/ready/blocked) por propuesta activa
- **`@quinotospec.init`**: Crea `schema.yaml` en la estructura inicial

---

## [2.2.0] - 2026-06-11

### Added
- **Delta Specs (ADDED/MODIFIED/REMOVED/RENAMED)**: Las propuestas ahora generan `delta-specs/` con formato de cambio incremental en lugar de especificaciones completas
- **Directorio `specs/`**: Source of truth canonico del sistema, organizado por dominio/servicio
- **Workflow `@quinotospec.specs-init`**: Inicializa `specs/` desde discovery, propuestas existentes o desde cero
- **Template `delta-spec-template.md`**: Template con secciones ADDED/MODIFIED/REMOVED/RENAMED y escenarios GIVEN/WHEN/THEN opcionales

### Changed
- **`@quinotospec.create-proposal`**: Genera `delta-specs/` con especificaciones incrementales; `proposal.md` ahora contiene resumen ejecutivo con referencias a delta-specs
- **`@quinotospec.archive`**: Ejecuta engine de merge de delta specs al archivar (ADDED→append, MODIFIED→replace, REMOVED→delete, RENAMED→rename) en `specs/`
- **`@quinotospec.init`**: Crea directorio `specs/` con README en la estructura inicial

### Compatibility
- **Coexistencia**: Propuestas sin `delta-specs/` se archivan normalmente sin merge de specs. Compatible hacia atras.

---

## [2.1.0] - 2026-03-21 - Berserker Edition

> Entrada documentada retroactivamente (backfill) — el release no registró changelog en su momento.

### Added
- **Battle Frenzy (Swarm Mode)** (`@quinotospec.battle-frenzy`): Ejecución paralela de múltiples agentes para tareas masivas, con skills de soporte `quinotospec-swarm-executor` y `quinotospec-swarm-task-splitter`
- **Blood-Bond mejorado**: Predicción proactiva con métricas avanzadas — skills separadas `quinotospec-blood-bond-analyzer`, `quinotospec-blood-bond-monitor` y `quinotospec-blood-bond-predictor`
- **Fix workflow** (`@quinotospec.fix`): Resolución de bugs y fixes menores sin propuesta formal

### Changed
- **Infrastructure**: Actualizados badges, versiones, conteos, AGENTS.md, install.sh

## [2.0.0] - 2026-04-15 - Possessed Edition

### Resumen
- Versión estable de producción con todas las features completadas
- Integración nativa con múltiples IDEs (OpenCode, Cursor, Cline)
- Sistema completo de workflows y skills para desarrollo asistido por IA

### Added
- **Mjolnir Refactor**: Capacidad de reescribir módulos enteros bajo demanda para limpiar deuda técnica
- **Code Review Workflow** (`@quinotospec.review`): Revisión de branches contra criterios de aceptación, tests y convenciones del stack
- **Sprint Planning Workflow** (`@quinotospec.sprint`): Generación de sprint plans con capacidad, prioridades y dependencias
  - Separado en 3 workflows: init, create, plan
- **Validate Skill** (`quinotospec-validate`): Checks de sistema reutilizables como precondición para workflows críticos
- **Refresh Discovery** (`@quinotospec.refresh-discovery`): Discovery incremental — detecta cambios y actualiza solo los archivos afectados
- **Dependency Graph** (`@quinotospec.dependency-graph`): Mapa de dependencias inter-servicio con detección de contract drift
- **Agent Train** (`@quinotospec.agent-train`): Asistencia para crear agentes abstractos especializados con sugerencias basadas en discovery
- **Blood-Bond**: Sistema de predicción proactiva de User Stories e intenciones
- **Stack Discovery** (`@quinotospec.stack-discovery`): Discovery consolidado para arquitecturas multi-servicio
- Soporte para **OpenCode** con parámetro `--opencode`
- Soporte para **Cursor** con parámetro `--cursor` (renombra workflows a commands)
- Soporte para **Cline** con parámetro `--cline`
- 19 skills especializadas incluyendo:
  - Generate GitHub Branch
  - File Creation
  - Stack Detect
  - Mark Done (con modos bulk y force)
  - Read PDF
  - Update Changelog
  - Rules Enforce
  - Metrics
  - Syntax Validate
  - Rollback
- 20 workflows automatizados para el flujo completo de desarrollo
- 9 agentes especializados pre-configurados
- Sistema de sprints con configuración base y por sprint
- Distribución de propuestas a microservicios
- Dashboard de estado del proyecto (`@quinotospec.status`)
- Documentación completa en AGENTS.md y README.md

### Changed
- Mejorado README.md con tabla de contenido completa
- Agregada sección de Ejemplo de Estructura de Proyecto
- Agregada Guía de Solución de Problemas
- Documentadas dependencias del instalador
- Corregido error tipográfico en reglas ("manualnente" → "manualmente")
- Agregada regla #3 de Verificación de Acuerdos de Producto

### Technical Details
- **Workflows**: 20 archivos en `agent-dist/workflows/`
- **Skills**: 19 skills en `agent-dist/skills/`
- **Rules**: 1 archivo de reglas globales en `agent-dist/rules/`
- **Install Script**: Soporte para múltiples IDEs con `install.sh`

---

## [1.0.0] - 2026-04-04 - Initial Release

### Resumen
- Versión inicial del paquete QuinotoSpec
- Framework básico de "Proposal First" / "Context Slicing"
- Estructura fundamental de directorios y workflows

### Added
- Flujo de trabajo básico: Discovery → Proposal → User Stories → Tasks → Apply
- Archivo AGENTS.md con guía técnica para agentes
- Script de instalación básico (`install.sh`)
- Estructura de `.quinoto-spec/` para proyectos objetivo
- Workflow de Discovery (`@quinotospec.discovery`)
- Workflow de Create Proposal (`@quinotospec.create-proposal`)
- Workflow de Create User Stories (`@quinotospec.create-user-stories`)
- Workflow de Create Tasks (`@quinotospec.create-tasks`)
- Workflow de Apply (`@quinotospec.apply`)
- Skill de Update Changelog
- Skill de Mark Done
- Sistema de prefix-registry para trazabilidad
- Convención de naming de branches
- Sistema de archivado con carpeta `_archived/`
- Licencia MIT

### Documentation
- README.md inicial con documentación de usuario
- AGENTS.md con instrucciones para agentes
- Estructura de descubrimiento de 8 archivos en `.quinoto-spec/discovery/`

---

## Versiones Futuras (Roadmap)

El roadmap vivo y único vive en [V3_ROADMAP.md](V3_ROADMAP.md) (plan v3.1.0 → v3.3.0: Fase 1 Engineering Fundamentals completada, Fase 2 Extensibility completada, Fase 3 Agents y Fase 4 Product). Esta sección ya no duplica su contenido para evitar planes divergentes.

---

## Notas de Versión

### Formato de Entrada (para agentes)
```markdown
## [Fecha: YYYY-MM-DD] - [Título de la Acción]
### Resumen
- detalle 1
- detalle 2
**Tiempo Ahorrado**: ~{Tiempo Humano} (IA: {Tiempo IA} vs Humano: {Tiempo Humano})
```

### Convención de Versiones
- **Major (X.0.0)**: Cambios breaking en la metodología o estructura
- **Minor (0.X.0)**: Nuevas features, workflows o skills
- **Patch (0.0.X)**: Correcciones de bugs, mejoras de documentación

### Enlaces
- [Documentación Principal](README.md)
- [Guía para Agentes](AGENTS.md)
- [Licencia MIT](LICENSE)
- [Repositorio GitHub](https://github.com/Quinoto-Tech/QuinotoSpec)
