# QuinotoSpec Changelog

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
