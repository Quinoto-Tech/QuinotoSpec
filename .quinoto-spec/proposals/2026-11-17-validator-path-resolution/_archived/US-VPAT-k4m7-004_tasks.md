# Plan de Tareas (Validator Path Resolution — US-VPAT-k4m7-004)

**Proposal ID:** 2026-11-17-validator-path-resolution
**Prefijo:** VPAT-k4m7
**Estado:** proposed

| ID | Tipo | Título | Descripción | Historia Relacionada | Servicio | Archivos a Modificar | Estimación | Prioridad | Dependencias | Estado |
|---|---|---|---|---|---|---|---|---|---|---|
| TSK-VPAT-k4m7-007 | Backend | Fallback en `update_agents.py` | Añadir `resolve_package_root(user_root)` (devuelve `user_root/agent-dist` si existe; si no `Path(__file__).resolve().parents[2]`, convención de `agent-dist/lib/quinotospec_common.py:55`) y aplicarlo a las resoluciones de `workflows`, `skills`, `rules`, `templates` (líneas 70, 88, 95, 195-196). `--root` del usuario sigue operando sobre el proyecto. GREEN de TSK-002 para este script. | US-VPAT-k4m7-004 | payload-python | agent-dist/skills/quinotospec-update-agents/update_agents.py, tests/test-installed-paths.sh | S | P1 | TSK-VPAT-k4m7-002 | [x] |
| TSK-VPAT-k4m7-008 | Backend | Fallback en `template_resolver.py` + regresión cero en fuente | Aplicar el mismo helper a la resolución core de skills (`template_resolver.py:97`). Regresión: en el repo fuente el comportamiento es idéntico al actual (suite compara salida pre/post en fixture del source). | US-VPAT-k4m7-004 | payload-python | agent-dist/skills/quinotospec-template-resolver/template_resolver.py, tests/test-installed-paths.sh | XS | P1 | TSK-VPAT-k4m7-007 | [x] |
