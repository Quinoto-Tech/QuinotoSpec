---
description: Genera un documento de onboarding personalizado por rol para nuevos integrantes del equipo, basado en el discovery y el estado actual del proyecto.
---

Este workflow lee la documentación existente del proyecto y genera un archivo de onboarding completo, contextualizado y accionable para que una persona nueva pueda ponerse al día sin depender de otro compañero.

**Parámetros Opcionales:**
- `ROL`: Rol del integrante. Si no se provee, el workflow **preguntará** antes de continuar.

---

## Paso 0 — Selección de Rol (OBLIGATORIO antes de continuar)

Si el usuario **no proporcionó** el parámetro `ROL`, detener la ejecución y presentar el siguiente menú de selección:

---

> **¿Para qué rol generamos el onboarding?**
>
> Elegí una opción:
>
> **1. General**
> Vista balanceada del proyecto. Para alguien que aún no tiene un rol definido o necesita una visión completa.
>
> **2. Desarrollador**
> Foco técnico: arquitectura, setup, código, tests y flujo de trabajo del equipo.
>
> **3. Producto / Negocio**
> Foco en qué se está construyendo, por qué, acuerdos del equipo y roadmap. Sin detalles técnicos.
>
> **4. Soporte**
> Foco en comportamiento del sistema, endpoints, servicios externos e identificación de incidentes.
>
> **5. Tengo un IQ muy bajo y necesito entender**
> Lenguaje extremadamente simple, analogías del mundo real, sin jerga técnica. Para cualquier persona sin background técnico.
>
> **6. Otro**
> Ingresá el nombre del rol y el agente te pedirá especificaciones adicionales.

---

Esperar la respuesta del usuario antes de continuar.

### Si elige opciones 1–5:
- Registrar el ROL seleccionado internamente (ver tabla de mapeo más abajo).
- Continuar al Paso 1.

### Si elige opción 6 — "Otro":
1. Solicitar al usuario:
   > "¿Cómo se llama el rol? (ej. `Data Analyst`, `Scrum Master`, `Legal`, `Investor`)"
2. Registrar el nombre ingresado como `ROL_CUSTOM`.
3. Solicitar especificaciones adicionales:
   > "Contame un poco más sobre este rol para personalizar el documento:
   > - ¿Qué necesita entender esta persona sobre el proyecto?
   > - ¿Qué secciones son más importantes para ella? (ej. datos, procesos, métricas, flujos de usuario)
   > - ¿Hay algo que definitivamente NO debe incluirse?
   > - ¿Tiene conocimientos técnicos o es un perfil no técnico?"
4. Registrar las especificaciones como `ROL_SPECS`.
5. Continuar al Paso 1 usando `ROL_SPECS` como guía de generación en lugar de un skill predefinido.

### Tabla de mapeo de roles a skills

| Opción | ROL | Skill a cargar y aplicar |
|---|---|---|
| 1 | General | `quinotospec-onboard-general` |
| 2 | Desarrollador | `quinotospec-onboard-developer` |
| 3 | Producto / Negocio | `quinotospec-onboard-product` |
| 4 | Soporte | `quinotospec-onboard-support` |
| 5 | Simple | `quinotospec-onboard-simple` |
| 6 | Custom (`ROL_CUSTOM`) | Sin skill — usar `ROL_SPECS` como instrucciones |

**Instrucción crítica**: Una vez determinado el ROL, leer el SKILL.md correspondiente de la carpeta `skills/quinotospec-onboard-{rol}/` **antes de recolectar contexto**. Las instrucciones del skill son vinculantes: determinan qué secciones incluir, con qué nivel de detalle y en qué tono.

---

## Paso 1 — Verificar prerequisitos

1. Verificar que exista el directorio `.quinoto-spec/discovery/`. Si no existe → **detener ejecución** y notificar al usuario:
   > "No se encontró el directorio `.quinoto-spec/discovery/`. Ejecuta primero `@quinotospec.discovery` para generar el contexto del proyecto."

2. Verificar que existan al mínimo los archivos `00-stack-profile.md` y `01-overview.md` dentro de `.quinoto-spec/discovery/`. Si falta alguno → advertir, pero continuar con lo disponible.

3. Leer la `Discovery Date` en `00-stack-profile.md`. Si tiene más de 30 días de antigüedad → incluir advertencia visible en el documento generado:
   > "⏰ **Advertencia**: El discovery tiene más de 30 días de antigüedad. Algunos datos pueden estar desactualizados. Considera ejecutar `@quinotospec.refresh-discovery`."

---

## Paso 2 — Recolección de contexto

Leer los archivos de discovery disponibles. El skill del rol seleccionado indica **qué extraer** de cada archivo y cuánto detalle incluir.

**Fuentes del discovery (`.quinoto-spec/discovery/`):**

| Archivo | Qué extraer |
|---|---|
| `00-stack-profile.md` | Lenguaje, frameworks, package manager, test runner, comandos de dev/build/test |
| `01-overview.md` | Qué hace el proyecto, estructura de carpetas, pre-requisitos de entorno |
| `02-architecture.md` | Descripción de arquitectura, componentes principales, patrones de diseño |
| `03-endpoints-and-openapi.md` | Endpoints principales, autenticación |
| `04-data-and-services.md` | Modelos de datos clave, servicios externos integrados |
| `05-devops-ci-security.md` | Variables de entorno requeridas, pipeline CI/CD, comandos de despliegue |
| `07-product-and-agreements.md` | DoR/DoD del equipo, visión de producto |

**Fuentes de estado del proyecto:**

- Escanear `.quinoto-spec/proposals/` (excluir `_archived/`): extraer título, estado, prioridad y servicios afectados de cada `proposal.md`.
- Para cada propuesta activa, buscar archivos `*_tasks.md` y contar tareas `[ ]` vs `[x]`.
- Leer `.quinoto-spec/prefix-registry.md` para listar los prefijos activos.
- Leer `.quinoto-spec/quinoto-spec-changelog.md` para actividad reciente.

> **Importante**: El skill del rol indica cuántas entradas del changelog incluir, qué propuestas son relevantes y cómo presentar la información.

---

## Paso 3 — Generar documento de onboarding

Crear el archivo `.quinoto-spec/onboarding-{{ROL_SLUG}}-{{FECHA}}.md` donde:
- `ROL_SLUG` es el rol en kebab-case (ej. `desarrollador`, `producto-negocio`, `soporte`, `general`, `simple`, o el nombre custom).
- `FECHA` tiene formato `YYYYMMDD`.

**El documento debe seguir estrictamente las instrucciones del skill cargado en el Paso 0.**

Para ROL = "Otro" (custom), aplicar las `ROL_SPECS` provistas por el usuario como guía de generación.

Estructura base del documento (el skill puede ampliar, reducir u omitir secciones):

---

```markdown
# 👋 Guía de Onboarding — [NOMBRE DEL PROYECTO]

> **Rol**: [ROL seleccionado]
> **Generado**: [FECHA]
> **Discovery base**: [Discovery Date del 00-stack-profile.md]

---

## 🗺️ ¿Qué es este proyecto?

[Resumen ejecutivo de 3-5 oraciones extraído de 01-overview.md: qué hace el sistema, para quién, en qué lenguaje/plataforma corre.]

---

## 🛠️ Cómo levantar el proyecto

### Pre-requisitos
[Lista de herramientas, versiones y accesos necesarios, extraídos de 01-overview.md y 05-devops-ci-security.md]

### Variables de entorno requeridas
[Lista de variables sensibles detectadas en 05-devops-ci-security.md. Indicar cuáles son obligatorias y dónde conseguirlas.]

```bash
# Copiar el archivo de ejemplo
cp .env.example .env
# Completar los valores indicados con ⚠️
```

### Comandos básicos
```bash
# Instalar dependencias
[comando de install]

# Levantar en desarrollo
[comando dev]

# Correr tests
[comando test]

# Build de producción
[comando build]
```

---

## 🏗️ Arquitectura del Sistema

[Descripción de 2-4 párrafos extraída de 02-architecture.md: capas, módulos principales, patrón de diseño, responsabilidades.]

### Componentes clave

| Componente | Responsabilidad | Tecnología |
|---|---|---|
| [nombre] | [qué hace] | [tech] |

[Incluir el diagrama Mermaid de 02-architecture.md si existe.]

---

## 📡 Endpoints Principales

[Tabla resumida con los endpoints más importantes de 03-endpoints-and-openapi.md. No más de 10 filas; priorizar los de uso más frecuente.]

| Método | Ruta | Descripción | Auth requerida |
|---|---|---|---|
| GET | /ejemplo | Descripción | Sí / No |

---

## 🗄️ Modelos de Datos Clave

[Descripción de los modelos/tablas/colecciones más importantes de 04-data-and-services.md. Máximo 5 modelos, con sus campos principales.]

---

## 🔄 Estado Actual del Proyecto

### Propuestas Activas

| Prefijo | Propuesta | Estado | Prioridad | Progreso | Servicios |
|---|---|---|---|---|---|
| [PREFIX] | [Nombre] | [🟡/🟢/✅] | [P1/P2/P3] | [X/Y tareas] | [servicios] |

### Tareas Pendientes (próximas a ejecutar)

[Listar hasta 10 tareas con estado `[ ]` de las propuestas activas de mayor prioridad, con su ID, descripción y propuesta de origen.]

| Task ID | Descripción | Historia | Propuesta |
|---|---|---|---|
| TSK-XXX-001 | [descripción] | US-XXX-001 | [slug] |

---

## 📋 Acuerdos del Equipo

### Definition of Ready (DoR)
[Extraído de 07-product-and-agreements.md. Si está vacío, indicar: "⚠️ El equipo aún no definió estos acuerdos. Ver `.quinoto-spec/discovery/07-product-and-agreements.md`".]

### Definition of Done (DoD)
[Ídem DoR.]

---

## 📅 Actividad Reciente

[Últimos 10 registros del changelog, mostrando fecha, título de acción y resumen breve.]

| Fecha | Acción | Resumen |
|---|---|---|
| YYYY-MM-DD | [título] | [resumen] |

---

## 🧭 Primeros Pasos Sugeridos

[Basado en el ROL provisto (si existe) y las propuestas activas, generar una lista de 5-7 acciones concretas recomendadas para la primera semana:]

1. [ ] Levantar el proyecto localmente y correr los tests (`[comando test]`).
2. [ ] Leer la propuesta activa de mayor prioridad en `.quinoto-spec/proposals/`.
3. [ ] Revisar los acuerdos del equipo en `.quinoto-spec/discovery/07-product-and-agreements.md`.
4. [ ] Ejecutar `@quinotospec.status` para ver el dashboard del proyecto.
5. [tareas adicionales basadas en el ROL y propuestas activas]

---

## 📚 Recursos y Documentación

| Recurso | Ubicación |
|---|---|
| Discovery completo | `.quinoto-spec/discovery/` |
| Propuestas técnicas | `.quinoto-spec/proposals/` |
| Historial de cambios | `.quinoto-spec/quinoto-spec-changelog.md` |
| Registro de prefijos | `.quinoto-spec/prefix-registry.md` |
| Dashboard del proyecto | `PROJECT_STATUS.md` (si existe) |
| Comandos del agente | Ver `AGENTS.md` en la raíz |

---

_Generado por `@quinotospec.onboard` · QuinotoSpec Berserker Edition_
```

---

## Paso 4 — Notificación final

Al terminar, notificar al usuario:

> "✅ Documento de onboarding generado en `.quinoto-spec/onboarding-{{ROL_SLUG}}-{{FECHA}}.md`.
> Podés compartirlo directamente o abrirlo para personalizarlo antes de enviarlo."

---

**Instrucción Final OBLIGATORIA (Changelog):**
Una vez generado el documento, DEBES ejecutar la skill `quinotospec-update-changelog`.
- **Título de la Acción**: Onboarding Generado — ROL: {{ROL}}
- **Resumen**: Se generó el documento de onboarding en `.quinoto-spec/onboarding-{{ROL_SLUG}}-{{FECHA}}.md` para el rol "{{ROL}}". Basado en discovery de [Discovery Date].