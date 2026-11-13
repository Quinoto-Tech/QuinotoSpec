# Hallazgos y Recomendaciones: QuinotoSpec

Deuda técnica, riesgos, brechas de cobertura y seguridad, roadmap priorizado y checklist de seguimiento.

Guardar en: `.quinoto-spec/discovery/07-findings-and-recommendations.md`

**Discovery Date:** 2026-11-13
**Versión analizada:** 3.4.0 — *Warband: Hird Edition* (`beta-rc`)

## Resumen ejecutivo

El paquete está en buen estado operativo:

- `bash scripts/validate-all.sh --strict` → **0 errores, 0 warnings**.
- `bash tests/run-all-tests.sh` → **28/28 suites verdes**.
- `pip-audit` del ejemplo → **1 advisory en `pytest`**, dependencia de test.
- `npm audit` del ejemplo → **0 critical/high**, 6 low en la cadena de Jest.
- Sin secretos, sin dependencias obligatorias y con instalador transaccional.

Las brechas principales no son funcionales sino de **medición, cadena de suministro, endurecimiento de la UI y operación**:

1. No hay cobertura instrumentada del paquete.
2. La cadena de CI/assets no está fijada por hash ni firmada.
3. Las auditorías de dependencias no están automatizadas.
4. La UI local no tiene autenticación ni cabeceras de seguridad.
5. El gate de producto está bloqueado hasta completar `08-product-and-agreements.md`.
6. La recuperación multi-repo y los backups no están automatizados.

## Hallazgos priorizados

| ID | Hallazgo | Prioridad | Impacto | Esfuerzo | Owner sugerido |
|---|---|---|---|---|---|
| F-01 | Cobertura del paquete no medida ni bloqueante | 🔴 Alta | Regresiones no detectadas en código sin suite | M | `test-writer` / QA |
| F-02 | Cadena de suministro de CI y assets sin pinning/firma | 🔴 Alta | Riesgo de compromiso de Actions o asset vendorizado | M | `devops-engineer` / `security-auditor` |
| F-03 | Auditorías de dependencias fuera de CI | 🟠 Media | Vulnerabilidades nuevas pasan desapercibidas | S | `devops-engineer` |
| F-04 | UI local sin auth ni cabeceras de seguridad | 🟠 Media | Exposición de todo `.quinoto-spec/` si se publica el puerto | S | `security-auditor` / `architect` |
| F-05 | Acuerdos de producto vacíos bloquean propuestas | 🟠 Media | `create-proposal` se detiene por el gate de DoR/DoD | S | Product Owner |
| F-06 | Recuperación multi-repo y backups manuales | 🟠 Media | RTO/RPO indefinidos ante pérdida de datos | M | `devops-engineer` |
| F-07 | Contrato JSON de CLIs no versionado | 🟡 Baja | Agentes dependen de claves por convención | M | `architect` |
| F-08 | UI reconstruye todo el resumen por request | 🟡 Baja | Lentitud en proyectos grandes | S | `performance-optimizer` |
| F-09 | Estado compartido en `ThreadingHTTPServer` | 🟡 Baja | Condiciones de carrera en multi-proyecto concurrente | S | `architect` |
| F-10 | Accesibilidad de UI no verificada | 🟡 Baja | Barreras para teclado/lectores de pantalla | S | `doc-writer` / UI |
| F-11 | Ejemplos sin lockfile ni auditoría Rust en CI | 🟡 Baja | Reproducibilidad y cobertura de supply chain parcial | S | `devops-engineer` |
| F-12 | Artefactos `__pycache__` en el árbol de trabajo | 🟡 Baja | Ruido local; no versionados por `.gitignore` | XS | Cualquier dev |

Leyenda: 🔴 Alta = atender en el corto plazo; 🟠 Media = planificar; 🟡 Baja = mejora continua.

---

## F-01 — Cobertura del paquete no medida ni bloqueante

**Prioridad:** 🔴 Alta
**Owner:** `test-writer` / QA

### Evidencia

```bash
grep -rn 'coverage\|--cov' .github/workflows scripts tests
```

No hay job de cobertura para `agent-dist/`. La única cobertura disponible es la del playground:

```bash
cd examples/python-fastapi
pytest --cov=app --cov-report=term
```

```text
Name                     Stmts   Miss  Cover
app/main.py                 10      0   100%
app/models.py                3      0   100%
app/routes/users.py         18      1    94%
TOTAL                       31      1    97%
```

Ese **97% corresponde al ejemplo**, no al paquete. Las 28 suites verifican comportamiento, pero no informan qué líneas de `agent-dist/` quedan sin ejecutar.

### Impacto

- Regresiones en ramas de error de `install.sh`, `backup.py`, `contract.py`, `rules_enforce.py` o la UI pueden pasar si no hay un test específico.
- No se puede fijar un umbral de calidad objetivo para releases.

### Recomendación

1. Instrumentar `coverage.py` sobre las suites Python y sobre los subprocess de los scripts.
2. Emitir `coverage.xml` y un resumen en CI.
3. Fijar un umbral inicial alcanzable (por ejemplo 70% de líneas en `agent-dist/lib`, `agent-dist/ui` y validadores) y subirlo por release.
4. Añadir cobertura de ramas para `install.sh` usando `bash -x` o tests E2E con escenarios de fallo.

### Criterio de aceptación

```bash
coverage run -m unittest discover -s tests -p 'test_*.py'
coverage report --fail-under=70
```

- [ ] Job de cobertura en CI.
- [ ] Umbral documentado en `CONTRIBUTING.md`.
- [ ] Reporte publicado como artefacto del workflow.

---

## F-02 — Cadena de suministro de CI y assets sin pinning/firma

**Prioridad:** 🔴 Alta
**Owner:** `devops-engineer` / `security-auditor`

### Evidencia

```bash
grep -n 'uses:' .github/workflows/*.yml
```

Acciones referenciadas por tag mayor:

- `actions/checkout@v7`
- `actions/setup-python@v7`
- `softprops/action-gh-release@v3`

Asset vendorizado:

```bash
ls -lh agent-dist/ui/static/mermaid.min.js
# ~3.2 MB
```

El release publica `.tar.gz` + `.sha256`, pero **no firma** ni publica procedencia.

### Impacto

- Un tag móvil comprometido puede ejecutar código en CI con acceso al repositorio.
- Un asset vendorizado sin versión/hash documentado es difícil de auditar.
- Un checksum sin firma no protege contra un atacante que reemplaza ambos artefactos.

### Recomendación

1. Fijar cada Action por SHA completo y dejar el tag en comentario.
2. Activar Dependabot o Renovate para actualizar SHAs.
3. Documentar versión, licencia y SHA-256 de `mermaid.min.js`; verificar el hash en CI.
4. Firmar releases con Sigstore/cosign o GPG y publicar `*.sig`/`*.pem`.
5. Evaluar `npm`/`pip` provenance si se publica en registros.

### Criterio de aceptación

- [ ] Todas las Actions fijadas por SHA.
- [ ] Hash de `mermaid.min.js` verificado en `validate-all.sh`.
- [ ] Release con firma y verificación documentada.

---

## F-03 — Auditorías de dependencias fuera de CI

**Prioridad:** 🟠 Media
**Owner:** `devops-engineer`

### Evidencia y resultados

Paquete: **sin dependencias obligatorias**.

Ejemplo Python:

```bash
pip-audit -r examples/python-fastapi/requirements.txt
```

```text
pytest 8.4.2 — PYSEC-2026-1845 — fix 9.0.3
```

Ejemplo Node (lock temporal):

```bash
npm audit
```

```text
6 low severity vulnerabilities
deepmerge — prototype poisoning — transitiva de jest-config
```

Ejemplo Rust: `cargo audit` no ejecutado (toolchain ausente).

### Impacto

- Las dependencias de ejemplo son la primera experiencia del usuario; una vulnerabilidad alta rompería la confianza.
- Sin job automatizado, una regresión de dependencias solo se descubre manualmente.

### Recomendación

1. Añadir jobs `dependency-audit-python`, `dependency-audit-node` y `dependency-audit-rust` a `ci.yml`.
2. Fallar en `high`/`critical`; reportar `low`/`moderate` sin bloquear.
3. Actualizar el rango de `pytest` del ejemplo a `>=9.0.3,<10` cuando sea compatible.
4. Versionar `package-lock.json` del ejemplo Node o generar el lock en CI antes de auditar.
5. Ejecutar `cargo audit` en CI.

### Criterio de aceptación

- [ ] `pip-audit` en CI.
- [ ] `npm audit --audit-level=high` en CI.
- [ ] `cargo audit` en CI.
- [ ] Dependencias del ejemplo sin advisories altas/críticas.

---

## F-04 — UI local sin auth ni cabeceras de seguridad

**Prioridad:** 🟠 Media
**Owner:** `security-auditor` / `architect`

### Evidencia

`agent-dist/ui/server.py`:

```python
def _send(self, status, body, content_type="text/html; charset=utf-8"):
    ...
    self.send_header("Content-Type", content_type)
    self.send_header("Content-Length", str(len(payload)))
    self.send_header("Cache-Control", "no-store")
```

No se emiten:

- `Content-Security-Policy`
- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Permissions-Policy`

No hay autenticación. El binding por defecto es `127.0.0.1`, pero `--host` permite `0.0.0.0`.

### Impacto

- Si el usuario publica el puerto, cualquiera en la red puede leer propuestas, specs, evidencia y changelog.
- Sin CSP, un Markdown malicioso o un asset comprometido tiene más margen de ejecución.
- Sin `X-Frame-Options`, la UI puede embeberse en un iframe.

### Recomendación

1. Advertir y pedir confirmación si `--host` no es loopback.
2. Añadir cabeceras de seguridad en `_send()`.
3. Servir Mermaid con CSP compatible (sin `unsafe-eval` si la versión lo permite).
4. Documentar que la UI no es multiusuario ni remota.
5. Evaluar token local efímero si se quiere defensa en profundidad.

### Criterio de aceptación

- [ ] Cabeceras de seguridad presentes en todas las respuestas.
- [ ] Test que verifique `Content-Security-Policy` y `X-Content-Type-Options`.
- [ ] Advertencia/bloqueo con `--host 0.0.0.0`.

---

## F-05 — Acuerdos de producto vacíos bloquean propuestas

**Prioridad:** 🟠 Media
**Owner:** Product Owner / maintainer

### Evidencia

`08-product-and-agreements.md` es una plantilla vacía por instrucción del workflow de discovery. La regla **Product Agreement Check (BLOQUEANTE)** y `create-proposal` detienen la ejecución si el archivo no tiene DoR/DoD reales.

Además, `quinotospec-help` recomienda `/quinotospec.create-proposal` en este estado sin comprobar el gate de producto: la recomendación es correcta como “siguiente paso del flujo”, pero el comando se bloqueará hasta completar `08`.

### Impacto

- El siguiente `@quinotospec.create-proposal` fallará hasta que un humano complete el archivo.
- Es un bloqueo **intencional**, no un bug, pero debe comunicarse.

### Recomendación

1. Completar `Visión de Producto`, `Business Goals/KPIs`, `DoR` y `DoD`.
2. Revisar y aprobar los acuerdos en equipo.
3. Versionar el archivo y actualizarlo cuando cambie el producto.
4. Si se necesita una excepción, documentarla en `proposal.md` bajo `**⚠️ Excepción DoR/DoD:**`.

### Criterio de aceptación

- [ ] `08-product-and-agreements.md` con contenido sustantivo.
- [ ] `contract.py validate --root . --strict` sigue en verde.
- [ ] `create-proposal` puede ejecutarse sin override.

---

## F-06 — Recuperación multi-repo y backups manuales

**Prioridad:** 🟠 Media
**Owner:** `devops-engineer`

### Evidencia

- `backup.py` implementa create/verify/list/restore/cleanup con SHA-256.
- No hay workflow de backup programado.
- `bifrost.py --backup` genera un `tar.gz` federado; el restore es manual.
- No hay prueba E2E de restore completo en CI.

### Impacto

- RTO/RPO no definidos.
- Pérdida de un repo federado requiere intervención manual.
- Un backup no probado no es un backup confiable.

### Recomendación

1. Programar backups (cron local o workflow) con retención.
2. Añadir un smoke test de restore completo en CI usando un sandbox.
3. Documentar runbook de recuperación multi-repo.
4. Definir RTO/RPO y responsable.
5. Evaluar cifrado del store de backups si contiene datos sensibles.

### Criterio de aceptación

- [ ] Backup automático con retención.
- [ ] Test de restore completo en CI.
- [ ] Runbook publicado en `docs/`.

---

## F-07 — Contrato JSON de CLIs no versionado

**Prioridad:** 🟡 Baja
**Owner:** `architect`

### Evidencia

Los scripts con `--json` emiten formas distintas. Ejemplos:

- `contract.py` devuelve errores con código/severidad/ruta/línea.
- `rules_enforce.py` devuelve checks y veredicto.
- `search.py` devuelve `schema_version` y resultados.
- `update_agents.py` devuelve un diff/estado.

No hay un JSON Schema común ni un test que valide claves obligatorias.

### Impacto

- Un cambio de clave puede romper workflows o agentes sin que un test lo detecte.
- Los consumidores dependen de convenciones no escritas.

### Recomendación

1. Definir un envelope común (`schema_version`, `ok`, `errors`, `warnings`, `data`).
2. Publicar JSON Schemas por comando.
3. Añadir tests de contrato para cada `--json`.
4. Versionar cambios incompatibles.

### Criterio de aceptación

- [ ] Schemas en `docs/` o `agent-dist/schemas/`.
- [ ] Tests que validen el envelope.
- [ ] Guía de compatibilidad para consumidores.

---

## F-08 — UI reconstruye todo el resumen por request

**Prioridad:** 🟡 Baja
**Owner:** `performance-optimizer`

### Evidencia

`State.refresh()` llama a `readers.build_summary()` en cada request. `build_summary()` recorre discovery, propuestas, tareas, specs, evidencia y changelog. No hay caché ni invalidación por mtime.

### Impacto

- En proyectos con cientos de propuestas/archivos, cada navegación puede tardar más de lo deseable.
- El costo se multiplica en modo multi-root.

### Recomendación

1. Cachear por `(root, mtime máximo)` o usar `watchdog`/polling ligero.
2. Separar endpoints JSON de páginas HTML para permitir cache.
3. Medir con un proyecto sintético de 100 propuestas.
4. Mantener la UI por debajo de 2s en localhost (principio `PERF-01`).

### Criterio de aceptación

- [ ] Benchmark documentado.
- [ ] Caché con invalidación correcta.
- [ ] Test de rendimiento en CI o script reproducible.

---

## F-09 — Estado compartido en `ThreadingHTTPServer`

**Prioridad:** 🟡 Baja
**Owner:** `architect`

### Evidencia

```python
class State:
    roots = []
    root = Path(".")
    summaries = []
    summary = None
```

`ThreadingHTTPServer` atiende requests concurrentes y `State.refresh()` muta atributos de clase.

### Impacto

- Dos requests con `?project=` distinto pueden pisarse el estado.
- En uso local monousuario es poco probable, pero es una bomba de tiempo si se expone.

### Recomendación

1. Crear una instancia de estado por request o usar `threading.local`.
2. Añadir un lock si se mantiene caché compartida.
3. Test de concurrencia con dos proyectos.

### Criterio de aceptación

- [ ] Sin atributos mutables de clase para estado de request.
- [ ] Test concurrente multi-root.

---

## F-10 — Accesibilidad de UI no verificada

**Prioridad:** 🟡 Baja
**Owner:** `doc-writer` / UI

### Evidencia

No hay tests de accesibilidad ni auditoría con axe/Lighthouse. La UI usa HTML server-side, tema claro/oscuro y Mermaid.

### Impacto

- Posibles barreras de teclado, contraste o etiquetas ARIA.
- Mermaid puede no ser accesible sin texto alternativo.

### Recomendación

1. Ejecutar `axe-core` o Lighthouse en las páginas principales.
2. Verificar navegación por teclado y foco visible.
3. Añadir `aria-label` a controles y `alt`/descripción a diagramas.
4. Respetar `prefers-reduced-motion` y `prefers-color-scheme`.

### Criterio de aceptación

- [ ] Auditoría sin errores críticos.
- [ ] Checklist de accesibilidad en `CONTRIBUTING.md`.

---

## F-11 — Ejemplos sin lockfile ni auditoría Rust en CI

**Prioridad:** 🟡 Baja
**Owner:** `devops-engineer`

### Evidencia

- `examples/node-express` no tiene `package-lock.json`.
- `examples/rust-axum` no se compila ni audita en CI.
- El job `example-playground` solo cubre Python.

### Impacto

- El ejemplo Node no es reproducible bit a bit.
- El ejemplo Rust puede romperse sin que CI lo detecte.

### Recomendación

1. Versionar `package-lock.json`.
2. Añadir jobs de build/test para Node y Rust.
3. Añadir `cargo audit` y `npm audit`.
4. Mantener los ejemplos alineados con el README.

### Criterio de aceptación

- [ ] Lockfile versionado.
- [ ] Jobs de ejemplo Node/Rust en CI.
- [ ] Auditorías en verde.

---

## F-12 — Artefactos `__pycache__` en el árbol de trabajo

**Prioridad:** 🟡 Baja
**Owner:** Cualquier dev

### Evidencia

```bash
find . -name '*.pyc' -not -path './.git/*' | head
```

Hay `.pyc` en `agent-dist/` y `examples/`. `.gitignore` los excluye (`__pycache__/`, `*.pyc`), por lo que **no están versionados**, pero ocupan espacio y confunden búsquedas.

### Impacto

- Ruido en herramientas de búsqueda y empaquetado.
- Riesgo de incluir binarios en un tarball si se cambia el filtro.

### Recomendación

1. Ejecutar `find . -name '__pycache__' -type d -prune -exec rm -rf {} +` antes de empaquetar.
2. Usar `python3 -B` en scripts y tests (ya se hace en muchos).
3. Verificar que `package-release.sh` los excluya.

### Criterio de aceptación

- [ ] Tarball sin `.pyc`.
- [ ] Script de limpieza documentado.

---

## Hallazgos históricos ya corregidos

| Hallazgo previo | Estado actual | Evidencia |
|---|---|---|
| Plugin OpenCode v2 incompatible con el runtime | ✅ Corregido | `agent-dist/plugins/opencode-v2/index.js` con hooks `context`/`compaction`; `test-bootstrap.sh` lo prueba |
| `AGENTS.md` global en ruta incorrecta | ✅ Corregido | `get_agents_root()` usa el directorio del IDE; `test-install-e2e.sh` cubre global por IDE |
| Suites de test sin auto-descubrimiento | ✅ Corregido | `run-all-tests.sh` detecta suites huérfanas |
| Jormungandr con fallback falso | ✅ Corregido | Kahn real sobre YAML inline y multilínea; `test-nordic-skills.sh` |
| Drift de versión entre archivos | ✅ Mitigado | `validate-all.sh` y `release.yml` verifican 4 fuentes + docs |
| Referencias muertas en documentación | ✅ Mitigado | `check-readme-commands.py` y `check-links.sh` en el gate |

## Roadmap de mejoras

### Corto plazo (0–2 semanas)

| Acción | Owner | Prioridad |
|---|---|---|
| Completar `08-product-and-agreements.md` | Product Owner | 🔴 Alta |
| Añadir cabeceras de seguridad y advertencia de `--host` | Security / Architect | 🟠 Media |
| Añadir jobs de auditoría de dependencias | DevOps | 🟠 Media |
| Fijar Actions por SHA y documentar hash de Mermaid | DevOps | 🔴 Alta |
| Instrumentar cobertura inicial del paquete | QA / Test Writer | 🔴 Alta |

### Medio plazo (1–2 meses)

| Acción | Owner | Prioridad |
|---|---|---|
| Umbral de cobertura en CI y reporte por release | QA | 🔴 Alta |
| Firmar releases y publicar procedencia | DevOps | 🟠 Media |
| Backup programado + test de restore completo | DevOps | 🟠 Media |
| Envelope JSON versionado para CLIs | Architect | 🟡 Baja |
| Benchmark y caché de UI | Performance | 🟡 Baja |

### Largo plazo (trimestre)

| Acción | Owner | Prioridad |
|---|---|---|
| Runbook de recuperación multi-repo (Bifrost) | DevOps | 🟠 Media |
| Auditoría de accesibilidad y plan de remediación | UI / Docs | 🟡 Baja |
| Jobs de ejemplo Node/Rust y lockfiles | DevOps | 🟡 Baja |
| Endurecimiento opcional de UI (token local, CSP estricta) | Security | 🟡 Baja |
| Revisión de modelo de amenazas con STRIDE/DREAD | Security | 🟡 Baja |

## Optimizaciones de rendimiento

| Oportunidad | Impacto | Esfuerzo |
|---|---|---|
| Cachear `build_summary()` por mtime | Alto en proyectos grandes | M |
| Evitar reconstruir todas las propuestas para `/proposals` | Medio | S |
| Cargar Mermaid solo en páginas con bloques `mermaid` | Medio | S |
| Servir JSON y HTML desde el mismo resumen cacheado | Medio | S |
| Compresión HTTP (`gzip`) para HTML/JSON | Bajo/Medio | S |
| Índice Mimir incremental en vez de completo | Medio | M |

## Accesibilidad

- [ ] Navegación completa por teclado.
- [ ] Foco visible en enlaces y botones.
- [ ] Contraste AA en tema claro y oscuro.
- [ ] `aria-label` en navegación y controles.
- [ ] Texto alternativo/descripción para diagramas Mermaid.
- [ ] Respeto de `prefers-reduced-motion`.
- [ ] Formularios de búsqueda con `label` asociado.
- [ ] Mensajes de error y vacío anunciados a lectores de pantalla.

## Checklist de seguimiento

| Ítem | Owner | Estado | Verificación |
|---|---|---|---|
| F-01 Cobertura | QA / test-writer | ⬜ Pendiente | `coverage report --fail-under=70` |
| F-02 Supply chain | DevOps / Security | ⬜ Pendiente | Actions por SHA + hash Mermaid |
| F-03 Auditorías | DevOps | ⬜ Pendiente | Jobs en CI |
| F-04 UI hardening | Security / Architect | ⬜ Pendiente | Cabeceras + test |
| F-05 Acuerdos | Product Owner | ⬜ Pendiente | `08` completo |
| F-06 DR | DevOps | ⬜ Pendiente | Backup + restore E2E |
| F-07 JSON contract | Architect | ⬜ Pendiente | Schemas + tests |
| F-08 UI perf | Performance | ⬜ Pendiente | Benchmark |
| F-09 Concurrencia UI | Architect | ⬜ Pendiente | Test concurrente |
| F-10 Accesibilidad | UI / Docs | ⬜ Pendiente | Auditoría axe |
| F-11 Ejemplos | DevOps | ⬜ Pendiente | Jobs Node/Rust |
| F-12 Pycache | Dev | ⬜ Pendiente | Tarball limpio |

## Evidencia de verificación de este discovery

```text
bash scripts/validate-all.sh --strict
→ Results: 0 errors, 0 warnings
→ All validations passed

bash tests/run-all-tests.sh
→ Total: 28 suites
→ ✅ Pas: 28
→ ❌ Fail: 0

pip-audit -r examples/python-fastapi/requirements.txt
→ 1 paquete afectado: pytest 8.4.2 (PYSEC-2026-1845, fix 9.0.3)

npm audit (lock temporal del ejemplo)
→ 6 low, 0 moderate, 0 high, 0 critical

python3 -B examples/python-fastapi -m pytest --cov=app
→ 5 passed, cobertura 97%
```

## Datos que requieren ejecución o permisos

| Dato faltante | Comando | Permiso |
|---|---|---|
| Cobertura real de `agent-dist/` | Instrumentar `coverage.py` y ejecutar suites | Dependencia de desarrollo |
| Auditoría Rust | `cargo install cargo-audit && cargo audit` | Toolchain Rust + red |
| Comportamiento real en cada IDE | Instalar y abrir sesión en OpenCode/Cursor/Claude/Cline | Escritura en `$HOME` + reinicio |
| Prueba de carga de UI | `ab`/`hey` sobre el servidor | Herramienta externa |
| Auditoría de accesibilidad | `axe-core`, Lighthouse, lector de pantalla | Navegador y herramientas |
| Firma de release | `cosign`/GPG | Clave y permisos de release |

## 🔗 Referencias

- `01-stack-profile.md` — stack y pruebas
- `04-endpoints-and-openapi.md` — superficie HTTP
- `06-devops-ci-security.md` — CI, seguridad y auditorías
- `docs/IMPROVEMENTS-BACKLOG.md` — backlog histórico (M1–M8 implementados)
- `docs/ARCHITECTURE.md` — matriz de madurez
