# QuinotoSpec Changelog

## [Fecha: 2026-01-29] - Expanded Archive & Project Dashboard
### Resumen
- **Archive Workflow Evolution**: Ahora permite archivar no solo propuestas completas (carpetas), sino también archivos individuales de Historias de Usuario y Tareas usando el prefijo `__`.
- **Nuevo Workflow `@quinotospec.status`**: Implementación de un dashboard automático (`PROJECT_STATUS.md`) que resume el progreso, prioridades y el valor total generado (Time Saved).
- **Estandarización de Workflows**: Ajuste masivo en todos los workflows para asegurar que el reporte al changelog sea obligatorio y consistente.
- **Optimización de Changelog**: Se cambió el orden de escritura a "Newest First" para facilitar la lectura de arriba hacia abajo.
**Time Saved**: ~2h (AI: 10m vs Human: 2h)


## [Fecha: 2026-01-29] - Cursor Support Added
### Resumen
- Se añadió el parámetro `--cursor` al script `install.sh`.
- Ahora el instalador permite elegir entre el directorio `.agent/` (default) o `.cursor/`.
- En modo Cursor, se renombra automáticamente la carpeta `workflows/` a `commands/` para compatibilidad nativa.
- Se actualizó el `README.md` con las instrucciones de uso para Cursor.
**Time Saved**: ~1h (AI: 5m vs Human: 1h)

## [Fecha: 2026-01-29] - Multi-Language Stack Detection
### Resumen
- Implementación de la nueva Skill `quinotospec-stack-detect` para identificación automática de stacks tecnológicos.
- Actualización del workflow `@quinotospec.discovery` para generar el perfil técnico en `.quinoto-spec/discovery/00-stack-profile.md`.
- Vinculación del workflow `@quinotospec.create-proposal` con el perfil técnico para ofrecer sugerencias de arquitectura y código especializadas según el lenguaje detectado.
**Time Saved**: ~2h (AI: 10m vs Human: 2h)
