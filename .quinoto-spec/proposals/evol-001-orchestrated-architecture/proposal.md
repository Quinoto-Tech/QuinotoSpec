# Propuesta Técnica: Evolución a Arquitectura Orquestada (EVOL-001)

## Contexto y Motivación
La arquitectura monolítica actual de los agentes de IA presenta limitaciones de contexto y precisión a medida que los proyectos crecen. Esta propuesta busca evolucionar QuinotoSpec hacia un modelo de **Orquestador-Subagentes** con memoria persistente, siguiendo los principios de la "Berserker Edition".

## Objetivos (Tier 1)
- Implementar el patrón **Orchestrator-Workers**.
- Reducir el ruido de contexto mediante **Subagentes Efímeros**.
- Implementar **Memoria Persistente** via Engram (SQLite) y MCP.
- Refactorizar el sistema de **Skills** para carga bajo demanda (Lazy Loading).

## Diseño de la Solución

### 1. El Orchestrator
El agente principal actuará como el "Cerebro" que delega tareas a subagentes especializados. Su única responsabilidad es mantener el estado global y coordinar el flujo de trabajo.

### 2. Subagentes Especializados
- **Explorer**: Escaneo de codebase (Discovery).
- **Proposer/Designer**: Creación de especificaciones y arquitectura.
- **Implementer**: Ejecución técnica en hilos aislados.
- **Verifier**: Validación de cumplimiento de tareas.

### 3. Sistema de Skills Dinámico
Las skills se cargarán basándose en:
- `Trigger`: Palabras clave en la intención.
- `Scope`: Directorios afectados.

### 4. Memoria (Engram)
Uso de una base de datos SQLite local para registrar decisiones técnicas, permitiendo la recuperación de contexto tras la compactación de hilos.

## Impacto
- **Positivo**: Mayor precisión, menor consumo de tokens en tareas largas, mejor trazabilidad.
- **Riesgo**: Complejidad inicial en la configuración de subagentes.

## Próximos Pasos (Historias de Usuario)
1. Definir los prompts de sistema para cada rol de subagente.
2. Actualizar los archivos de workflow para invocar subagentes.
3. Implementar el motor de búsqueda en Engram.
