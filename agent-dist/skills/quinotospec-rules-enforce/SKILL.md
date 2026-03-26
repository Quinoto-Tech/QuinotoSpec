---
name: Quinotospec Rules Enforce
description: Ejecuta y hace cumplir las reglas definidas en quinotospec-rules.md. Detiene workflows que violen las reglas.
---

# Skill: Quinotospec Rules Enforce

Usa esta skill para verificar cumplimiento de reglas antes de ejecutar acciones críticas. Esta skill convierte las reglas de quinotospec-rules.md en checks ejecutables.

## Reglas a Verificar

### 1. Changelog - Siempre actualizar

- **Verificación**: Lee `.quinoto-spec/quinoto-spec-changelog.md`
- **Check**: ¿La última entrada es de hace más de 24h?
- **Acción si falla**: Advertir que se necesita actualizar el changelog

### 2. Prefix Registry - No inventar prefijos

- **Verificación**: Lee `.quinoto-spec/prefix-registry.md`
- **Check**: ¿El prefijo ya existe en la tabla?
- **Acción si falla**: Detener y pedir registro del prefijo primero

### 3. Product Agreement Check (BLOQUEANTE)

- **Verificación**: Lee `.quinoto-spec/discovery/07-product-and-agreements.md`
- **Check**: ¿Tiene contenido más allá de headers?
- **Acción si falla**: **DETENER** ejecución - no se puede proceder sin DoR/DoD

### 4. No Sobreescribir Specs

- **Verificación**: Al escribir en archivos `user-histories.md` o `*_tasks.md`
- **Check**: ¿El archivo ya existe?
- **Acción si falla**: Usar merge inteligente, nunca overwrite

### 5. Validación de Estado Antes de Archivar

- **Verificación**: Al ejecutar archive workflow
- **Check**: ¿El estado en proposal.md es `✅ Completada`?
- **Acción si falla**: Advertir antes de proceder

### 6. Convención de Archivado

- **Verificación**: Al mover archivos a `_archived/`
- **Check**: ¿Existe la carpeta `_archived/`?
- **Acción si falla**: Crear la carpeta antes de mover

### 7. Branch Naming Convention

- **Verificación**: Al crear branches
- **Check**: ¿El branch sigue `feature/{{ID}}-descripcion`?
- **Acción si falla**: Corregir nombre antes de crear

### 8. Aprobación de Config Crítica

- **Verificación**: Al modificar archivos de configuración
- **Check**: ¿Es uno de los archivos protegidos?
- **Acción si falla**: Pedir confirmación explícita al usuario

## Comportamiento

- **Modo strict** (default): Detiene la ejecución si regla crítica falla
- **Modo warning**: Solo advierte pero permite continuar (usar para checks no bloqueantes)
- Retorna JSON con:
  - `passed`: boolean
  - `violations`: array de reglas fallidas
  - `blocking`: boolean (si hay reglas bloqueantes)

## Uso

```
/enforce-rules --mode strict --check changelog,prefix,product-agreement
```
