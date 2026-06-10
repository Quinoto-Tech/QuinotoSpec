# Guia de Migracion - QuinotoSpec

## De v1.0 a v2.0

### Resumen de Cambios

| Aspecto | v1.0 | v2.0 |
|---------|------|------|
| Workflows | 20 | 33 |
| Skills | 19 | 27 |
| Reglas | 8 | 12 |
| Agentes | 0 | 9 |
| Install | Basico | Con validacion |

### Breaking Changes

1. **Skill renombrada**: `generate-github-branch` -> `quinotospec-generate-branch`
   - El directorio en `agent-dist/skills/` cambio de nombre
   - Si tenias referencias directas, actualizalas

2. **Nuevas reglas bloqueantes**: Reglas #9, #10, #12 son BLOCKING
   - #9: Validacion pre-workflow critico
   - #10: Backup obligatorio antes de mjolnir-refactor
   - #12: Proteccion de archivos archivados

3. **Workflows renombrados**: Algunos workflows ahora tienen heading H1
   - No afecta funcionalidad, solo estructura del archivo

### Pasos de Migracion

#### Automatica (Recomendada)
```bash
# 1. Backup manual por seguridad
cp -r .quinoto-spec/ .quinoto-spec.backup/

# 2. Ejecutar migracion
@quinotospec.migrate --to 2.0.0

# 3. Validar
@quinotospec-validate --full
```

#### Manual
Si prefieres migrar manualmente:

1. **Actualizar instalador**:
   ```bash
   cd quinotospec-package/
   git pull origin master
   ./install.sh --opencode --global
   ```

2. **Agregar agentes** (si no existen):
   ```bash
   mkdir -p .opencode/agents  # o .cursor/agents
   # Copiar agentes desde agent-dist/agents/
   ```

3. **Agregar nuevas skills**:
   ```bash
   # Copiar skills nuevas
   cp -r agent-dist/skills/quinotospec-search .opencode/skills/
   cp -r agent-dist/skills/quinotospec-stats .opencode/skills/
   cp -r agent-dist/skills/quinotospec-diff .opencode/skills/
   cp -r agent-dist/skills/quinotospec-sync .opencode/skills/
   ```

4. **Renombrar skill**:
   ```bash
   mv .opencode/skills/generate-github-branch .opencode/skills/quinotospec-generate-branch
   ```

5. **Actualizar reglas**:
   ```bash
   cp agent-dist/rules/quinotospec-rules.md .opencode/rules/
   ```

6. **Validar**:
   ```bash
   @quinotospec-validate --full
   ```

### Verificacion Post-Migracion

Despues de migrar, verifica:

```bash
# 1. Tests pasan
./tests/run-all-tests.sh

# 2. Validacion completa
@quinotospec-validate --full

# 3. Discovery vigente
@quinotospec.refresh-discovery  # si discovery > 30 dias

# 4. Workflow basico funciona
@quinotospec.status
```

### Rollback

Si la migracion causa problemas:

```bash
# Restaurar desde backup
rm -rf .quinoto-spec/
cp -r .quinoto-spec.backup/ .quinoto-spec/

# O desde backup automatico (si existe)
@quinotospec.backup --restore backup-pre-migrate-{timestamp}
```

## De v2.0 a v2.1

### Cambios Menores

v2.1 es una actualizacion incremental:
- Nuevos workflows: migrate, backup, export, import
- Nuevas skills: search, stats, diff, sync
- Mejoras en skills existentes: update-changelog, validate, mark-done
- Mejoras en workflows: apply (conflict resolution), create-proposal (validacion)

### Migracion
```bash
@quinotospec.migrate --to 2.1.0
```

## Futuras Versiones

### v3.0 - Warband: Falange (TBA)
- Class System: Roles especializados
- Shield Wall: Testing defensivo
- Breaking changes esperados en estructura de agentes

### v4.0 - Warband: Hird (TBA)
- War Council: Resolucion de conflictos
- Multi-repo support nativo
- Breaking changes en sync y dependency-graph
