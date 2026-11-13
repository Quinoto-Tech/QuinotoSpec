# 08 — Producto y acuerdos (DoR / DoD)

## Vision

Demo minima de una API REST para mostrar el flujo QuinotoSpec de punta a punta
(discovery → propuesta → historias → tareas → changelog) sobre codigo real.

**Publico**: alguien que evalua QuinotoSpec y quiere ver un `.quinoto-spec/`
completo sin gastar tokens en un proyecto propio.

## Alcance

| Dentro | Fuera |
|--------|-------|
| CRUD basico de usuarios (listar, crear, obtener) | Update y delete |
| Validacion con pydantic | Autenticacion y autorizacion |
| Tests con `TestClient` | Base de datos real |
| `.quinoto-spec/` completo como ejemplo | CI del ejemplo, deploy |

## Definition of Ready (DoR)

Una tarea entra al pipeline si:

- [ ] Existe una propuesta aprobada con prefijo registrado en `prefix-registry.md`
- [ ] La historia de usuario tiene criterio de aceptacion verificable
- [ ] Se conoce el archivo o modulo a tocar
- [ ] El alcance no requiere una decision de producto abierta

## Definition of Done (DoD)

Una tarea se considera terminada cuando:

- [ ] `pytest -v` verde (sin tests nuevos fallando)
- [ ] El endpoint responde lo documentado en `04-endpoints-and-openapi.md`
- [ ] No se agregaron dependencias sin registrarlas en `05-data-and-services.md`
- [ ] Se actualizo el changelog v2 con la entrada correspondiente
- [ ] La propuesta quedo marcada como completada en `proposal.md`

## Acuerdos del ejemplo

- Los datos en memoria son un atajo **explicito**: no se reportan como bug.
- Cualquier feature nueva (auth, DB, delete) requiere propuesta nueva, no un
  parche sobre `users-api`.
- El ejemplo no se despliega: no hay entorno productivo que cuidar.

## Metricas de exito del playground

- Un usuario nuevo corre `uvicorn` + `pytest` en menos de 5 minutos.
- Puede leer el pipeline completo en `.quinoto-spec/` sin abrir el codigo.
