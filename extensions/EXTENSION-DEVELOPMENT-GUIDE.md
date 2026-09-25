# Guía de desarrollo de extensiones

Una extensión amplía QuinotoSpec sin modificar el core. La fuente local se instala bajo `.quinoto-spec/extensions/<id>/` y se registra en `.quinoto-spec/extensions/.registry`.

## Estructura

```text
mi-extension/
├── extension.yml
├── commands/
├── skills/
├── templates/
└── config-template.yml
```

El manifest debe declarar `schema_version`, metadata estable, `provides`, requisitos y hooks. Los IDs usan caracteres kebab-case y las rutas no pueden contener `..` ni symlinks.

## Catálogo

El catálogo curado es `extensions/catalog.json`; el comunitario es `extensions/catalog.community.json`. Un entry local contiene `id`, `name`, `description` y `path`. El manager no descarga URLs ni ejecuta código durante la instalación.

## Hooks

Los puntos disponibles son `before_*` y `after_*` del contrato de workflows. Un hook automático requiere `auto: true`, pero solo se ejecuta con una invocación explícita `--run --yes`.

## Resolución

Los templates se resuelven en este orden: overrides del proyecto, presets, extensions y core. Usa `template_resolver.py` para inspeccionar la capa y el path ganador.

## Checklist

- [ ] Manifest válido y versión semver.
- [ ] Sin symlinks ni paths fuera del root.
- [ ] Commands/skills tienen nombres únicos.
- [ ] Hooks son necesarios, acotados y observables.
- [ ] Se prueba install, update, list, info, remove y hook run en sandbox.
- [ ] Se registra el cambio con `quinotospec-update-changelog`.
