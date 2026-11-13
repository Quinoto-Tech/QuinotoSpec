# 06 — DevOps, CI y seguridad

## Ejecucion local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload        # dev server + Swagger en /docs
pytest -v                            # suite
pytest --cov=app --cov-report=term-missing
```

## CI

Este ejemplo **no** trae workflow propio: el CI del repo (`QuinotoSpec`) valida el
paquete, no cada ejemplo. Existen `requirements.txt` y el `tests/` del ejemplo,
pero nada los corre automaticamente.

Si se copia este ejemplo como base de un proyecto real, el primer paso es agregar
un workflow propio (`pytest` en cada push) porque el gate del ejemplo no existe.

## Dependencias

- Rangos (`>=x,<y`) en `requirements.txt`, sin `pip-tools` ni lockfile con hashes.
- Solo dependencias usadas: se quitaron `sqlalchemy`, `python-jose` y `passlib`
  porque estaban declaradas sin uso (ver `07-findings`).
- Sin auditoria automatica de dependencias (no hay `pip-audit` ni Dependabot).

## Seguridad

| Tema | Estado |
|------|--------|
| Autenticacion | No implementada (fuera de alcance del ejemplo) |
| Autorizacion | No aplica |
| Validacion de entrada | pydantic en el body; `email` sin `EmailStr` |
| Secretos | Ninguno en el repo |
| CORS | No configurado (default de FastAPI) |
| Rate limiting | No implementado |

## Riesgos aceptados en una demo

Datos en memoria, sin auth y sin CORS son aceptables para un playground y **no**
deben copiarse a un proyecto productivo sin resolverlos.
