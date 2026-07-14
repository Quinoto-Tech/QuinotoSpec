# Guía para Agentes QuinotoSpec

Este es el paquete QuinotoSpec — una metodología y sistema de configuración de agentes para desarrollo asistido por IA. Los agentes operan en proyectos que usan QuinotoSpec siguiendo el flujo de trabajo "Proposal First" / "Context Slicing".

---

## 1. Comandos de Build, Lint y Test

Dado que este es un **paquete de configuración de agentes** (no una aplicación en tiempo de ejecución), los comandos tradicionales de build/test no aplican. Sin embargo, al trabajar en **proyectos objetivo** que usan QuinotoSpec:

### Comandos de Análisis de Proyecto
```bash
# Detectar stack del proyecto
/quinotospec-stack-detect

# Ejecutar discovery completo
/quinotospec.discovery

# Validar estado del sistema antes de workflows críticos
/quinotospec-validate --full
```

### Validación de Sintaxis
```bash
# Validar todos los archivos QuinotoSpec
/quinotospec-syntax-validate --type all

# Validar una propuesta específica
/quinotospec-syntax-validate --type proposal --slug <slug-name> --strict
```

### Ejecutar Tests en Proyectos Objetivo
```bash
# Leer el perfil de stack para encontrar el comando de test correcto
cat .quinoto-spec/discovery/01-stack-profile.md

# Patrones comunes: npm test, pytest, bundle exec rspec, go test ./..., cargo test
```

**Patrones para un solo test**: `npm test -- --testPathPattern=filename`, `pytest -k test_name`, `bundle exec rspec spec/path/to/spec.rb`, `go test -run TestName ./...`

---

## 2. Convenciones de Código

### Principios Fundamentales
- **Proposal First**: Siempre crear una propuesta técnica antes de escribir código
- **Context Slicing**: Discovery → Propuesta → User Stories → Tareas
- **Nunca editar archivos de especificación manualmente**: Usar skills como `quinotospec-update-changelog`
- **Toda edición del agente debe registrarse**: Después de cualquier cambio significativo, ejecutar `/quinotospec-update-changelog` para documentar la acción en el historial

### Convenciones de Nombrado de Archivos
- **Workflows**: `quinotospec.<workflow-name>.md`
- **Skills**: `quinotospec-<skill-name>/SKILL.md`
- **Rules**: `quinotospec-rules.md`
- **Scripts Temporales**: `.quinoto-spec/scripts/temp_*.{py,sh,js}` (NUNCA en raíz del proyecto)

### Convenciones de Nombrado de Branches (CRÍTICO)
```
feature/{{TASK_ID}}-descripcion-en-kebab-case
bugfix/{{TASK_ID}}-descripcion-en-kebab-case
```
Ejemplos: `feature/TSK-AUTH-001-add-login-endpoint`, `bugfix/US-ABC-123-fix-validation`

### Convención de Archivado
- Usar carpeta `_archived/` (NUNCA prefijo `__`)
- Estructura: `.quinoto-spec/proposals/{SLUG}/_archived/` para archivos

---

## 3. Flujo de Trabajo QuinotoSpec

### Ciclo Principal
```
1. Init (/quinotospec.init)                      → Inicializar estructura (nuevo proyecto)
2. Discovery (/quinotospec.discovery)             → Entender contexto del proyecto
3. Propuesta (/quinotospec.create-proposal)       → Definir solución técnica
4. User Stories (/quinotospec.create-user-stories) → Desglosar en stories de valor
5. Tareas (/quinotospec.create-tasks)             → Convertir en tareas atómicas
6. Aplicar (/quinotospec.apply)                   → Implementar tarea
7. Marcar Completado (/quinotospec-mark-done)     → Actualizar specs y archivar
```

### Workflows Complementarios
| Workflow | Propósito |
|----------|-----------|
| `/quinotospec.create-prd` | Product Requirements Document |
| `/quinotospec.create-rfc` | RFC interactivo con proposal seed. Soporta `--party` para debate multi-agente |
| `/quinotospec.review` | Revisar branch/PR contra criterios |
| `/quinotospec.archive` | Archivar propuestas completadas y mergear delta specs |
| `/quinotospec.status` | Dashboard de proyecto con estado DAG de artefactos |
| `/quinotospec.specs-init` | Inicializar specs/ con requerimientos del sistema |
| `/quinotospec.schema-fork` | Personalizar schema YAML del DAG de artefactos |
| `/quinotospec.party-mode` | Mesa redonda multi-agente — debate en caracter. Tambien invocable via `--party` en create-proposal y create-rfc |
| `/quinotospec.changelog-view` | Ver changelog consolidado (v2 + v1) con filtros |
| `/quinotospec.status` | Dashboard de proyecto |
| `/quinotospec.pre-commit` | Check pre-commit (test + validate + rules) |
| `/quinotospec.release` | Version bump, changelog, tagging |
| `/quinotospec.retrospective` | Retrospectiva con métricas y patrones |
| `/quinotospec.health` | Detectar archivos huérfanos e inconsistencias |
| `/quinotospec.cleanup` | Limpiar branches stale y scripts temporales |
| `/quinotospec.tiwaz-rune` | Análisis formal de entropía (Shannon v2 + proxies v1) con plan de remediación |

### Regla del Registro de Prefijos
- Cada propuesta necesita un prefijo único que combine un mnemónico de 4 letras + un sufijo de 4 caracteres (ej. `AUTH-a1b2`)
- Registrar en `.quinoto-spec/prefix-registry.md`
- NUNCA inventar prefijos que no estén en el registro o que no sigan el formato de idempotencia

### Verificación de Acuerdo de Producto (BLOQUEANTE)
Antes de `/quinotospec.create-proposal`:
1. Verificar `.quinoto-spec/discovery/08-product-and-agreements.md`
2. Si solo tiene placeholders o está vacío → DETENER y notificar al usuario para completar DoR/DoD

---

## 4. Manejo de Errores

- **Archivo de tarea faltante** → notificar al usuario y detener
- **ID de tarea no encontrado** → reportar error con sugerencias
- **Interrupciones de workflow** → guardar `ultimo_paso_completado` en YAML para reanudar
- **Fallos de validación** → usar `/quinotospec-validate --strict` para bloquear

---

## 5. Ubicaciones de Archivos QuinotoSpec

Una vez ejecutado el `/quinotospec.discovery`, los 8 archivos en `.quinoto-spec/discovery/` documentan exhaustivamente la naturaleza del proyecto: stack tecnológico, arquitectura, endpoints, modelos de datos, prácticas DevOps, deuda técnica y acuerdos de producto. Estos archivos constituyen la fuente autoritativa de contexto para cualquierAgent antes de proponer o implementar cambios.

```
.quinoto-spec/
├── discovery/                    # 8 archivos de especificación del proyecto
│   ├── 01-stack-profile.md       # Stack tecnológico, frameworks, test runners
│   ├── 02-overview.md            # Resumen ejecutivo, estructura de carpetas
│   ├── 03-architecture.md       # Diagrama de arquitectura, patrones de diseño
│   ├── 04-endpoints-and-openapi.md  # Endpoints REST/GraphQL, OpenAPI spec
│   ├── 05-data-and-services.md   # Modelos de datos, servicios externos
│   ├── 06-devops-ci-security.md  # CI/CD, auditoría de dependencias, seguridad
│   ├── 07-findings-and-recommendations.md  # Deuda técnica, vulnerabilidades
│   └── 08-product-and-agreements.md  # DoR/DoD, visión de producto
├── proposals/{DATE}-{slug}/       # Propuestas técnicas
│   ├── proposal.md
│   ├── user-stories.md
│   ├── {US_ID}_tasks.md
│   └── _archived/
├── prefix-registry.md            # Seguimiento de prefijos
├── changelog/                    # Historial auto-generado (v2: archivos individuales)
│   ├── YYYY-MM-DD-PREFIX-slug.md
│   └── INDEX.md                  # Tabla de contenido (gitignored, regenerable)
├── quinoto-spec-changelog.md     # Historial v1 legacy (opcional, backward compat)
├── scripts/                      # Scripts temporales (temp_*.py, etc.)
└── sprints/                      # Planificación de sprints
```

---

## 6. Gestión del Changelog (CRÍTICO)

QuinotoSpec soporta dos formatos de changelog:

### Formato v2 (recomendado, default)
Cada entrada es un archivo separado en `.quinoto-spec/changelog/YYYY-MM-DD-PREFIX-SLUG.md`:
- **Append-Only**: nunca genera merge conflicts en equipos multi-agente
- **INDEX.md** se regenera automáticamente (gitignored, nunca commiteado)
- Vista consolidada con `/quinotospec.changelog-view`

### Formato v1 (legacy)
Archivo único `.quinoto-spec/quinoto-spec-changelog.md`:
- Entradas ordenadas newest-first manualmente
- Usado para backward compatibility con proyectos pre-v2.5.0

### Reglas compartidas
- **NUNCA editar archivos de changelog manualmente**
- Siempre usar la skill `quinotospec-update-changelog` (auto-detecta formato)
- Para ver historial: `/quinotospec.changelog-view`

### Formato de Entrada (ambos formatos)
```markdown
## [Fecha: YYYY-MM-DD] - [Título de la Acción]
### Resumen
- detalle 1
- detalle 2
**Tiempo Ahorrado**: ~{Tiempo Humano} (IA: {Tiempo IA} vs Humano: {Tiempo Humano})
```

---

## 7. Archivos de Configuración Requiriendo Aprobación

Los siguientes archivos requieren **aprobación explícita del usuario** antes de modificar:
- `.quinoto-spec/sprints/base-config.yml`
- `.quinoto-spec/sprints/sprint-{ID}/sprint-config.yml`
- `.quinoto-spec/*/mjolnir-refactor.yml`

---

## 8. Referencia de Skills

### Skills Básicas
| Skill | Propósito |
|-------|-----------|
| `quinotospec-stack-detect` | Identificar stack tecnológico desde archivos de configuración |
| `quinotospec-validate` | Pre-flight checks para workflows críticos |
| `quinotospec-syntax-validate` | Validar estructura de archivos spec |
| `quinotospec-update-changelog` | Escribir en changelog |
| `quinotospec-entropy-calculator` | Calcular métricas de entropía (Shannon v2 + proxies v1) para Tiwaz Rune |
| `quinotospec-mark-done` | Completar tareas y archivar |
| `quinotospec-generate-github-branch` | Crear branches con nombres correctos |
| `quinotospec-file-creation` | Estandarizar creación de archivos y scripts temporales |
| `quinotospec-rollback` | Deshacer cambios de workflows fallidos |

### Skills de Gobernanza
| Skill | Propósito |
|-------|-----------|
| `quinotospec-rules-enforce` | Bloquear workflows que violen reglas |
| `quinotospec-metrics` | Métricas de compliance y productividad |

### Skills de Blood-Bond
| Skill | Propósito |
|-------|-----------|
| `quinotospec-blood-bond-analyzer` | Analizar patrones históricos del desarrollador |
| `quinotospec-blood-bond-monitor` | Detectar inactividad y activar predicción |
| `quinotospec-blood-bond-predictor` | Generar predicciones proactivas |

### Skills de Swarm (Battle Frenzy)
| Skill | Propósito |
|-------|-----------|
| `quinotospec-swarm-executor` | Ejecutar múltiples subagentes en paralelo |
| `quinotospec-swarm-task-splitter` | Dividir tareas masivas en chunks paralelizables |

### Skills de Specs y Artefactos
| Skill | Propósito |
|-------|-----------|
| `quinotospec-artifact-engine` | Computar estado DAG de artefactos (done/ready/blocked) |
| `quinotospec-party-orchestrator` | Orquestar mesas redondas multi-agente |

### Skills de Onboarding
| Skill | Propósito |
|-------|-----------|
| `quinotospec-onboard-developer` | Onboarding orientado a desarrolladores |
| `quinotospec-onboard-product` | Onboarding orientado a producto/negocio |
| `quinotospec-onboard-support` | Onboarding orientado a soporte/help desk |
| `quinotospec-onboard-general` | Onboarding con vista balanceada |
| `quinotospec-onboard-simple` | Onboarding en lenguaje simple sin jerga |

### Skills de Extensión
| Skill | Propósito |
|-------|-----------|
| `quinotospec-pre-commit` | Check pre-commit (test + validate + rules) |
| `quinotospec-suggest-next` | Sugerir siguiente tarea a ejecutar |
| `quinotospec-conflict-detector` | Detectar conflictos entre propuestas activas |
| `quinotospec-estimate` | Estimar complejidad de propuestas |

---

## 9. Frescura del Discovery

- Archivos de discovery mayores a **30 días** generan advertencia
- Usar `/quinotospec.refresh-discovery` para actualizar discovery obsoleto
- Siempre verificar fecha del discovery antes de crear propuestas
