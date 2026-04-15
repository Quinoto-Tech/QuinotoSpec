# Guía de Contribución - QuinotoSpec

¡Gracias por tu interés en contribuir a QuinotoSpec! Esta guía te ayudará a entender cómo contribuir efectivamente al proyecto.

## Tabla de Contenido

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
  - [Reportar Bugs](#reportar-bugs)
  - [Sugerir Mejoras](#sugerir-mejoras)
  - [Contribuir con Código](#contribuir-con-código)
- [Desarrollo Local](#desarrollo-local)
  - [Requisitos Previos](#requisitos-previos)
  - [Configuración del Entorno](#configuración-del-entorno)
  - [Estructura del Proyecto](#estructura-del-proyecto)
- [Desarrollo de Components](#desarrollo-de-components)
  - [Crear una Nueva Skill](#crear-una-nueva-skill)
  - [Crear un Nuevo Workflow](#crear-un-nuevo-workflow)
  - [Crear un Nuevo Agent](#crear-un-nuevo-agent)
  - [Modificar Reglas Globales](#modificar-reglas-globales)
- [Estándares de Código](#estándares-de-código)
  - [Convenciones de Naming](#convenciones-de-naming)
  - [Formato de Archivos](#formato-de-archivos)
  - [Documentación](#documentación)
- [Proceso de Pull Request](#proceso-de-pull-request)
  - [Branch Naming](#branch-naming)
  - [Checklist del PR](#checklist-del-pr)
  - [Revisión de Código](#revisión-de-código)
- [Release Process](#release-process)

---

## Código de Conducta

Este proyecto adhiere a un código de conducta que esperamos que todos los contribuidores respeten. Por favor, lee [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) antes de contribuir.

## Cómo Contribuir

### Reportar Bugs

Si encuentras un bug, por favor:

1. **Verifica que no haya sido reportado** en [GitHub Issues](https://github.com/anomalyco/opencode/issues)
2. **Crea un nuevo issue** con:
   - Título descriptivo
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Versión de QuinotoSpec
   - Entorno (OS, IDE, versión del agente)
   - Logs o screenshots relevantes

### Sugerir Mejoras

Las sugerencias son bienvenidas:

1. Abre un issue con la etiqueta `enhancement`
2. Describe la mejora y su justificación
3. Propón una implementación si es posible
4. Discute con los mantenedores antes de comenzar a codificar

### Contribuir con Código

1. **Fork el repositorio**
2. **Crea un branch** siguiendo la convención de naming
3. **Implementa tus cambios**
4. **Escribe tests** si aplica
5. **Actualiza la documentación**
6. **Abre un Pull Request**

---

## Desarrollo Local

### Requisitos Previos

- **Git**: Para control de versiones
- **Node.js** (opcional): Para scripts de utilidad
- **Python 3.8+** (opcional): Para algunas skills
- **Editor de código**: VS Code, Cursor, o cualquier editor con soporte Markdown

### Configuración del Entorno

```bash
# 1. Clona tu fork
git clone https://github.com/tu-usuario/quinotospec-package.git
cd quinotospec-package

# 2. Agrega el remote upstream
git remote add upstream https://github.com/anomalyco/opencode.git

# 3. Crea un branch para tu contribución
git checkout -b feature/TSK-CONTRIB-001-tu-contribucion

# 4. Instala QuinotoSpec en un proyecto de prueba
./install.sh --opencode  # O --cursor, --cline
```

### Estructura del Proyecto

```
quinotospec-package/
├── agent-dist/                    # Distribución de agentes
│   ├── agents/                    # Definiciones de agentes
│   │   └── agent-name.md
│   ├── rules/                     # Reglas globales
│   │   └── quinotospec-rules.md
│   ├── skills/                    # Skills especializadas
│   │   └── skill-name/
│   │       └── SKILL.md
│   └── workflows/                 # Flujos de trabajo
│       └── quinotospec.workflow-name.md
├── AGENTS.md                      # Guía para agentes
├── CHANGELOG.md                   # Historial de cambios
├── CONTRIBUTING.md                # Este archivo
├── LICENSE                        # Licencia MIT
├── README.md                      # Documentación principal
└── install.sh                     # Script de instalación
```

---

## Desarrollo de Components

### Crear una Nueva Skill

Las skills son instrucciones especializadas que el agente puede ejecutar.

#### Estructura

```
agent-dist/skills/quinotospec-nueva-skill/
└── SKILL.md
```

#### Formato del SKILL.md

```markdown
---
name: Nueva Skill
description: Descripción breve de lo que hace la skill.
---

# Skill: Nueva Skill

Descripción detallada de la skill.

## Instrucciones de Ejecución

### Paso 1 - Descripción
1. Instrucción específica
2. Otra instrucción

### Paso 2 - Descripción
- Punto importante
- Otro punto

## Ejemplos

### Ejemplo Básico
```
@quinotospec-nueva-skill --parametro valor
```

### Ejemplo Avanzado
```
@quinotospec-nueva-skill --parametro valor --flag
```

## Parámetros

| Parámetro | Descripción | Requerido | Default |
|-----------|-------------|-----------|---------|
| `--parametro` | Descripción del parámetro | Sí | N/A |
| `--flag` | Flag opcional | No | false |

## Notas Importantes

- Nota 1
- Nota 2
```

#### Checklist para Nueva Skill

- [ ] Nombre descriptivo y único
- [ ] Descripción clara en el frontmatter
- [ ] Instrucciones paso a paso
- [ ] Ejemplos de uso
- [ ] Documentación de parámetros
- [ ] Pruebas en al menos 2 proyectos diferentes
- [ ] Actualizado en README.md si es una skill pública

### Crear un Nuevo Workflow

Los workflows son secuencias automatizadas de instrucciones.

#### Estructura

```
agent-dist/workflows/quinotospec.nombre-workflow.md
```

#### Formato del Workflow

```markdown
---
description: Descripción breve del workflow
---

# Workflow: Nombre del Workflow

Descripción detallada de qué hace este workflow.

## Precondiciones

- Condición 1
- Condición 2

## Instrucciones

### Paso 1 - Descripción
1. Instrucción específica
2. Otra instrucción

### Paso 2 - Descripción
- Punto importante
- Otro punto

## Output Esperado

Describe qué archivos se generan o modifican.

## Ejemplos

### Ejemplo Básico
```
@quinotospec.nombre-workflow
```

### Ejemplo con Parámetros
```
@quinotospec.nombre-workflow --parametro valor
```

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| Error 1 | Causa 1 | Solución 1 |
| Error 2 | Causa 2 | Solución 2 |
```

#### Checklist para Nuevo Workflow

- [ ] Nombre sigue convención `quinotospec.nombre.md`
- [ ] Descripción en frontmatter
- [ ] Precondiciones documentadas
- [ ] Pasos claros y secuenciales
- [ ] Output esperado definido
- [ ] Ejemplos de uso
- [ ] Errores comunes documentados
- [ ] Actualizado en README.md

### Crear un Nuevo Agent

Los agents son perfiles especializados con responsabilidades específicas.

#### Estructura

```
agent-dist/agents/agent-name.md
```

#### Formato del Agent

```markdown
# Agent: Nombre del Agent

## Descripción
Breve descripción del rol y responsabilidades del agente.

## Responsabilidades
- Responsabilidad 1
- Responsabilidad 2
- Responsabilidad 3

## Comandos Disponibles
- `@comando1`: Descripción
- `@comando2`: Descripción

## Configuración
```yaml
name: agent-name
description: Descripción
model: modelo-preferido
temperature: 0.7
```

## Ejemplo de Uso
```
@agent-name ejecuta [descripción de la tarea]
```
```

#### Checklist para Nuevo Agent

- [ ] Nombre descriptivo
- [ ] Descripción clara de responsabilidades
- [ ] Lista de comandos disponibles
- [ ] Configuración de modelo
- [ ] Ejemplos de uso
- [ ] Documentado en README.md

### Modificar Reglas Globales

Las reglas globales están en `agent-dist/rules/quinotospec-rules.md`.

#### Proceso

1. **Abre un issue** discutiendo el cambio de regla
2. **Obtén aprobación** de los mantenedores
3. **Modifica el archivo** siguiendo el formato existente
4. **Actualiza la documentación** si es necesario
5. **Prueba en múltiples proyectos**

#### Formato de Reglas

```markdown
## Nombre de la Regla
- **Regla**: Descripción clara de la regla
- **Acción**: Qué hace el agente cuando se viola la regla
- **Excepciones**: Cuándo no aplica (si hay)
```

---

## Estándares de Código

### Convenciones de Naming

| Component | Format | Example |
|-----------|--------|---------|
| **Skills** | `quinotospec-<name>` | `quinotospec-mark-done` |
| **Workflows** | `quinotospec.<name>.md` | `quinotospec.apply.md` |
| **Agents** | `<name>.md` | `code-reviewer.md` |
| **Branches** | `feature/<ID>-<desc>` | `feature/TSK-AUTH-001-add-login` |
| **Proposals** | `YYYY-MM-DD-<slug>` | `2024-04-15-auth-jwt` |

### Formato de Archivos

#### Archivos Markdown
- Usa **H1** (`#`) solo para el título principal
- Usa **H2** (`##`) para secciones principales
- Usa **H3** (`###`) para subsecciones
- Incluye tabla de contenido en archivos > 100 líneas
- Usa bloques de código con lenguaje especificado

#### Frontmatter (YAML)
```yaml
---
name: Nombre
description: Descripción breve
---
```

#### Ejemplos de Código
- Usa bloques de código con sintaxis resaltada
- Incluye comentarios explicativos
- Muestra tanto el código como la salida esperada

### Documentación

#### Requisitos Mínimos
- Toda nueva feature debe tener documentación
- Actualizar README.md si es una feature pública
- Incluir ejemplos de uso
- Documentar parámetros y opciones

#### Estilo de Documentación
- Escribe en español (para consistencia con el proyecto)
- Usa lenguaje claro y conciso
- Incluye ejemplos prácticos
- Explica el "por qué" además del "cómo"

---

## Proceso de Pull Request

### Branch Naming

```
feature/TSK-CONTRIB-001-descripcion-corta
bugfix/TSK-CONTRIB-002-fix-descripcion
docs/TSK-CONTRIB-003-update-readme
```

### Checklist del PR

#### Antes de Abrir el PR
- [ ] Código funciona localmente
- [ ] Tests pasan (si aplica)
- [ ] Documentación actualizada
- [ ] Changelog actualizado (si es un cambio significativo)
- [ ] Commits son limpios y descriptivos

#### Contenido del PR
- [ ] Título descriptivo
- [ ] Descripción detallada de los cambios
- [ ] Referencia a issues relacionados
- [ ] Screenshots si aplica
- [ ] Notas de release si aplica

#### Ejemplo de PR Template

```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Nueva feature
- [ ] Bug fix
- [ ] Mejora de documentación
- [ ] Refactoring
- [ ] Otro

## Cambios Realizados
- Cambio 1
- Cambio 2
- Cambio 3

## Testing
- [ ] Tests unitarios
- [ ] Tests de integración
- [ ] Testing manual

## Screenshots (si aplica)
[Screenshots aquí]

## Notas Adicionales
[Notas aquí]

Fixes #<issue_number>
```

### Revisión de Código

#### Para Revisores
- Revisa por claridad y mantenibilidad
- Verifica que la documentación esté actualizada
- Prueba localmente si es posible
- Proporciona feedback constructivo

#### Para Autores
- Responde a todos los comentarios
- Haz cambios solicitados
- Mantén los commits limpios
- Haz squash si es necesario

---

## Release Process

### Versioning

QuinotoSpec sigue [Semantic Versioning](https://semver.org/):

- **Major (X.0.0)**: Cambios breaking en la metodología o estructura
- **Minor (0.X.0)**: Nuevas features, workflows o skills
- **Patch (0.0.X)**: Correcciones de bugs, mejoras de documentación

### Proceso de Release

1. **Actualiza CHANGELOG.md** con todos los cambios
2. **Actualiza versiones** en archivos relevantes
3. **Crea un tag** de Git con el número de versión
4. **Publica el release** en GitHub
5. **Actualiza documentación** si es necesario

### Ejemplo de Tag

```bash
git tag -a v2.1.0 -m "Release v2.1.0: Nueva skill de validación"
git push origin v2.1.0
```

---

## Preguntas Frecuentes

### ¿Cómo pruebo mis cambios?

1. Instala QuinotoSpec en un proyecto de prueba
2. Realiza tus cambios en el paquete
3. Re-instala en el proyecto de prueba
4. Prueba todas las funcionalidades afectadas

### ¿Puedo contribuir sin saber programar?

¡Sí! Las contribuciones de documentación, diseño, testing y bugs son muy valiosas.

### ¿Cuánto tiempo toma revisar un PR?

Normalmente revisamos PRs en 3-7 días hábiles. Los PRs grandes pueden tomar más tiempo.

### ¿Cómo me mantengo actualizado?

- Sigue el repositorio en GitHub
- Suscríbete a las releases
- Únete a las discusiones en issues

---

## Contacto

- **Issues**: [GitHub Issues](https://github.com/anomalyco/opencode/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/anomalyco/opencode/discussions)
- **Email**: [team@quinotospec.dev](mailto:team@quinotospec.dev)

¡Gracias por contribuir a QuinotoSpec! 🪓
