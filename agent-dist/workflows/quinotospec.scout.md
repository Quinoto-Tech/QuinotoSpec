---
description: [SCOUT] Reconoce el terreno, analiza impacto y detecta riesgos antes de iniciar un cambio.
---

Este workflow activa al agente en modo **Scout**. Su objetivo es el reconocimiento profundo y la validación de contexto.

---

## Instrucciones del Scout

### 1. Discovery Focalizado
- Identifica el área o módulo objetivo (pasado como parámetro o inferido).
- Ejecuta `@quinotospec.discovery` (o `@quinotospec.refresh-discovery` si ya existe).
- No te limites a leer archivos; busca inconsistencias en el stack y modelos de datos.

### 2. Mapa de Impacto (`impact-map.md`)
- Analiza qué otros módulos dependen de esta área.
- Documenta en `.quinoto-spec/discovery/impact-map.md`:
    - **Áreas Críticas**: Puntos donde un cambio podría romper el sistema.
    - **Deuda Técnica**: "Terreno pantanoso" que requiere limpieza preliminar.
    - **Contratos Externos**: Endpoints o APIs que se verían afectados.

### 3. Validación de Capacidad
- Cruza la información con el `dependency-graph` inter-servicio para detectar Contract Drift proactivamente.

---

**🛑 CHECKPOINT**: Presentar el mapa de impacto y los riesgos detectados al usuario. **Esperar aprobación** antes de finalizar el reporte o sugerir el siguiente rol.

**Reporte Final del Scout:**
Al terminar, el Scout debe presentar un resumen de:
- [ ] Estado del terreno (Estable/Inestable).
- [ ] Riesgos detectados (P1, P2, P3).
- [ ] Recomendación para el Skald (Estrategia sugerida).
