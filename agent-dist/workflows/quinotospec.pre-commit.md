---
description: Check rápido pre-commit que ejecuta tests del stack + validación de sintaxis + enforcement de reglas
---

# Workflow: Pre Commit

Objetivo: ejecutar una verificación pre-commit rápida antes de hacer push o crear un PR. No reemplaza CI completo, pero detecta problemas comunes antes de que lleguen al repo.

## Instrucciones

### Paso 1 - Ejecutar tests del stack

1. Leer `.quinoto-spec/discovery/01-stack-profile.md` para identificar el comando de test del proyecto.
2. Ejecutar el comando de test. Si falla, reportar los tests rotos y detener el workflow.
3. Si no hay discovery o el comando de test no está definido, mostrar advertencia y continuar.

### Paso 2 - Validar sintaxis QuinotoSpec

1. Ejecutar `quinotospec-syntax-validate --type all`.
2. Si hay errores de sintaxis, listarlos. No bloquear el commit, pero advertir.

### Paso 3 - Enforce rules

1. Ejecutar `quinotospec-rules-enforce` en modo `warning` (no `strict`).
2. Si se detectan violaciones de reglas, listarlas como advertencias.

### Paso 4 - Resumen

Mostrar un resumen con el formato:

```
Pre-commit Check ─────────────────────────────
Tests:            ✅ pasaron / ❌ fallaron / ⚠️ no configurados
Sintaxis:         ✅ OK / ⚠️ {N} advertencias
Reglas:           ✅ OK / ⚠️ {N} violaciones
──────────────────────────────────────────────
```

Si los tests fallaron, recomendar no hacer commit hasta que pasen.
Si solo hay advertencias de sintaxis o reglas, el commit puede proceder.

## Modos

- **Default**: Ejecuta los 3 pasos completos.
- **`--quick`**: Solo ejecuta tests (saltea validación de sintaxis y reglas). Útil cuando los archivos QuinotoSpec no cambiaron.
- **`--skip-tests`**: Saltea tests del stack. Útil cuando solo se modificaron archivos de documentación o configuración.

## Precondiciones

- `.quinoto-spec/discovery/` debe existir (ejecutar `@quinotospec.discovery` primero).
- Si no existe discovery, el workflow muestra advertencia y solo ejecuta validación de sintaxis + reglas.
