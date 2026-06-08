---
name: quinotospec-conflict-detector
description: Detecta conflictos y solapamientos de alcance entre una propuesta nueva y las propuestas activas existentes (mismos archivos, servicios, dominios o flujos).
---

# Skill: Conflict Detector

Analiza una propuesta nueva o en curso y detecta conflictos potenciales con otras propuestas activas en `.quinoto-spec/proposals/`. Útil antes de crear una propuesta o durante la planificación de sprints.

## Instrucciones de Ejecución

### Paso 1 - Recibir input

Recibir uno de:
- `--proposal-slug {{SLUG}}`: analiza una propuesta existente contra las demás
- `--proposal-description "{{DESCRIPCION}}"`: analiza una propuesta futura contra las activas (modo pre-creación)
- `--all`: analiza todas las propuestas activas entre sí (modo auditoría global)

### Paso 2 - Recolectar propuestas activas

1. Listar todas las carpetas en `.quinoto-spec/proposals/` (excluyendo `_archived/`)
2. Para cada propuesta activa, leer `proposal.md` y extraer:
   - **Servicios Afectados** (metadatos iniciales)
   - **Archivos nuevos/modificados** (sección "Impacto en el Sistema")
   - **Dominios/flujos** (sección "Arquitectura y Diseño Técnico")
   - **Prioridad** y **Estado**

### Paso 3 - Detectar conflictos

Comparar la propuesta objetivo contra cada propuesta activa (o todas contra todas en modo `--all`):

| Nivel | Condición | Severidad |
|-------|-----------|-----------|
| **CRÍTICO** | Mismos archivos Y mismo servicio | 🔴 Bloqueante |
| **ALTO** | Mismo servicio, archivos distintos | 🟠 Revisar orden |
| **MEDIO** | Mismos flujos/dominios, servicios distintos | 🟡 Coordinar |
| **BAJO** | Mismo tipo de cambio (ej. dos refactors) | 🟢 Informativo |

### Paso 4 - Generar reporte

Formato del reporte:

```
Conflict Detector — {{PROPOSAL_SLUG o "Análisis Global"}}
────────────────────────────────────────────────────────

🔴 CRÍTICOS ({{N}})
| Propuesta A | Propuesta B | Conflicto |
| auth-jwt    | auth-refresh | Archivo: auth-service/token.go |

🟠 ALTOS ({{N}})
| Propuesta A | Propuesta B | Conflicto |
| pay-v2      | pay-refund   | Servicio: payment-service |

🟡 MEDIOS ({{N}})
| Propuesta A | Propuesta B | Conflicto |
| notif-email | notif-push   | Dominio: notificaciones |

🟢 BAJOS ({{N}})
| Propuesta A | Propuesta B | Observación |
| refactor-db | refactor-api | Ambos son refactors |

────────────────────────────────────────────────────────
Total: {{N}} conflictos | {{CRITICAL_COUNT}} críticos
```

### Paso 5 - Recomendaciones

Si hay conflictos críticos o altos:
1. Sugerir orden de implementación (cuál primero, cuál después)
2. Si es posible, sugerir merge de propuestas que ataquen el mismo problema
3. Si hay conflicto de archivos, sugerir extraer el código compartido a un módulo común

## Modos y Flags

| Flag | Descripción |
|------|-------------|
| `--proposal-slug {{SLUG}}` | Analizar una propuesta específica contra las demás |
| `--proposal-description "..."` | Analizar una descripción de propuesta futura |
| `--all` | Analizar todas las propuestas entre sí |
| `--min-level {{NIVEL}}` | Filtrar por nivel mínimo (CRITICO, ALTO, MEDIO, BAJO) |
| `--json` | Output en formato JSON para consumo por otros skills |

## Ejemplos

```
@quinotospec-conflict-detector --proposal-slug auth-jwt
@quinotospec-conflict-detector --proposal-description "Agregar refresh token al auth-service"
@quinotospec-conflict-detector --all --min-level ALTO
@quinotospec-conflict-detector --all --json
```

## Integración

Esta skill es llamada automáticamente por:
- `@quinotospec.create-proposal`: antes de generar la propuesta, para documentar conflictos al inicio
- `@quinotospec.sprint.plan`: para evitar agendar propuestas conflictivas en el mismo sprint

## Notas

- Solo analiza propuestas en estado `🟡 Propuesta` o `🟢 En Progreso` (no `✅ Completada` ni archivadas)
- Si no hay discovery, advertir pero continuar (se pierde contexto de servicios/arquitectura)
- Los archivos se comparan por ruta relativa exacta
