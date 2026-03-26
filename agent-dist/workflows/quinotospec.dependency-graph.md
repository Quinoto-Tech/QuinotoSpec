---
description: Genera un mapa de dependencias inter-servicio y detecta contract drift entre los componentes del sistema distribuido
---

Este workflow analiza cómo los servicios del sistema se comunican entre sí, detecta dependencias ocultas y alerta sobre contratos de API inconsistentes.

**Precondición**: Todos los sub-proyectos deben tener su `*/.quinoto-spec/discovery/` actualizado. Ejecutar `quinotospec.stack-discovery` si es necesario.

---

## Paso 1 — Inventario de servicios

Escanea el root y lista todos los servicios con `/.quinoto-spec/discovery/`. Para cada uno, extrae de `03-endpoints-and-openapi.md` la lista de endpoints expuestos.

---

## Paso 2 — Detección de dependencias inter-servicio

Para cada servicio, analiza el código fuente buscando llamadas HTTP a otros servicios internos (fetch, axios, requests, httpx, etc.) o referencias a variables de entorno que apunten a URLs internas (ej. `API_URL`, `SERVICE_HOST`).

Construye la tabla de dependencias:

| Servicio Consumidor | Servicio Proveedor | Endpoint Consumido | Método | Hallado en |
| --- | --- | --- | --- | --- |
| [servicio-a] | [servicio-b] | `/api/users/{id}` | GET | `src/services/user.service.ts` |

---

## Paso 3 — Contract Drift Detection

Para cada dependencia identificada en el paso anterior:
1. Busca el endpoint consumido en el `03-endpoints-and-openapi.md` del servicio proveedor.
2. Compara el contrato esperado (método, parámetros, respuesta) contra lo que el consumidor asume.
3. Si hay discrepancia → marcar como `⚠️ CONTRACT DRIFT`.

Tabla de resultados:

| Consumidor | Proveedor | Endpoint | Estado | Detalle |
| --- | --- | --- | --- | --- |
| servicio-a | servicio-b | `GET /users/{id}` | ✅ OK | Contratos alineados |
| servicio-c | servicio-b | `POST /orders` | ⚠️ DRIFT | Consumidor envía `user_id`, proveedor espera `userId` |

---

## Paso 4 — Recursos y dependencias compartidas

Identifica recursos compartidos entre servicios:
- **Bases de datos**: ¿Más de un servicio escribe al mismo esquema/tabla?
- **Sistemas de auth**: ¿Qué servicios comparten el mismo JWT/token provider?
- **Message brokers / queues**: ¿Qué servicios publican/consumen de los mismos topics?

---

## Paso 5 — Generación del archivo de salida

Genera `.quinoto-spec/discovery/00-dependency-graph.md` con:

```markdown
# 🕸️ Dependency Graph — [Fecha]

## Mapa de dependencias (Mermaid)

​```mermaid
graph TD
  ServicioA -->|GET /users/{id}| ServicioB
  ServicioC -->|POST /orders| ServicioB
​```

## Tabla de dependencias
[tabla del paso 2]

## ⚠️ Contract Drift Detectado
[tabla del paso 3, solo las filas con DRIFT]

## Recursos Compartidos
[hallazgos del paso 4]

## Recomendaciones
- [Acción sugerida para cada DRIFT detectado]
```

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez completado, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Dependency Graph Generated
- **Resumen**: Se generó el mapa de dependencias en `.quinoto-spec/discovery/00-dependency-graph.md`. Contract drifts detectados: [N].
