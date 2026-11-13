---
date: 2026-11-13
prefix: QSPE-a7f3
slug: discovery-executed
format: v2
type: change
---

## [2026-11-13] - Discovery Executed

### Resumen
- **Discovery ejecutado**: se exploró el repositorio completo (instalador, payload `agent-dist/`, scripts, tests, CI, UI, ejemplos y estado `.quinoto-spec/`) y se regeneraron los 8 archivos de especificación en `.quinoto-spec/discovery/`.
- **`01-stack-profile.md`**: stack real del paquete (Bash 4+, Python 3.8+ stdlib, JavaScript para plugins, sin framework ni gestor de paquetes), inventario 49 workflows / 95 skills / 9 agentes / 18 reglas / 13 templates, runners de test, linters, estándares de código y acoplamiento de versión 3.4.0.
- **`02-overview.md`**: resumen ejecutivo, estructura del repositorio, puntos de entrada, comandos de instalación/test/release, prerrequisitos y 8 riesgos principales.
- **`03-architecture.md`**: capas y módulos, patrones (adapter, staging transaccional, repository read-only, policy engine, configuración por capas, append-only), placeholder explícito para el runtime interno de cada IDE y diagramas de secuencia de UI, instalación y Apply con evidencia.
- **`04-endpoints-and-openapi.md`**: mapeo de las 19 rutas HTTP de la UI local, parámetros, errores, autenticación (inexistente), OpenAPI 3.1 mínimo validado y matriz de pruebas de integración.
- **`05-data-and-services.md`**: modelo de datos en sistema de archivos, entidades Proposal/Story/Task/Evidence/Approval/Spec/Changelog, diagrama ER, manifiestos de ownership y backup, estado global de la UI y ausencia de servicios externos de runtime.
- **`06-devops-ci-security.md`**: jobs de CI (matriz Ubuntu/macOS y Python 3.8/3.11/3.13), pipeline de release por tag, cron de entropía 06:00 UTC, revisión de seguridad, auditoría de dependencias y estrategia de backup/recuperación.
- **`07-findings-and-recommendations.md`**: 12 hallazgos priorizados con evidencia, owner y criterio de aceptación; roadmap corto/medio/largo; optimizaciones de rendimiento y checklist de accesibilidad.
- **`08-product-and-agreements.md`**: plantilla vacía para completar por humanos (Visión, KPIs, DoR y DoD), sin listas predefinidas. **Bloquea `create-proposal` hasta que se complete**, por la regla Product Agreement Check.
- **Verificación**: `scripts/validate-all.sh --strict` → 0 errores / 0 warnings; `tests/run-all-tests.sh` → 28/28 suites; `contract.py validate --strict` → `Valid: True`; `test-ui.sh` → 17/17 checks; playground FastAPI → 5/5 tests y 97% de cobertura.
- **Auditoría de dependencias**: paquete sin dependencias obligatorias; `pip-audit` detectó 1 advisory en `pytest 8.4.2` (PYSEC-2026-1845, fix 9.0.3) del ejemplo; `npm audit` detectó 6 vulnerabilidades `low` en la cadena dev de Jest; `cargo audit` no se ejecutó por falta de toolchain Rust.

**Tiempo Ahorrado**: ~6h (IA: ~35m vs Humano: ~6h de explorar el repo, ejecutar gates y redactar 8 documentos con diagramas)
