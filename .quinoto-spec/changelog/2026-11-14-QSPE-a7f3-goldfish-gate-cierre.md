---
date: 2026-11-14
prefix: QSPE-a7f3
slug: goldfish-gate-cierre
format: v2
type: change
---

## [2026-11-14] - Goldfish gate obligatorio al cerrar tareas

### Resumen
- **`evidence_validate.py`**: nuevo kind `goldfish`. Exige `fresh_context: true`, lente `comprehension` presente, `comprehension.explained_scope: true`, veredicto `pass`, cero hallazgos `blocking` abiertos, `inputs` existentes y sin modificar después de `recorded_at` (revisión no stale) y frescura por `--max-age`.
- **`rules_enforce.py`**: el check `goldfish` se expone en `ALL_CHECKS` bajo la regla 16 ("Verificacion Antes de Completar"); con `--require-evidence` produce violación `evidence.invalid` si la evidencia falta o no valida, igual que `verify-before-done`.
- **`agent-dist/rules/quinotospec-rules.md`**: la regla 16 exige la pasada Goldfish antes de completar y prohíbe simularla con el mismo contexto. Sin nuevas secciones H1: el inventario sigue en 18 reglas.
- **`quinotospec-verify-before-done`**: el gate pasa de cinco a seis pasos (nuevo paso 4 Goldfish), con instrucción de revisión, esquema JSON de evidencia, comando de validación y filas nuevas en la tabla de fallos.
- **`quinotospec-mark-done`**: Paso 0 y modo bulk validan `verify-before-done.json` **y** `goldfish.json` antes de cambiar estados; `--skip-tests` no omite la evidencia Goldfish.
- **Documentación**: `README.md` y `README_EN.md` documentan el gate como obligatorio al cerrar (paridad estructural ES/EN conservada) y `docs/ADVANCED-USAGE.md` agrega el esquema completo del registro.
- **Tests**: `tests/test-goldfish-gate.py` (12 casos: evidencia válida, faltante, contexto reutilizado, alcance no explicado, hallazgo blocking abierto, veredicto != pass, lentes sin comprehension, input inexistente, input modificado tras la revisión, evidencia stale y dispatcher bloqueando/permitiendo); `test-rules-enforce.py` verifica el check diferido y `test-engineering-skills.sh` exige la sección Goldfish en la skill.
- **Verificación**: `scripts/validate-all.sh` → 0 errores / 0 warnings; suite `Goldfish Gate` 12/12; `contract.py validate --strict` OK.

**Tiempo Ahorrado**: ~3h (IA: ~25m vs Humano: ~3h de diseñar el esquema, escribir validador y dispatcher, actualizar 3 skills, docs bilingües y 12 tests)
