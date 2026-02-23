# 🪓 QuinotoSpec: Berserker Edition Launch

## Bienvenida a la Era de la Orquestación

¡Bienvenido al **Modo Berserker**! Lo que acabamos de hacer no es solo una actualización de archivos; es un cambio de paradigma en cómo tu QuinotoSpec entiende y evoluciona tu código. Pasamos de un agente que leía reglas estáticas a un sistema vivo de **Subagentes Especializados** con **Memoria Institucional**. QuinotoSpec ahora no solo "hace" cosas, sino que "sabe por qué" las hace y tiene un equipo de expertos (lógicos) para cada etapa del desarrollo. Es el fin de la IA amnésica y el comienzo de un socio de desarrollo que escala con la complejidad de tu proyecto.

---

## 🚀 ¿Qué puede hacer QuinotoSpec ahora?

Ahora, tu asistente no es un "generalista" que se marea con archivos grandes, sino una **Línea de Ensamblaje de Expertos**:

- **Ahora puede delegar**: El Orchestrator divide el trabajo y llama al experto adecuado.
- **Ahora puede enfocar su atención**: Los subagentes operan con "contexto quirúrgico", leyendo solo lo que necesitan para su tarea específica (cero ruido, cero alucinaciones).
- **Ahora puede recordar**: Gracias a **Engram**, las decisiones que tomaste hace tres semanas no se pierden cuando se limpia el historial del chat.
- **Ahora es reactivo**: Las habilidades (Skills) se activan solas mediante **Triggers** y **Scopes**; si tocas el frontend, se cargan las reglas de UI; si tocas el backend, se cargan las de API.
- **Ahora es transparente**: Al final de cada intervención, el Orquestador te listará exactamente qué **Expertos** (Skills) participaron en la tarea para que sepas qué criterios se aplicaron.
- **Ahora es auditable**: Cada decisión técnica queda registrada en un sistema de búsqueda de texto completo.

---

## 🛠️ ¿Cómo lo resolvimos técnicamente?

Para lograr esta potencia, hemos rediseñado la arquitectura siguiendo estos pilares:

### 1. El Panteón de Roles (Subagentes)
Hemos creado una estructura de **Prompts de Sistema Dinámicos** en `agent-dist/roles/`. Cada rol tiene una misión sagrada:
- **Explorer**: Escanea y mapea la realidad actual (`discovery`).
- **Proposer & Designer**: Crean la visión estratégica y arquitectónica.
- **Implementer**: El guerrero que escribe el código en hilos aislados.
- **Verifier**: El guardián que asegura que el *Definition of Done* se cumpla antes de cerrar.

### 2. Sistema de Skills Especializadas (Lazy Loading)
Refactorizamos todas las habilidades en `agent-dist/skills/` agregando metadatos YAML. 
- **Solución**: Usamos `triggers` (palabras clave) y `scopes` (rutas de archivos). Esto permite que el agente inyecte el conocimiento justo a tiempo, optimizando el uso de tokens y manteniendo la precisión.

### 3. Engram: La Base de Datos de la Memoria
Es el componente más revolucionario. Resolvemos la "amnesia" de los LLMs mediante persistencia física.
- **La Tecnología**: Una base de datos **SQLite** con el motor **FTS5** (Full Text Search) ubicada en `.quinoto-spec/engram.db`.
- **Cómo lo usamos**: 
    1. **Registro**: Cada vez que se cierra una tarea, el `Implementer` genera un Summary resumido que se inserta en la base de datos.
    2. **Búsqueda**: Creamos la skill `@quinotospec.memory-search` que usa un script de Python (`search.py`) para interrogar a la base de datos de forma ultrarrápida.
    3. **Sincronización**: Para que tu equipo también tenga esta memoria, Engram exporta "chunks" JSON hasheados que se suben a Git, permitiendo que la inteligencia sea compartida.

---

## 🧠 Entendiendo Engram (Tu Biblioteca Técnica)

Imagina que **Engram** es el diario de vida técnico de tu proyecto. En lugar de confiar en que la IA recordará un mensaje de hace 10 días, QuinotoSpec escribe esa decisión en piedra (bueno, en SQLite).

- **¿Cuándo se usa?**: Cuando el Orchestrator detecta una pregunta sobre el pasado ("¿Por qué usamos este patrón?") o cuando necesitas asegurar coherencia arquitectónica.
- **¿Qué guarda?**: Decisiones de diseño, soluciones a bugs críticos, hallazgos de arquitectura y lecciones aprendidas.
- **Tu superpoder**: Puedes usar `@quinotospec.memory-query "término"` para que la IA escanee toda la historia del proyecto en milisegundos y te traiga la respuesta exacta, citando fecha y contexto.

---

## 🎨 Un Ejemplo Real

La "personalidad" de tus expertos se define mediante **Skills Especializadas**. Aquí te mostramos cómo podrías crear un experto en UI para que QuinotoSpec trabaje con rigor visual:

**Archivo:** `agent-dist/skills/expert-ui/SKILL.md`

```yaml
---
name: UI-Visual-Expert
description: Experto en diseño premium, animaciones y accesibilidad.
trigger: ["componente", "estilo", "css", "layout", "visual"]
scope: ["src/components/**", "src/styles/**"]
tools: ["view_file", "edit_file"]
---

# Reglas del Experto UI
1. **Estética Premium**: Siempre sugieres el uso de gradientes suaves y micro-animaciones.
2. **Prohibición**: Nunca permitas el uso de colores hexadecimales puros; usa siempre variables de CSS.
3. **Accesibilidad**: Es obligatorio que cada componente tenga etiquetas ARIA.
```

**¿Cómo funciona la magia?**
Si pides: *"Agrega un botón al header"*, el **Orchestrator** detecta el Trigger `"botón"` y el Scope `"src/components"`. Automáticamente, el sistema le "inyecta" al subagente **Implementer** esta personalidad. En ese hilo de chat, el agente **se convierte** en ese experto con este rigor específico.

**La Memoria (Engram) como refuerzo**
Si se toma una decisión importante (ej: "A partir de ahora, todo botón debe tener 8px de border-radius"), esa decisión se guarda en Engram.

La próxima vez que cualquier subagente trabaje en UI, consultará la memoria y recordará esa regla que se definió en el pasado, manteniendo la coherencia sin que tú tengas que repetírselo.
---

## ⚔️ Comandos de la Berserker Edition

Aquí tienes el arsenal de comandos actualizado para operar en este nuevo modo:

| Comando | Agente / Rol | Qué Hace |
| :--- | :--- | :--- |
| `@quinotospec.discovery` | **Explorer** | Escaneo profundo de la codebase. Genera el mapa del "Estado del Arte". |
| `@quinotospec.create-proposal` | **Proposer** | Crea la estructura de una nueva iniciativa técnica con prefijo único. |
| `@quinotospec.memory-init` | **System** | (NUEVO) Inicializa la base de datos `engram.db` para que el sistema empiece a recordar. |
| `@quinotospec.memory-search` | **System** | (NUEVO) Busca términos en la memoria institucional (decisiones, bugs, arquitectura). |
| `@quinotospec.apply` | **Implementer** | Ejecuta una tarea técnica (TSK) en un hilo de contexto aislado y limpio. |
| `@quinotospec.status` | **Orchestrator** | Calcula el progreso real del proyecto y el tiempo de vida (Human Time) ahorrado. |

---

**QuinotoSpec Berserker Edition** es el resultado de llevar la metodología *OpenSpec* al límite de lo que la IA puede hacer hoy. Ahora, eres el General de un ejército de subagentes listos para conquistar cualquier codebase. ⚔️
