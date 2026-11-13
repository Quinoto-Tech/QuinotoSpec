# Ejemplos

Tres proyectos de referencia. Solo `python-fastapi` es **playground**: trae el
`.quinoto-spec/` completo (discovery de 8 archivos, propuesta, historias, tareas
y changelog). Los otros dos muestran como se ve el stack, sin pipeline generado.

| Ejemplo | Stack | `.quinoto-spec/` | Para que sirve |
|---------|-------|------------------|----------------|
| [`python-fastapi`](python-fastapi/README.md) | Python 3.11+ · FastAPI · pytest | **Completo** | Playground: ver el pipeline real y probar `@quinotospec.help` |
| [`node-express`](node-express/README.md) | Node.js · Express | No | Referencia de stack para proyecto JS/TS |
| [`rust-axum`](rust-axum/README.md) | Rust · Axum | No | Referencia de stack para proyecto Rust |

## Empezar por el playground

```bash
cd python-fastapi
pip install -r requirements.txt
pytest -v
uvicorn app.main:app --reload
```

Despues lee, en este orden:

1. `.quinoto-spec/discovery/01-stack-profile.md` — que contexto se genera
2. `.quinoto-spec/proposals/users-api/proposal.md` — como se define el alcance
3. `.quinoto-spec/changelog/` — como queda registrada la entrega

Detalle completo en el [README del playground](python-fastapi/README.md).

## Usar un ejemplo como base de tu proyecto

```bash
cp -r examples/python-fastapi ../mi-proyecto
cd ../mi-proyecto
rm -rf .quinoto-spec      # opcional: queres tu propio pipeline, no el de la demo
@quinotospec.discovery
```

Los ejemplos se empaquetan con el release (`scripts/package-release.sh`), asi que
sirven como referencia offline.
