# QuinotoSpec Class System (Falange Edition)

El **Class System** introduce roles especializados para los agentes, permitiendo una colaboración estructurada en "formación cerrada".

## Roles

### 🔍 Scout (Explorador)
- **Fase**: Discovery / Reconocimiento.
- **Misión**: Mapear el terreno, identificar dependencias y detectar riesgos técnicos antes de proponer cambios.
- **Workflows Clave**: `@quinotospec.discovery`, `@quinotospec.dependency-graph`, `@quinotospec.refresh-discovery`.

### 📜 Skald (Cronista)
- **Fase**: Estrategia / Comunicación.
- **Misión**: Traducir requerimientos de negocio a especificaciones técnicas y mantener la coherencia de la documentación.
- **Workflows Clave**: `@quinotospec.create-proposal`, `@quinotospec.create-user-histories`, `quinotospec-update-changelog`.

### 🛠️ Blacksmith (Herrero)
- **Fase**: Implementación / Refuerzo.
- **Misión**: Transformar especificaciones en código sólido, tests y refactors de alta calidad.
- **Workflows Clave**: `@quinotospec.create-tasks`, `@quinotospec.apply`, `@quinotospec.mjolnir-refactor`.

## Triggers (Comandos)

Para activar a los agentes en sus respectivos roles, utiliza los siguientes comandos:

- **`@quinotospec.scout`**: Inicia fase de reconocimiento.
- **`@quinotospec.skald`**: Inicia fase de diseño y especificación.
- **`@quinotospec.blacksmith`**: Inicia fase de forja y construcción.
- **`@quinotospec.warband`**: Inicia la **Formación Falange** (Scout -> Skald -> Blacksmith).

## Formación Cerrada (Shield Wall)
Los agentes operan en una secuencia de validación cruzada:
1.  **Scout** valida el contexto.
2.  **Skald** define la intención.
3.  **Blacksmith** forja la ejecución.
