# Fix: create-proposal-discovery-sources
- **Fecha**: 2026-10-20 03:41
- **Descripción**: `quinotospec-create-proposal` solo ponía foco explícito en `01-stack-profile.md` y `08-product-and-agreements.md`; no mapeaba `02`–`07` a las secciones técnicas de la propuesta.
- **Comportamiento esperado**: antes de redactar, el agente lee el discovery técnico y cita hallazgos concretos (arquitectura, endpoints, datos, CI, deuda) en las secciones correspondientes.
- **Comportamiento actual (antes del fix)**: el agente leía `01` y `08`, generaba una propuesta genérica y nunca consultaba `03`/`04`/`05`/`06`/`07`.
- **Stack detectado**: paquete de configuración de agentes (Markdown + Bash + Python); test runner: `tests/run-all-tests.sh` vía `scripts/validate-all.sh`.

## Evidencia

**RED** (`bash tests/test-discovery-sources.sh`):
```
❌ .../quinotospec-create-proposal/SKILL.md: falta el bloque 'Lectura dirigida del Discovery'
❌ .../quinotospec.create-proposal.md: no referencia 04-endpoints-and-openapi.md como fuente de una sección
...
Resultados: 16 errores
exit=1
```

**GREEN**:
```
✅ agent-dist/skills/quinotospec-create-proposal/SKILL.md
✅ agent-dist/workflows/quinotospec.create-proposal.md
Resultados: 0 errores
exit=0
```

**Validación completa**: `bash scripts/validate-all.sh --allow-no-node` → 0 errors, 0 warnings; `bash tests/run-all-tests.sh` → 22 suites, 0 fallos.

## Riesgo
BAJO — cambio normativo en documentación de workflow + test de regresión. Sin impacto en runtime.
