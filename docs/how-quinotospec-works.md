# Cómo funciona QuinotoSpec: Berserker Edition

## Introducción

**QuinotoSpec** es un framework de **Desarrollo Guiado por Especificaciones (SDD)** diseñado específicamente para potenciar la colaboración entre desarrolladores humanos y agentes de Inteligencia Artificial avanzada. 

Inspirado profundamente en la metodología **OpenSpec**, busca eliminar el "vibe coding" (codear por sensaciones) y la pérdida de contexto mediante un proceso estructurado, predecible y orquestado.

---

## Nueva Arquitectura: Orchestrator-Workers

En la versión **Berserker Edition**, QuinotoSpec evoluciona del modelo de agente monolítico a una arquitectura orquestada.

### 1. El Orchestrator
Es el agente de alta jerarquía encargado de la delegación, supervisión y mantenimiento de la visión global. Evita el ruido de la implementación para preservar su capacidad de atención.

### 2. Subagentes Especializados (Workers)
Entidades que ejecutan tareas atómicas en entornos aislados para evitar alucinaciones por saturación de contexto.

- **Explorer**: Mapea el "Estado del Arte" del proyecto (Discovery).
- **Proposer**: Define el "qué" y el "por qué" técnico y de negocio.
- **Designer**: Toma decisiones de arquitectura, interfaces y patrones.
- **Task Planner**: Desglosa el diseño en tareas técnicas (TSK) atómicas.
- **Implementer**: Escribe el código siguiendo el plan y las reglas.
- **Verifier**: Valida el cumplimiento del Definition of Done (DoD).

### 4. Búsqueda en Memoria (Memory Search)
El sistema permite recuperar recuerdos mediante el comando `@quinotospec.memory-search "término"`. El agente consulta la base de datos Engram y presenta las decisiones históricas relevantes para evitar repetir errores pasados.

### 5. Ciclo de Vida Efímero
Cada subagente sigue un ciclo estricto: **Nace** (contexto cero), **Ejecuta** (recibe instrucciones y Skills), **Reporta** (genera un Summary técnico) y **Muere** (la sesión se destruye). El Orchestrator solo absorbe el Summary quirúrgico.

---

## Fundamentos Evolucionados

### 1. Proposal First
Nunca se escribe código sin una propuesta aprobada. Esto garantiza que cada cambio tenga un propósito y diseño coherente.

### 2. Context Slicing & Lazy Loading
El contexto se "rebana" y las **Skills** se cargan bajo demanda mediante metadatos:
- **Triggers**: Palabras clave que activan la habilidad.
- **Scopes**: Directorios específicos donde la skill es válida.

---

## Memoria Persistente: Engram

Para resolver la amnesia forzada de los LLMs (límites de tokens), QuinotoSpec implementa **Engram**:
- **SQLite + FTS5**: Una base de datos local de texto completo que registra decisiones técnicas, correcciones de bugs y lecciones aprendidas.
- **Compactación Inteligente**: Ante la pérdida de contexto, el sistema reinyecta automáticamente las decisiones más relevantes extraídas de la memoria institucional.

---

## El Flujo de Trabajo SDD

1.  **Discovery (Explorer)**: Escaneo integral de la codebase.
2.  **Planning (Proposer/Designer)**: Formalización de la propuesta y arquitectura.
3.  **Tasking (Task Planner)**: Generación de TSKs vinculadas a un **Prefijo Único**.
4.  **Execution (Implementer)**: Implementación en hilos aislados.
5.  **Verification (Verifier)**: Validación final contra las especificaciones.

---

## Estructura y Reglas (Compulsory Rules)

- `.quinoto-spec/`: Almacena el cerebro (prefix-registry, proposals, memory chunks).
- `agent-dist/`: La maquinaria (workflows, skills, roles).
- **Product Agreement Block**: No se inicia nada sin acuerdos en `07-product-and-agreements.md`.
- **Integridad del Agente**: Solo el agente debe escribir en la especificación y el changelog.

---

> [!TIP]
> Al usar subagentes y memoria persistente, QuinotoSpec Berserker Edition permite escalar proyectos complejos manteniendo una precisión quirúrgica en cada cambio.
