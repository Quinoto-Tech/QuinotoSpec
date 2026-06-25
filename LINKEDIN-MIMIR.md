# 🧠 Yggdrasil + Mímir — QuinotoSpec v2.4.0

Hace un mes lancé QuinotoSpec v2.1.0 "Yggdrasil" — un framework de 33 workflows y 27 skills que transforma cómo los agentes de IA trabajan en proyectos de software.

Yggdrasil es el árbol que conecta los 9 mundos en la mitología nórdica. Estructura. Orden. Conexión. El ciclo Proposal First — Discovery, Propuesta, User Stories, Tareas, Apply — es la columna vertebral que sostiene el proyecto.

Pero debajo de Yggdrasil hay un pozo. Y en ese pozo está **Mímir**.

---

## El pozo debajo del árbol

En la mitología nórdica, Mímir es la figura de la sabiduría. Su cabeza cercenada fue preservada junto al pozo que está debajo de Yggdrasil. Odín sacrificó su ojo para beber de esas aguas y ver las conexiones entre todas las cosas.

Mímir no reemplaza a Yggdrasil. Mímir **lo alimenta**. La estructura del árbol ya estaba. Lo que faltaba era inteligencia sobre esa estructura.

Eso es lo que suma esta release.

---

## Las 3 capacidades de Mímir

### 1. Delta Specs — La memoria

Hasta ahora, cada propuesta en QuinotoSpec reescribía la especificación completa. En un proyecto brownfield con 50 endpoints y 3 servicios, eso es ruido puro.

**Delta Specs** invierte el modelo: las propuestas solo expresan lo que **cambia**.

- `ADDED` — nuevos requerimientos
- `MODIFIED` — requerimientos existentes que evolucionan (con `Was:` y `Reason:`)
- `REMOVED` — lo que se depreca (con `Migration:`)
- `RENAMED` — clarificación de nomenclatura

Al archivar, el engine de merge aplica los deltas al source of truth canónico en `specs/`. Yggdrasil ejecuta el ciclo. Mímir recuerda qué cambió.

---

### 2. Artifact DAG — Las conexiones ocultas

Los artefactos de QuinotoSpec tienen dependencias implícitas — proposal → delta-specs → user-stories → tasks → apply. Pero nunca fueron validadas. Odín sacrificó un ojo por esto.

El **Artifact Dependency Graph Engine** las hace explícitas en un schema YAML. El engine lee el schema, escanea el filesystem, y responde: **¿qué está listo y qué está bloqueado?**

```
user-stories → 🔒 blocked (espera: design)
tasks        → 🔒 blocked (espera: user-stories)
design       → ⏳ ready
```

El dashboard de `@quinotospec.status` ahora incluye el estado de artefactos por propuesta activa. Yggdrasil conecta las ramas. Mímir revela lo que depende de qué.

---

### 3. Party Mode — El consejo

QuinotoSpec tiene 9 agentes especializados. Hasta ahora trabajaban en solitario. **Party Mode** los sienta a todos en la misma mesa.

Pero lo mas interesante no es convocarlos manualmente — es que el consejo se integra directamente en el flujo de trabajo:

```
@quinotospec.create-proposal "Refactorizar capa de autenticacion" --party
@quinotospec.create-rfc "Feature flags en staging" --party
```

El flag `--party` hace que, antes de redactar la propuesta o el RFC, se convoque automaticamente a los agentes relevantes. El Architect defiende acoplamiento controlado. El Security Auditor exige API gateway desde dia 1. El Test Writer pregunta como testeas un race condition bajo carga. Las conclusiones del debate alimentan directamente el documento final — sin pasos extra.

Dos modos: **Voiced** (rapido, el orquestador voicea a los agentes en un solo hilo) o **Spawned** (profundo, agentes independientes con contexto aislado, 3 rondas). El orquestador monitorea groupthink. Si todos estan de acuerdo, inyecta una perspectiva contrarian.

Yggdrasil da los agentes. Mimr les da voz. Y `--party` los sienta en la mesa sin que tengas que convocarlos.

---

## El stack actual

```
36 workflows, 29 skills, 12 reglas, 9 agentes
Yggdrasil (estructura) + Mímir (inteligencia)
Party Mode integrado en create-proposal y create-rfc via --party
```

---

## Lo que sigue

Yggdrasil ya estaba. Mímir ya está debajo. **Falta la Fase 1** — TDD con enforcement, debugging sistemático, bootstrap automático al iniciar sesión. Las Iron Laws de @obra/superpowers que van a transformar cómo los agentes escriben código.

Pero por ahora — el árbol tiene raíces profundas y el pozo está lleno.

---

**Repo:** [github.com/Quinoto-Tech/QuinotoSpec](https://github.com/Quinoto-Tech/QuinotoSpec)

*#AI #SoftwareDevelopment #DeveloperTools #OpenSource #Agents #QuinotoSpec*
