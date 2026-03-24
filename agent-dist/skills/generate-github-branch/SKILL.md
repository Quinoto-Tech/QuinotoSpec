---
name: Generate GitHub Branch
description: Crea un nuevo branch feature siguiendo la convención de nombrado del sistema QuinotoSpec.
---

# Skill: Generate GitHub Branch

Usa esta skill para crear un branch de Git vinculado a una tarea técnica (`TSK-XXX`) o historia de usuario (`US-XXX`).

**IMPORTANTE**: Antes de ejecutar esta skill, DEBES confirmar con el usuario que está de acuerdo en crear un nuevo branch. Si el usuario no confirma, no ejecutes la skill.

## Instrucciones de Ejecución

### 1. Verificar estado del working directory

```bash
git status
```

Si hay cambios sin commitear no relacionados a la tarea actual, notifica al usuario antes de continuar.

### 2. Identificar la rama base

- Por defecto, crear el branch desde `main` o `develop` (el que exista en el repo).
- Verificar cuál es la rama principal con:

```bash
git remote show origin | grep 'HEAD branch'
```

### 3. Crear el branch con convención de nombrado

El nombre del branch debe seguir el formato:
```
feature/{{TASK_ID}}-descripcion-corta-en-kebab-case
```

Ejemplos:
- `feature/TSK-AUTH-001-add-login-endpoint`
- `feature/US-PAY-003-checkout-flow`

```bash
git checkout -b feature/{{TASK_ID}}-descripcion-corta
```

### 4. Publicar el branch

```bash
git push -u origin feature/{{TASK_ID}}-descripcion-corta
```

## Convenciones

- Siempre kebab-case para la descripción.
- Siempre vincular al `TASK_ID` o `US_ID` al inicio del nombre.
- Nunca crear branches sin prefijo `feature/`, `fix/` o `chore/`.
