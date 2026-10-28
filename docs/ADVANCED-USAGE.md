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

## Tiwaz Rune (Analisis de Entropia)

Analisis formal de entropia de codigo con metricas de Shannon (v2) y proxies de deuda tecnica (v1):

```bash
# Analisis completo de un microservicio
@quinotospec.tiwaz-rune --service ./services/payments

# Solo metricas formales (Shannon)
@quinotospec.tiwaz-rune --formal-only

# Solo metricas proxy (deuda tecnica)
@quinotospec.tiwaz-rune --proxy-only

# Output JSON estructurado
@quinotospec.tiwaz-rune --json

# Comparar con reporte anterior
@quinotospec.tiwaz-rune --baseline
```

**Fases del analisis:**
1. Metricas formales: entropia del grafo de dependencias, complejidad ciclomatica, distribucion de tamanos, churn y configuracion
2. Metricas proxy: complejidad, acoplamiento, configuracion, dependencias, seguridad, testing y observabilidad
3. Score compuesto: `S_final = 0.60 * H_total + 0.40 * S_proxy`
4. Plan de remediacion: acciones inmediatas, corto y mediano plazo

Genera:
- Reporte completo en `.quinoto-spec/tiwaz-rune/YYYYMMDD-hhmm-entropy-report.md`
- Integracion con discovery (`07-findings-and-recommendations.md`)
- Alertas criticas si `S_final >= 0.76`
- Sugerencias de remediacion (`mjolnir-refactor`, `create-proposal`)

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

## Handoff de Code Review a Humano

Cuando una propuesta esta completada (todas sus tareas corrieron), genera una guia autonoma para la persona que hara el code review:

```bash
@quinotospec.review-handoff 2026-09-24-add-login
@quinotospec.review-handoff 2026-09-24-add-login --output ./CODE_REVIEW.md   # copia adicional en la raiz
@quinotospec.review-handoff 2026-08-01-refactor-api --archived               # propuesta ya archivada
@quinotospec.review-handoff 2026-09-24-add-login --force --full-diff        # gap documentado + diff inline
```

La guia (`CODE_REVIEW_GUIDE.md` dentro de la propuesta) consolida en un solo archivo: resumen y alcance, criterios de aceptacion por story, tabla de tareas con archivos declarados, cambios en git (commits, diff stat, mapeo tarea a commits), historial del changelog del prefijo, evidencia de verificacion, delta specs, comandos para reproducir la verificacion y un checklist de revision listo para marcar.

Orden del ciclo: `apply` → `mark-done` → `review-handoff` → code review humano (feedback via `quinotospec-receive-review`) → `archive`.

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
@quinotospec.review-handoff {SLUG}              # 6. Guia de code review para el humano
@quinotospec.review                             # 7. Revisar
@quinotospec.release                            # 8. Release
```

### Auditoria Completa
```bash
@quinotospec.health                             # 1. Detectar huerfanos
@quinotospec-validate --full                    # 2. Validar estado
@quinotospec.heimdallr --system "..."           # 3. Analizar seguridad
@quinotospec-metrics --dashboard                # 4. Ver metricas
```
