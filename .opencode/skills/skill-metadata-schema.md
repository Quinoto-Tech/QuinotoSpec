# Esquema de Metadatos para Skills QuinotoSpec

Todas las skills deben incluir un bloque YAML inicial para permitir la carga dinámica (Lazy Loading).

## Estructura YAML
```yaml
---
name: string        # Nombre único de la habilidad
description: string # Propósito detallado
trigger: string[]   # Palabras clave o intenciones que activan la skill
scope: string[]     # Rutas de archivos (glob patterns) donde aplica
tools: string[]     # Herramientas del sistema requeridas
---
```

## Ejemplo: Skill de Testing
```yaml
---
name: Jest-Testing-Standard
description: Reglas y utilidades para escribir tests con Jest.
trigger: ["test", "verify", "coverage"]
scope: ["**/__tests__/**", "**/*.test.ts"]
tools: ["run_command", "view_file"]
---
```
