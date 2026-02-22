# Integración de Subagentes y Memoria Persistente en QuinotoSpec

## 1. Fundamentos de la Nueva Arquitectura Orquestada

### 1.1. Del Agente Monolítico al Patrón Orchestrator-Workers
La evolución de QuinotoSpec marca el abandono definitivo del modelo de agente monolítico. La nueva arquitectura adopta el paradigma **Orchestrator-Workers**.

*   **Orchestrator**: Encargado de delegación, supervisión y visión global.
*   **Subagentes (Workers)**: Especialistas que ejecutan tareas atómicas en entornos aislados.

### 1.2. El Ciclo de Vida del Subagente Efímero
1.  **Nace**: Inicialización con contexto cero.
2.  **Ejecuta**: Recibe instrucción y Skills necesarias.
3.  **Reporta**: Genera un **Summary** técnico (Qué se hizo, Qué se aprendió, Qué queda pendiente).
4.  **Muere**: Sesión destruida. El Orchestrator solo absorbe el Summary.

## 2. Roles de Subagentes Especializados

### 2.1. Discovery (Explorer)
Escaneo integral de la codebase.

### 2.2. Planning (Proposer, Designer, Task Planner)
- **Proposer**: Define "qué" y "por qué".
- **Designer**: Decisiones arquitectónicas.
- **Task Planner**: Desglose en TSK atómicas.

### 2.3. Execution (Implementer, Verifier)
- **Implementer**: Escribe código.
- **Verifier**: Validación contra DoD y especificaciones.

## 3. Sistema de Skills con Lazy Loading

Carga dinámica basada en **Triggers** y **Scopes** definidos en metadatos Markdown.

## 4. Memoria Persistente con Engram y MCP

-   **Engram**: SQLite con FTS5 para búsquedas deterministas de decisiones reales.
-   **MCP (Model Context Protocol)**: Interfaz para que agentes consuman Engram.
-   **Compactación**: Reinyección automática de decisiones clave tras pérdida de contexto histórico.

## 5. Flujo de Trabajo SDD Actualizado

Línea de ensamblaje: `Orchestrator -> Explorer -> Proposer/Designer -> Task Planner -> Implementer -> Verifier`.

## 6. Reglas de Oro

-   **Aislamiento Compulsorio**: Contexto mínimo necesario.
-   **Prohibición de Improvisación**: Reportar falta de información al Orchestrator.
-   **Product Agreement Block**: Requisito de `07-product-and-agreements.md`.
-   **Prefix Registry**: Uso mandatorio de prefijos.
-   **Changelog Integrity**: Responsabilidad única del agente.
