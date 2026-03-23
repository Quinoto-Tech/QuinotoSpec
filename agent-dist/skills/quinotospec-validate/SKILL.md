---
name: Quinotospec Validate
description: Ejecuta checks de validación del estado del sistema QuinotoSpec antes de ejecutar workflows críticos.
---

# Skill: Quinotospec Validate

Usa esta skill como precondición antes de ejecutar cualquier workflow de creación o modificación. Verifica que el sistema esté en un estado coherente para continuar.

## Checks de Validación

Ejecuta los siguientes checks en orden y reporta el resultado de cada uno con ✅ / ❌:

### 1. Discovery
- ✅ La carpeta `.quinoto-spec/discovery/` existe.
- ✅ Están presentes los 8 archivos esperados: `00-stack-profile.md`, `01-overview.md`, `02-architecture.md`, `03-endpoints-and-openapi.md`, `04-data-and-services.md`, `05-devops-ci-security.md`, `06-findings-and-recommendations.md`, `07-product-and-agreements.md`.
- ✅ `07-product-and-agreements.md` tiene contenido más allá de los encabezados (DoR/DoD definidos).

### 2. Prefix Registry
- ✅ El archivo `.quinoto-spec/prefix-registry.md` existe.
- ✅ No hay filas duplicadas (dos propuestas con el mismo prefijo).

### 3. Changelog
- ✅ El archivo `.quinoto-spec/quinoto-spec-changelog.md` existe.

### 4. Propuestas Activas (si aplica)
- ✅ No hay propuestas con `**Estado:** 🟢 En Curso` sin ninguna tarea iniciada.
- ✅ No hay archivos de tareas con checkboxes mezclados inconsistentemente (ej. tareas completadas sin historia completada).

## Comportamiento

- Si **todos los checks pasan** → reportar `✅ Sistema válido. Puedes continuar.`
- Si **algún check falla** → reportar los checks fallidos con su causa y sugerir la acción correctiva antes de continuar.
- El agente que invoca esta skill **decide si detener o continuar** según el contexto. Para workflows bloqueantes (como `create-proposal`), un fallo en el check de `07-product-and-agreements.md` debe detener la ejecución.
