# QuinotoSpec: Berserker Edition 🪓

> [!NOTE]
> **ESTADO: PRODUCCIÓN / ESTABLE**
> Esta es la versión oficial diseñada para entornos de agentes avanzados y equipos de alto rendimiento.
>
> **Nota:** Estamos trabajando activamente en la integración nativa con GitHub Copilot.
>
> ### 🗺️ Roadmap
>
> **🪓 Berserker Edition (Actual)**
> _Status: 🟢 Estable / Producción_
> - ⏸️ **Runic Memory:** Memoria semántica del proyecto usando bases de datos vectoriales. _(Standby)_
> - ✅ **Mjolnir Refactor:** Capacidad de reescribir módulos enteros bajo demanda para limpiar deuda técnica. _(Completado)_
> - ✅ **Code Review Workflow** (`@quinotospec.review`): Revisión de branches contra criterios de aceptación, tests y convenciones del stack. _(Completado)_
> - ✅ **Sprint Planning Workflow** (`@quinotospec.sprint`): Generación de sprint plans con capacidad, prioridades y dependencias. _(Completado)_
> - ✅ **Validate Skill** (`quinotospec-validate`): Checks de sistema reutilizables como precondición para workflows críticos. _(Completado)_
> - ✅ **Refresh Discovery** (`@quinotospec.refresh-discovery`): Discovery incremental — detecta cambios y actualiza solo los archivos afectados. _(Completado)_
> - ✅ **Dependency Graph** (`@quinotospec.dependency-graph`): Mapa de dependencias inter-servicio con detección de contract drift. _(Completado)_
>
> **👻 Posesion Edition (TBA)**
> _Status: Concepto_
> - **Battle Frenzy (Swarm Mode):** Ejecución de múltiples agentes en paralelo para tareas masivas.
> - **Blood-Bond:** Predicción proactiva de User Stories e intenciones basada en el comportamiento del desarrollador.
>
> **🛡️ Warband: Falange Edition (TBA)**
> _Status: Futuro_
> - **Class System:** Roles de agentes especializados (Scout, Skald, Blacksmith) que trabajan en formación cerrada.
> - **Shield Wall:** Testing defensivo y validación cruzada entre agentes antes de mergear.
>
> **⚔️ Warband: Hird Edition (TBA)**
> _Status: Visionario_
> - **War Council:** Resolución de conflictos lógica y mediación estratégica entre equipos grandes.
> - **Alliance Integration (Multi-Repo):** Contexto compartido federado para arquitecturas distribuidas de gran escala.

<div align="center">
  <img src="berserker.png" alt="Quinoto Berserker" width="400" />
</div>

# Guía de Desarrollo Guiado por IA con QuinotoSpec

Esta guía explica cómo utilizar la metodología **QuinotoSpec** y sus agentes asociados para desarrollar software de manera estructurada, eficiente y documentada.

## Instalación

1.  **Obtén el paquete**: Asegúrate de tener la carpeta `quinotospec-package` disponible.
2.  **Ejecuta el instalador**: Desde una terminal, corre el script.
    
    ```bash
    # Da permisos de ejecución
    chmod +x quinotospec-package/install.sh

    # Ejecuta
    ./quinotospec-package/install.sh
    ```

    El script te pedirá **dónde quieres instalar el agente**.
    - Puedes presionar `Enter` para instalar en el directorio actual.
    - O escribir una ruta específica (ej. `~/proyectos/mi-nuevo-app`) y el script la creará si no existe.

### Soporte para Cursor
Si utilizas el editor **Cursor**, puedes usar el parámetro `--cursor` para que la instalación sea compatible con la estructura de Cursor:

```bash
./quinotospec-package/install.sh --cursor
```

**¿Qué cambia con este parámetro?**
- Instala la configuración en la carpeta `.cursor/` en lugar de `.agent/`.
- Renombra la subcarpeta `workflows` a `commands` para que Cursor la reconozca automáticamente como [custom commands](https://docs.cursor.com/context/rules-for-ai#custom-commands).

## Filosofía: "Proposal First" & "Context Slicing"

La metodología se basa en dos pilares fundamentales para maximizar la eficacia de la IA:

1.  **Proposal First**: La regla de oro. **Antes de escribir código, escribe una propuesta.** Esto evita el "código espagueti" y asegura que cada cambio tenga un propósito y diseño aprobado.

2.  **Context Slicing**: El contexto se "rebana" y refina progresivamente.
    - **Discovery**: Contexto Global (Todo el proyecto).
    - **Proposal**: Contexto de la Iniciativa (Solo lo relevante para el feature).
    - **User Histories**: Contexto del Valor (El "qué" y "para quién" funcional).
    - **Task**: Contexto Atómico (Instrucciones precisas para una acción).
    
    *Al achicar el foco en cada etapa, reducimos las alucinaciones y aumentamos la precisión.*

## Flujo de Trabajo (Workflow)

El ciclo de vida de una nueva funcionalidad sigue estos pasos estrictos, apoyados por workflows automatizados del agente:

### 1. Discovery
Si no conoces el estado actual del proyecto o vas a tocar un área compleja.

- **Comando**: `@quinotospec.discovery`
- **Output**: Genera documentación fresca en `.quinoto-spec/discovery/` (Arquitectura, Endpoints, etc.).
- **Objetivo**: Que el agente tenga contexto real antes de proponer nada.
- **Ejemplo**: `"Ejecuta @quinotospec.discovery en este directorio para entender la arquitectura base de datos."`

### 1.b Stack Discovery (Multi-Servicio)
Consolida múltiples discoveries independientes en una vista unificada a nivel raíz.

- **Comando**: `@quinotospec.stack-discovery`
- **Acción**: Lee los sub-proyectos, detecta inconsistencias tecnológicas y genera un discovery global consolidado.
- **Detalle**: Funciona como un "Discovery de Discoveries" en 3 pasos clave:
    1. **Gatekeeper de Frescura**: Verifica el `Discovery Date` de cada servicio. Si alguno tiene >30 días, bloquea y sugiere actualizarlo con `@quinotospec.refresh-discovery`.
    2. **Consolidación Inteligente**: No solo une archivos, sino que cruza datos: detecta inconsistencias de versión entre stacks, unifica la arquitectura en un solo diagrama Mermaid, y busca modelos de datos duplicados entre servicios.
    3. **Dependency Graph**: Invoca automáticamente el análisis de dependencias para mapear llamadas HTTP cruzadas y alertar sobre Contract Drift.
- **Ejemplo**: `"Ejecuta @quinotospec.stack-discovery para unificar la documentación de todos los microservicios del proyecto."`

### 2. Crear Propuesta Técnica
Define la solución a alto nivel.

- **Comando**: `@quinotospec.create-proposal`
- **Output**: Crea `.quinoto-spec/proposals/{slug}/proposal.md`.
- **Acción**:
    1.  El agente te pedirá la descripcion de la propuesta. (puedes inyectar documentcion en formato markdown)
    2.  Registrará automáticamente un **Prefijo Único** (ej. `AUTH`, `TPGO`) en `.quinoto-spec/prefix-registry.md`.
    3.  Generará el archivo base de la propuesta, incluyendo el campo `Servicios Afectados` para arquitecturas distribuidas.
- **Ejemplo**: `"Crea una propuesta técnica con @quinotospec.create-proposal. El objetivo es migrar la pasarela de pagos a Stripe."`

### 3. Generar Historias de Usuario
Desglosa la propuesta en requerimientos de valor.

- **Comando**: `@quinotospec.create-user-histories`
- **Parámetro**: Nombre de la carpeta de la propuesta (slug).
- **Output**: `.quinoto-spec/proposals/{slug}/user-histories.md`.
- **Detalle**: Crea items funcionales con su correspondiente columna `Servicio` para trazabilidad multi-repositorio.
- **Ejemplo**: `"Genera historias de usuario con @quinotospec.create-user-histories referenciando la propuesta 'stripe-migration'."`

### 4. Generar Tareas Técnicas
Convierte historias en pasos ejecutables para el desarrollador (o el agente).

- **Comando**: `@quinotospec.create-tasks`
- **Parámetro**: ID de la Historia de Usuario (ej. `US-AUTH-01`).
- **Output**: `.quinoto-spec/proposals/{slug}/{US_ID}_tasks.md`.
- **Detalle**: Crea una lista de chequeo técnica con columna `Servicio` heredada de la historia de usuario.
- **Ejemplo**: `"Genera las tareas técnicas para la historia 'US-STRP-001' usando el workflow @quinotospec.create-tasks."`

### 5. Implementación (Apply)
Ejecuta las tareas una por una.

- **Comando**: `@quinotospec.apply`
- **Input**: Descripción de la tarea o ID (ej. "Implementar TSK-AUTH-001").
- **Acción**:
    1.  El agente lee el contexto (Discovery + Propuesta).
    2.  Genera un branch (si aplica).
    3.  Escribe el código y los tests.
    4.  **Actualiza el Changelog automáticamente**.
- **Ejemplo**: `"Aplica la tarea 'TSK-STRP-001' usando @quinotospec.apply. Asegúrate de actualizar los tests de integración."`

### 6. Utilidades Adicionales

#### Mjolnir Refactor
Estrategia agresiva para reescribir módulos enteros con alta deuda técnica.

- **Comando**: `@quinotospec.mjolnir-refactor`
- **Acción**: Mapea impacto, analiza código legacy, genera propuesta de refactor, user stories y tareas de reemplazo paso a paso.
- **Ejemplo**: `"Aplica @quinotospec.mjolnir-refactor sobre la carpeta src/legacy-billing para migrarla a arquitectura hexagonal."`

#### Archive (Limpieza)
Mueve elementos finalizados a un estado de "archivo" para limpiar el workspace.

- **Comando**: `@quinotospec.archive`
- **Parámetro**: `TARGET` (Slug de propuesta, nombre de archivo de historias o tareas).
- **Acción**: Mueve el elemento a la carpeta `_archived/`.
- **Ejemplo**: `"Ejecuta @quinotospec.archive sobre la propuesta 'stripe-migration' porque ya se verificó en PROD."`

#### Read PDF
Ingesta documentación externa en formato PDF para darle contexto al agente.

- **Comando**: `@quinotospec.readpdf`
- **Acción**: Lee un PDF, extrae el texto usando Python/pdfplumber, y lo guarda en `.quinoto-spec/docs/`.
- **Ejemplo**: `"Lee el archivo ./docs/api-guide.pdf con @quinotospec.readpdf y guárdalo como 'guia-api'."`

#### Dashboard de Proyecto (Status)
Mantén una visión clara del progreso y el valor generado.

- **Comando**: `@quinotospec.status`
- **Acción**: Escanea propuestas y changelog, calculando velocidad de IA, alertas de bloqueos y descubrimientos caducados.
- **Ejemplo**: `"Muestra cómo venimos ejecutando @quinotospec.status para ver la velocidad del último sprint."`

#### Refresh Discovery
Actualiza solo los archivos de discovery afectados por cambios recientes.

- **Comando**: `@quinotospec.refresh-discovery`
- **Acción**: Detecta qué archivos cambiaron desde la `Discovery Date` y actualiza únicamente las partes impactadas.
- **Ejemplo**: `"Actualiza el discovery de la arquitectura porque metimos cambios en la BD, usa @quinotospec.refresh-discovery."`

#### Dependency Graph
Mapea las dependencias inter-servicio y detecta contract drift.

- **Comando**: `@quinotospec.dependency-graph`
- **Acción**: Analiza llamadas HTTP cross-servicio y recursos compartidos. Genera un mapa Mermaid y alerta sobre endpoints desalineados.
- **Ejemplo**: `"Corre @quinotospec.dependency-graph para ver qué servicios dependen todavía del viejo MS de usuarios."`

#### Code Review
Revisa un branch contra los criterios de aceptación.

- **Comando**: `@quinotospec.review`
- **Acción**: Verifica alineación con el DoD, tests, convenciones de stack (archivos permitidos) antes de mergear.
- **Ejemplo**: `"Haz un code review a la rama 'feature/TSK-STRP-001' usando @quinotospec.review."`

#### Sprint Planning
Genera un plan de acción a corto plazo y lo organiza en carpetas dedicadas.

- **Comando**: `@quinotospec.sprint`
- **Acción**: 
    1. Genera un folder `.quinoto-spec/sprints/sprint-{{ID}}/` para aislar el plan.
    2. Asigna tareas desde propuestas activas según `sprint-config.yml`.
    3. Soporta **priorización de propuestas**, **componentes permitidos** por desarrollador y **ownership** de componentes para una asignación precisa.
- **Ejemplo**: `"Arma el sprint para las próximas 2 semanas con @quinotospec.sprint."`

#### Distribute Proposal
Explota los artefactos de una propuesta central hacia los microservicios, ahora organizado por sprints.

- **Comando**: `@quinotospec.distribute`
- **Parámetros**: `SPRINT_ID`, `PROPOSAL_SLUG`.
- **Acción**: Lee la columna `Servicio` de historias y tareas filtradas por el sprint indicado, y copia los archivos a `<servicio>/.quinoto-spec/sprints/sprint-{{ID}}/proposals/{{SLUG}}/`.
- **Ejemplo**: `"Distribuye las tareas de 'auth-standardization' para el sprint 1 usando @quinotospec.distribute."`

### 7. Habilidades (Skills)

El agente cuenta con "Skills" especializadas que ejecutan tareas complejas de forma autónoma:

- **Generate Github Branch**: Crea branches siguiendo el estándar `feature/{{TASK_ID}}-descripcion-kebab-case` automáticamente, detectando la rama base y haciendo push.
- **File Creation**: Estandariza la creación de archivos, asegurando que scripts temporales y documentos sigan las normas.
- **Mark Done**: Automatiza el cierre de tareas. Marca el checkbox `[x]`, mueve artefactos completados a `_archived/`, y actualiza el changelog automáticamente.
- **Read PDF**: Motor de extracción de texto para documentos PDF. Genera un script temporal, extrae el contenido y lo guarda en `.quinoto-spec/docs/`.
- **Update Changelog**: Mantiene el `docs/quinoto-spec-changelog.md` actualizado con cada cambio relevante, calculando tiempos y categorizando cambios.
- **Validate**: Ejecuta checks de sistema (discovery, prefix-registry, changelog, propuestas) como precondición antes de workflows críticos.

## Mantenimiento y Reglas

### Integridad de la Especificación (Agent Only)
**CRÍTICO**: El contenido de la carpeta `.quinoto-spec/` y el archivo `docs/quinoto-spec-changelog.md` son administrados **EXCLUSIVAMENTE** por el agente.
- **NUNCA** edites estos archivos manualmente.
- Si necesitas corregir o actualizar algo en la especificación, pídeselo al agente (ej. "Actualiza el changelog", "Refina la propuesta").
- Esto garantiza que la "memoria" del sistema no se corrompa por intervenciones humanas no registradas.

### Changelog Automatizado
Los workflows usan la skill `quinotospec-update-changelog` para mantener el historial ordenado y consistente. El agente debe ser el único escritor de este archivo.

### Reglas del Proyecto (Compulsory Rules)
El sistema impone reglas estrictas para garantizar la calidad. El agente tiene instrucciones de detenerse si no se cumplen:

#### 1. Gestión del Changelog
- **Regla**: Nunca editar manualnente.
- **Acción**: El agente usará siempre la skill `quinotospec-update-changelog` tras completar tareas relevantes.

#### 2. Gestión de Prefijos e IDs
- **Regla**: Todo trabajo debe estar trazado bajo una Propuesta con un Prefijo registrado.
- **Acción**: Antes de crear historias o tareas, el agente verificará `.quinoto-spec/prefix-registry.md`. Si el prefijo no existe, no se permite avanzar.

#### 3. Product Agreement Check (BLOQUEANTE)
- **Regla**: No se arranca una propuesta sin definición de producto.
- **Acción**: Antes de crear una propuesta, el agente **lee** `.quinoto-spec/discovery/07-product-and-agreements.md`.
    - Si el archivo está vacío o tiene placeholders -> **STOP**.
    - El agente te dirá: *"No puedo crear la propuesta porque no se han definido los Acuerdos de Producto"*.
    - **Solución**: Debes llenar ese archivo con la Visión, DoR y DoD antes de pedir la propuesta.

---

## Flujo de Interacción (Humano vs Agente)

```mermaid
graph TD
    classDef human fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef agent fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;
    classDef artifact fill:#fff3e0,stroke:#e65100,stroke-width:1px,stroke-dasharray: 5 5;

    H(👤 Human):::human
    A(🤖 Agent):::agent

    subgraph Discovery ["Fase 1: Contexto"]
    H -->|1. Solicita Contexto| A
    A -->|2. Genera Docs| D1[Discovery Docs]:::artifact
    H -.->|3. Define Acuerdos| D2[Product Agreements]:::artifact
    end

    subgraph Planning ["Fase 2: Estrategia"]
    H -->|4. Solicita Propuesta| A
    A -->|5. Crea| P[Technical Proposal]:::artifact
    P -->|6. Revisa y Aprueba| H
    H -->|7. Solicita Planif.| A
    A -->|8. Genera| T[Histories & Tasks]:::artifact
    end

    subgraph Execution ["Fase 3: Desarrollo"]
    T -->|9. Elige Tarea| H
    H -->|10. Comando Apply| A
    A -->|11. Escribe Código| C[Codebase]:::artifact
    A -->|12. Auto-Actualiza| L[Changelog]:::artifact
    end
```

---

## Licencia

Este proyecto se distribuye bajo la licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

`QuinotoSpec` es un proyecto de código abierto y las contribuciones son bienvenidas.
