# Stack Profile — python-fastapi (ejemplo)

- **Lenguaje**: Python 3.11+
- **Framework**: FastAPI (API REST)
- **Testing**: pytest + fastapi.testclient
- **Persistencia**: lista en memoria (demo; en produccion: SQLite + SQLAlchemy)
- **Comando de tests**: `pytest -v`
- **Servidor dev**: `uvicorn app.main:app --reload`

## Comandos rapidos

| Accion | Comando |
|--------|---------|
| Todos los tests | `pytest -v` |
| Un solo test | `pytest tests/test_users.py::test_create_user` |
| Servidor dev | `uvicorn app.main:app --reload` |
