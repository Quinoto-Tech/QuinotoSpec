---
date: 2026-11-13
prefix: QSPE-a7f3
slug: docs-playground-y-comandos-citados
type: feature
---

## [2026-11-13] - Playground de 5 minutos y guard de comandos citados

### Resumen
- **Guard nuevo**: `scripts/check-readme-commands.py` valida que todo `/quinotospec-*` y `/quinotospec.*` citado en README, `docs/` y `examples/` exista como skill o workflow. Hoy: 85 comandos en cada README + docs + examples, 0 muertos. Integrado a `validate-all.sh` (falla el gate) y cubierto por `tests/test-docs-consistency.sh` (7 checks, con fixture que prueba que detecta referencias muertas)
- **Playground completo**: `examples/python-fastapi` era el unico ejemplo con `.quinoto-spec/` pero tenia 2 de 8 archivos de discovery. Se generaron `02-overview`, `03-architecture`, `04-endpoints-and-openapi`, `05-data-and-services`, `06-devops-ci-security`, `07-findings-and-recommendations` y `08-product-and-agreements`, basados en el codigo real
- **Playground que se instala**: `requirements.txt` tenia pins de 2023 (`fastapi==0.104`, `pydantic==2.5`) sin wheels para Python 3.13+; `pip install` fallaba compilando `pydantic-core`. Pasa a rangos (`>=x,<y`) y se quitan `sqlalchemy`, `python-jose` y `passlib`, declaradas sin uso. Verificado en un venv con **Python 3.15**: instala y 5/5 tests verdes
- **Contrato de `/users` documentado**: las rutas de coleccion son `/users/` (barra final); `/users` responde 307 por `redirect_slashes` de Starlette. Los ejemplos de `curl` del discovery levantaban body vacio en un cliente sin redirects; corregidos
- **Job `example-playground` en CI**: instala las dependencias del ejemplo y corre `pytest` en Python 3.13, para que el README no vuelva a mandar a un playground roto
- **`examples/README.md`** (nuevo): indice de los 3 ejemplos, marcando cual es playground y como usarlo como base de un proyecto
- **Quick Start ES+EN**: seccion "Probalo en 5 minutos (sin instalar nada)" y aclaracion de que la barrera es proporcional al cambio (`fix` / `quick-dev` / propuesta completa). Paridad estructural intacta (code_blocks 27/27)

**Verificacion**: `validate-all --strict` 0 errores (links 109/109, parity OK, 0 comandos muertos), 28/28 suites, playground `pytest` 5/5 en Python 3.15, lint-shell limpio

**Tiempo Ahorrado**: ~5h (IA: ~1h30 vs Humano: ~5h de escribir 7 archivos de discovery + validar el playground a mano)
