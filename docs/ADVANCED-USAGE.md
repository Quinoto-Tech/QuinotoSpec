# Uso Avanzado de QuinotoSpec

## Multi-Servicio

Para proyectos con multiples servicios que se comunican entre si:

```bash
# 1. Discovery consolidado
@quinotospec.stack-discovery

# 2. Mapa de dependencias
@quinotospec.dependency-graph

# 3. Sincronizacion entre servicios
@quinotospec-sync --projects ../auth,../payments,../users --mode check
```

## Battle Frenzy (Ejecucion Paralela)

Para tareas masivas que se pueden paralelizar:

```bash
# Analizar que se puede paralelizar
@quinotospec.battle-frenzy --dry-run "Migrar 20 endpoints a v2"

# Ejecutar en paralelo
@quinotospec.battle-frenzy "Crear tests para todos los servicios"
```

## Blood-Bond (Prediccion Proactiva)

Blood-Bond analiza tus patrones de trabajo y predice acciones:

```bash
# Ver perfil de trabajo
@quinotospec.blood-bond --profile

# Obtener sugerencias
@quinotospec.blood-bond --suggest

# Ver alertas de inactividad
@quinotospec.blood-bond --alerts
```

## Sprint Planning

Planificacion completa de sprints:

```bash
# 1. Inicializar estructura
@quinotospec.sprints.init

# 2. Crear sprint
@quinotospec.sprint.create --name "Sprint 1" --start 2026-04-15 --end 2026-04-29

# 3. Generar plan optimo
@quinotospec.sprint.plan
```

## Heimdallr (Analisis de Seguridad)

Analisis de amenazas STRIDE + DREAD:

```bash
@quinotospec.heimdallr --system "API REST con autenticacion JWT, base de datos PostgreSQL, deploy en AWS"
```

Genera:
- Matriz de riesgos priorizada
- Activos criticos y limites de confianza
- Amenazas con mitigaciones accionables

## Mjolnir Refactor

Reescritura agresiva de modulos con alta deuda:

```bash
# 1. Identificar modulo candidato
@quinotospec.discovery (revisar 07-findings-and-recommendations.md)

# 2. Crear propuesta de refactor
@quinotospec.create-proposal (describir refactor)

# 3. Ejecutar refactor
@quinotospec.mjolnir-refactor
```

Nota: Segun Regla #10, se crea backup automatico antes del refactor.

## Export/Import para Integracion

### Exportar a Jira
```bash
@quinotospec.export --format jira-csv --output ./jira-import.csv
```

### Importar desde GitHub Issues
```bash
@quinotospec.import --source github-issues --repo owner/repo --label enhancement
```

## Personalizacion de Agentes

Crear agente personalizado:

```bash
@quinotospec.agent-train --model opencode-go/mimo-v2-pro --type subagent
```

El agente se crea en `.quinoto-spec/agents/` con configuracion adaptada al proyecto.

## Workflows Combinados

### Pipeline Completo de Feature
```bash
@quinotospec-validate --full                    # 1. Validar estado
@quinotospec.create-proposal                    # 2. Crear propuesta
@quinotospec.create-user-stories --slug {SLUG}  # 3. Generar stories
@quinotospec.create-tasks --slug {SLUG}         # 4. Generar tareas
@quinotospec.apply --task-id {TASK_ID}          # 5. Implementar
@quinotospec.review                             # 6. Revisar
@quinotospec.release                            # 7. Release
```

### Auditoria Completa
```bash
@quinotospec.health                             # 1. Detectar huerfanos
@quinotospec-validate --full                    # 2. Validar estado
@quinotospec.heimdallr --system "..."           # 3. Analizar seguridad
@quinotospec-metrics --dashboard                # 4. Ver metricas
```
