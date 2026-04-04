---
name: Quinotospec Rollback
description: Deshace cambios realizados por workflows de QuinotoSpec cuando la validación falla o el usuario lo solicita.
---

# Skill: Quinotospec Rollback

Usa esta skill para deshacer cambios realizados durante la ejecución de un workflow. Útil cuando:
- Una validación falla después de crear archivos
- El usuario cambia de opinión
- Se necesita limpiar estado parcial

## Tipos de Rollback

### 1. Rollback de Changelog

Deshace la última entrada del changelog.

```bash
/rollback --type changelog
```

**Acciones**:
1. Lee `.quinoto-spec/quinoto-spec-changelog.md`
2. Elimina la última entrada (último header ##)
3. Guarda el archivo

### 2. Rollback de Propuesta

Deshace la creación de una propuesta completa.

```bash
/rollback --type proposal --slug stripe-migration
```

**Acciones**:
1. Mueve la carpeta `.quinoto-spec/proposals/{{SLUG}}` a `_archived/`
2. Elimina el prefijo del `prefix-registry.md`
3. Ejecuta rollback de changelog

### 3. Rollback de Historia de Usuario

Deshace la creación de una historia de usuario.

```bash
/rollback --type user-story --slug stripe-migration --us-id US-STRP-001
```

**Acciones**:
1. Elimina `{{US_ID}}_tasks.md`
2. Elimina la entrada en `user-histories.md`
3. Ejecuta rollback de changelog

### 4. Rollback de Tarea

Deshace el marcado de una tarea como completada.

```bash
/rollback --type task --slug stripe-migration --task-id TSK-STRP-001
```

**Acciones**:
1. Cambia `[x]` a `[ ]` en el archivo de tareas
2. Si la tarea estaba archivada, mover de `_archived/` de vuelta
3. Ejecuta rollback de changelog

### 5. Rollback Completo (Full)

Deshace todo lo realizado en una sesión/fecha específica.

```bash
/rollback --type full --since "2024-01-15"
```

**Acciones**:
1. Identifica todos los cambios desde la fecha dada
2. Pregunta al usuario qué desea revertir
3. Ejecuta rollback selectivo

## Flags

| Flag | Descripción |
|------|-------------|
| `--type` | Tipo: `changelog`, `proposal`, `user-story`, `task`, `full` |
| `--slug` | Slug de la propuesta |
| `--us-id` | ID de la historia de usuario |
| `--task-id` | ID de la tarea |
| `--since` | Fecha para rollback full |
| `--dry-run` | Mostrar qué se revertirá sin hacer cambios |
| `--confirm` | Saltar confirmación (para scripting) |

## Manejo de Errores

- Si el archivo no existe → *"No se encontró el elemento a revertir"*
- Si ya fue archivado previamente → *"El elemento ya está en archive"*
- Si hay dependencias (ej. tarea tiene hijos) → Advertir y pedir confirmación

## Ejemplo de Uso

```bash
# Ver qué se revertirá sin hacer cambios
/rollback --type proposal --slug auth-jwt --dry-run

# Revertir una propuesta
/rollback --type proposal --slug auth-jwt --confirm

# Rollback de múltiples tareas
/rollback --type task --slug auth-jwt --task-id TSK-AUTH-001,TSK-AUTH-002 --confirm
```

## Validación Post-Rollback

Después de ejecutar rollback, ejecutar `quinotospec-validate` para asegurar que el sistema está en estado consistente.
