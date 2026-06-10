---
name: quinotospec-validate
description: Ejecuta checks de validación del estado del sistema QuinotoSpec antes de ejecutar workflows críticos.
---

# Skill: Quinotospec Validate

Usa esta skill como precondición antes de ejecutar cualquier workflow de creación o modificación. Verifica que el sistema esté en un estado coherente para continuar.

## Checks de Validación

Ejecuta los siguientes checks en orden y reporta el resultado de cada uno con ✅ / ❌:

### 1. Discovery
- ✅ La carpeta `.quinoto-spec/discovery/` existe.
- ✅ Están presentes los 8 archivos esperados: `01-stack-profile.md`, `02-overview.md`, `03-architecture.md`, `04-endpoints-and-openapi.md`, `05-data-and-services.md`, `06-devops-ci-security.md`, `07-findings-and-recommendations.md`, `08-product-and-agreements.md`.
- ✅ `08-product-and-agreements.md` tiene contenido más allá de los encabezados (DoR/DoD definidos).

### 2. Prefix Registry
- ✅ El archivo `.quinoto-spec/prefix-registry.md` existe.
- ✅ No hay filas duplicadas (dos propuestas con el mismo prefijo).

### 3. Changelog
- ✅ El archivo `.quinoto-spec/quinoto-spec-changelog.md` existe.
- ✅ El changelog tiene entradas (no está vacío).

### 4. Propuestas Activas (si aplica)
- ✅ No hay propuestas con `**Estado:** 🟢 En Curso` sin ninguna tarea iniciada.
- ✅ No hay archivos de tareas con checkboxes mezclados inconsistentemente (ej. tareas completadas sin historia completada).

### 5. Branch Naming Convention (para workflows apply)
- ✅ El branch actual sigue el formato `feature/{{TASK_ID}}-descripcion` o `bugfix/{{TASK_ID}}-descripcion`.
- ⚠️ Si no hay branch o es main/master, advertencia nomás.

### 6. Archivo Config Crítico (para workflows de config)
- ✅ Al modificar `base-config.yml` o `sprint-config.yml`, verificar que se obtuvo confirmación del usuario.
- ⚠️ Si no hay confirmación registrada, DETENER.

### 7. Estado de Archive
- ✅ Al archivar, verificar que el estado en proposal.md sea `✅ Completada`.
- ⚠️ Si no está completada, Advertir antes de proceder.

### 8. Discovery Freshness
- ✅ Archivos de discovery tienen menos de 30 días.
- ⚠️ Si > 30 días, sugerir `@quinotospec.refresh-discovery`.

## Comportamiento

- Si **todos los checks pasan** → reportar `✅ Sistema válido. Puedes continuar.`
- Si **algún check falla** → reportar los checks fallidos con su causa y sugerir la acción correctiva antes de continuar.
- El agente que invoca esta skill **decide si detener o continuar** según el contexto. Para workflows bloqueantes (como `create-proposal`), un fallo en el check de `08-product-and-agreements.md` debe detener la ejecución.

## Flags de Uso

```bash
/quinotospec-validate --strict  # Detiene en cualquier fallo
/quinotospec-validate --quick   # Solo checks básicos (discovery + prefix)
/quinotospec-validate --full    # Todos los checks
```

## Checks Avanzados (modo full)

### 9. Consistencia de Tareas
- ✅ Cada US en user-stories.md tiene archivo de tareas correspondiente.
- ✅ No hay orphan tasks (tasks sin US padre).

### 10. Sprint Consistency
- ✅ Si hay sprints activos, las tareas asignadas existen.
- ✅ No hay tareas duplicadas entre sprints.

## Modo --fix (Correccion Automatica)

Ejecuta con `--fix` para intentar corregir automaticamente los errores detectados:

```bash
/quinotospec-validate --full --fix
```

### Correcciones Automaticas Disponibles

| Check | Correccion Automatica |
|-------|----------------------|
| Changelog vacio | Crea archivo con titulo `# QuinotoSpec Changelog` |
| Prefix registry no existe | Crea archivo con estructura base |
| `_archived/` no existe | Crea directorio en cada propuesta activa |
| Discovery > 30 dias | Sugiere `@quinotospec.refresh-discovery` (no auto-fix) |
| Orphan tasks | Reporta pero no corrige (requiere decision humana) |

### Correcciones que Requieren Confirmacion

- Crear archivos nuevos → Siempre pregunta antes
- Mover archivos a `_archived/` → Requiere confirmacion explicita
- Modificar estados en proposal.md → Requiere confirmacion

## Output JSON

Ejecuta con `--json` para obtener resultados en formato JSON (util para integracion con CI/CD):

```bash
/quinotospec-validate --full --json
```

### Formato de Output JSON

```json
{
  "valid": false,
  "timestamp": "2026-04-15T10:30:00Z",
  "checks": {
    "discovery": {
      "status": "pass",
      "details": "8/8 archivos presentes, DoR/DoD definidos"
    },
    "prefix_registry": {
      "status": "fail",
      "severity": "BLOCKING",
      "details": "Archivo no encontrado",
      "fix": "Ejecuta: touch .quinoto-spec/prefix-registry.md"
    },
    "changelog": {
      "status": "pass",
      "details": "15 entradas encontradas"
    }
  },
  "summary": {
    "total": 10,
    "passed": 8,
    "failed": 1,
    "warnings": 1,
    "blocking": 1
  }
}
```

## Check de Integridad (Checksums)

En modo `--full`, verifica integridad de archivos criticos:

1. Calcula checksum (md5) de archivos de especificacion
2. Compara con checksums almacenados en `.quinoto-spec/.checksums` (si existe)
3. Si un archivo fue modificado externamente (sin pasar por QuinotoSpec):
   - Reporta: "⚠️ Archivo modificado externamente: proposal.md"
   - Sugiere verificar si el cambio fue intencional
4. Actualiza checksums despues de cada workflow exitoso

Este check detecta:
- Ediciones manuales de archivos de especificacion
- Conflictos de merge no resueltos
- Archivos corruptos o truncados
