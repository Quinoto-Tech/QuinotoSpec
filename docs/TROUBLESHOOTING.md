# Troubleshooting - QuinotoSpec

## Problemas de Instalacion

### "Permission denied" al ejecutar install.sh
```bash
chmod +x install.sh
./install.sh --opencode
```

### "agent-dist directory not found"
Verifica que estas ejecutando desde el directorio raiz del paquete:
```bash
cd quinotospec-package/
./install.sh
```

### La instalacion no pasa la verificacion
```bash
# Verificar instalacion existente
./install.sh --verify --opencode --global

# Reinstalar
./install.sh --opencode --global
```

### Conflicto entre instalacion local y global
Si tienes ambas, la local tiene prioridad. Para limpiar:
```bash
# Desinstalar local
./install.sh --uninstall --opencode

# Verificar global
./install.sh --verify --opencode --global
```

## Problemas de Ejecucion

### "No se encontro .quinoto-spec/discovery/"
Necesitas ejecutar discovery primero:
```bash
@quinotospec.discovery
```

### "Prefijo no registrado"
El prefijo debe registrarse antes de usarse. Crea una propuesta:
```bash
@quinotospec.create-proposal
```
El workflow registra el prefijo automaticamente en `prefix-registry.md`.

### "Product Agreement Check fallido"
Debes completar los acuerdos de producto antes de crear propuestas:
1. Abre `.quinoto-spec/discovery/08-product-and-agreements.md`
2. Completa las secciones de DoR (Definition of Ready) y DoD (Definition of Done)
3. Guarda el archivo
4. Reintenta el workflow

### Workflows no reconocidos por el IDE
- **OpenCode**: Verifica que los archivos estan en `.opencode/commands/` (no `workflows/`)
- **Cursor**: Verifica que estan en `.cursor/commands/`
- **Cline**: Verifica que estan en `.cline/workflows/`

Reinstala con el flag correcto:
```bash
./install.sh --opencode
./install.sh --cursor
./install.sh --cline
```

### Discovery desactualizado (> 30 dias)
```bash
@quinotospec.refresh-discovery
```

## Problemas de Tests

### Tests fallan despues de apply
1. Revisa el output del test para identificar el error
2. Si es un error simple, el agente intenta corregirlo (max 2 intentos)
3. Si persiste, se ejecuta rollback automatico
4. Crea una tarea de debugging si el problema es complejo

### No hay tests configurados
QuinotoSpec detecta el stack pero no encuentra tests:
1. Agrega un framework de tests al proyecto
2. Actualiza `01-stack-profile.md` con el comando de tests
3. Re-ejecuta la tarea

## Problemas de Changelog

### Changelog vacio o no existe
```bash
# Crear manualmente
touch .quinoto-spec/quinoto-spec-changelog.md
echo "# QuinotoSpec Changelog" > .quinoto-spec/quinoto-spec-changelog.md
```

### Entradas con formato incorrecto
```bash
# Validar formato
/quinotospec-update-changelog --validate-only

# Corregir automaticamente
/quinotospec-update-changelog --fix
```

## Problemas de Git

### Branch naming incorrecto
Si estas en un branch que no sigue la convencion:
```bash
# Crear branch correcto
/quinotospec-generate-github-branch --task-id TSK-AUTH-001

# O renombrar el actual
git branch -m feature/TSK-AUTH-001-descripcion-correcta
```

### Conflictos de merge
1. No fuerces la resolucion
2. Usa `git mergetool` o resuelve manualmente
3. Despues de resolver, ejecuta tests
4. Continua con el workflow

## Diagnosticos

### Estado completo del sistema
```bash
@quinotospec-validate --full
```

### Detectar archivos huerfanos
```bash
@quinotospec.health
```

### Ver metricas del proyecto
```bash
@quinotospec-metrics --dashboard
```

### Buscar en .quinoto-spec/
```bash
/quinotospec-search --query "auth" --type proposal
```

### Limpiar recursos
```bash
@quinotospec.cleanup
```

## Obtener Ayuda

1. Revisa esta guia de troubleshooting
2. Ejecuta `@quinotospec-validate --full` para diagnosticar
3. Revisa `.quinoto-spec/quinoto-spec-changelog.md` para ver historial
4. Abre un issue en https://github.com/Quinoto-Tech/QuinotoSpec/issues
