# Changelog - QuinotoSpec

Todos los cambios notables en el paquete QuinotoSpec serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/), y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.5.0] - 2026-06-12

### Added
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

### [2.1.0] - Berserker Edition (TBA)
- **Battle Frenzy (Swarm Mode)**: Mejoras en ejecución de múltiples agentes en paralelo
- **Blood-Bond**: Predicción proactiva mejorada con métricas avanzadas

### [3.0.0] - Warband: Falange Edition (TBA)
- **Class System**: Roles de agentes especializados (Scout, Skald, Blacksmith)
- **Shield Wall**: Testing defensivo y validación cruzada entre agentes

### [4.0.0] - Warband: Hird Edition (TBA)
- **War Council**: Resolución de conflictos lógica y mediación estratégica
- **Alliance Integration (Multi-Repo)**: Contexto compartido federado

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
