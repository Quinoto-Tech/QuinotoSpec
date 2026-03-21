---
description: [WARBAND] Ejecuta la "Formación Falange" coordinando al Scout, Skald y Blacksmith en secuencia.
---

Este workflow activa la **Formación Falange**. El agente operará pasando por los tres roles especializados para completar una iniciativa de inicio a fin.

---

## Fases de la Warband

### Fase 1: El Scout 🔍
- **Acción**: Identifica riesgos y áreas de impacto.
- **Resultado Esperado**: `impact-map.md` y reporte de riesgos.
- **🛑 CHECKPOINT**: Presentar hallazgos al usuario y **esperar aprobación** para invocar al Skald.

### Fase 2: El Skald 📜
- **Acción**: Diseña la solución y redacta las especificaciones.
- **Resultado Esperado**: `proposal.md` y `user-histories.md`.
- **🛑 CHECKPOINT**: Presentar propuesta y historias al usuario y **esperar aprobación** para invocar al Blacksmith.

### Fase 3: El Blacksmith 🛠️
- **Acción**: Genera las tareas y ejecuta el código.
- **Resultado Esperado**: Código funcional, tests pasados y `changelog` actualizado.
- **🛑 CHECKPOINTS**: Seguir el protocolo de autorización **tarea por tarea** definido en `quinotospec.blacksmith.md`.

---

## Reglas de la Warband
1.  **Validación de Paso**: El agente debe solicitar confirmación al usuario al final de cada fase (Scout → Skald y Skald → Blacksmith).
2.  **Contexto Compartido**: Cada rol debe leer los artefactos generados por el anterior para mantener la coherencia.
3.  **Registro Único**: Todo el proceso se traza bajo el mismo prefix de propuesta.

---

**Reporte de Misión:**
Al finalizar la Warband, se entrega el feature completo, documentado y verificado.
