---
description: Ayudar al desarrollador a crear agentes abstractos especializados basados en el discovery y estructura del proyecto
---

[INSTRUCCIÓN MAESTRA]

# Workflow: Agent Train

Este workflow ayuda al desarrollador a crear agentes abstractos especializados, haciendo sugerencias basadas en el discovery y la estructura del proyecto. No genera perfiles automáticamente, sino que guía y sugiere basándose en el análisis del código.

---

## Parámetros

| Parámetro | Descripción | Valores |
|-----------|-------------|---------|
| `AGENT_NAME` | Nombre del agente a crear (opcional) | Nombre especificado por el usuario |
| `--suggest` | Modo de sugerencias | Genera sugerencias basadas en análisis |
| `--edit` | Modo edición | Editar un agente existente |

---

## Flujo Principal

### Paso 0 — Refrescar Discovery

**OBLIGATORIO**: Ejecutar `quinotospec.refresh-discovery.md` para asegurar datos actualizados.

1. Ejecutar el workflow `quinotospec.refresh-discovery.md`
2. Si no existe discovery, informar al usuario y ofrecer crear uno primero.

---

### Paso 1 — Analizar Estructura del Proyecto

Escanear la estructura del proyecto para detectar áreas potenciales:

1. **Detectar estructura de directorios**:
   - Buscar en raíz y nivel 1-2
   - Identificar: `src/`, `app/`, `modules/`, `packages/`, `services/`, `apps/`, `lib/`

2. **Detectar sub-módulos**:
   - Listar directorios con código fuente
   - Identificar patrones: `auth/`, `users/`, `payments/`, `products/`, etc.

3. **Detectar stack tecnológico**:
   - Buscar: `package.json`, `go.mod`, `requirements.txt`, `pyproject.toml`, `Cargo.toml`, `pom.xml`

4. **Presentar análisis al usuario**:
   ```
   Análisis del proyecto:

   [Stack Detectado]
   - Lenguaje: {detectado}
   - Framework: {detectado}
   - Build tool: {detectado}

   [Estructura]
   - Directorios principales: {lista}
   - Sub-módulos: {lista}

   [Sugerencias de agentes]
   1. {suggestion 1}
   2. {suggestion 2}
   3. {suggestion 3}
   ```

---

### Paso 2 — Definir Agente Abstracto

Ayudar al usuario a definir el agente preguntando:

1. **Propósito del agente**:
   - ¿Qué área del proyecto cubirá?
   - ¿Qué tipo de tareas realizará?

2. **Sugerencias basadas en análisis**:
   - Proponer agentes según sub-módulos detectados
   - Proponer agentes según capas (backend, frontend, api, etc.)

3. **Loop de sugerencias**:
   - Mostrar sugerencia al usuario
   - Esperar confirmación o modificación
   - **SOLO DETENER** cuando el usuario exprese explícitamente que no quiere seguir editando, por ejemplo:
     - "ya está bien", "asÍ está bien", "listo", "no quiero más", "terminado", "ya no"
   - Si el usuario no responde o да una respuesta abierta, continuar ofreciendo sugerencias

4. **Plantilla de definición**:
   ```
   # Agente: {NOMBRE}

   ## Propósito
   {descripción del propósito}

   ## Áreas de conocimiento
   - {área 1}
   - {área 2}

   ## Convenciones sugeridas (basadas en análisis)
   - Naming: {patrón detectado}
   - Estructura: {patrón detectado}

   ## Comandos sugeridos
   - {comando 1}: {descripción}
   - {comando 2}: {descripción}
   ```

---

### Paso 3 — Generar Sugerencias

Basado en el análisis, ofrecer sugerencias concretas:

#### 3.1 Sugerencias por Área Detectada

Para cada sub-módulo o capa detectada:
- **Nombre sugerido**: `{nombre del área}`
- **Responsabilidades**: Basadas en la estructura de archivos
- **Convenciones**: Extraer naming patterns de archivos existentes

#### 3.2 Sugerencias por Stack

- **Frontend**: Componentes, hooks, estilos
- **Backend**: Controllers, services, models
- **API**: Endpoints, schemas, validators
- **Database**: Models, migrations, queries

#### 3.3 Sugerencias por Integraciones

- APIs externas detectadas
- Bases de datos usadas
- Servicios internos

---

### Paso 4 — Crear Perfil (Opcional)

Si el usuario desea guardar el agente:

1. **Crear carpeta**: `.quinoto-spec/agents/`
2. **Generar archivo**: `.quinoto-spec/agents/{AGENT_NAME}.md`
3. **Incluir**:
   - Propósito definido por el usuario
   - Áreas asignadas
   - Convenciones detectadas
   - Comandos útiles
   - Ejemplos de código

---

## Modo Edición (--edit)

Si se invoca con `--edit AGENT_NAME`, el workflow permitirá editar un agente existente.

### Paso 1 — Cargar Agente Existente

1. Buscar archivo: `.quinoto-spec/agents/{AGENT_NAME}.md`
2. Si no existe, informar al usuario y ofrecer crear uno nuevo
3. Si existe, mostrar el contenido actual al usuario

### Paso 2 — Loop de Edición

1. **Preguntar qué desea modificar**:
   - Propósito del agente
   - Áreas de conocimiento
   - Convenciones
   - Comandos
   - Agregar nuevo elemento
   - Eliminar elemento
   - Otra cosa

2. **Procesar cada cambio**:
   - Aplicar modificaciones solicitadas
   - Mostrar resultado actualizado

3. **Continuar hasta que el usuario exprese que no quiere más**: "ya está bien", "así está bien", "listo", "no quiero más", "terminado", "ya no"

### Paso 3 — Guardar Cambios

1. Sobrescribir archivo `.quinoto-spec/agents/{AGENT_NAME}.md`
2. Confirmar al usuario que los cambios fueron guardados

---

## Ejemplos de Uso

```bash
# Obtener sugerencias de agentes para el proyecto
@quinotospec.agent-train --suggest

# Crear un agente específico con ayuda
@quinotospec.agent-train --agent auth-expert

# Análisis completo y sugerencias
@quinotospec.agent-train

# Editar un agente existente
@quinotospec.agent-train --edit auth-expert

```

---

## Notas

1. El workflow **no genera perfiles automáticamente**, ayuda al usuario a crearlos.

2. Las sugerencias se basan en:
   - Estructura de directorios
   - Archivos de configuración detectados
   - Convenciones de naming observadas

3. El loop de sugerencias continúa hasta que el usuario exprese explícitamente que no quiere más, usando frases como: "ya está bien", "así está bien", "listo", "no quiero más", "terminado", "ya no".

4. El usuario tiene control total sobre la definición del agente.

5. Este workflow complementa:
   - `quinotospec.discovery`: Base de conocimiento
   - `quinotospec.refresh-discovery`: Datos actualizados
