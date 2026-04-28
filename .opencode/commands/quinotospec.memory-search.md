# Workflow: Memory Search

Busca en la memoria persistente del proyecto.

## Pasos
1. **Identificar término**: Extrae la palabra clave de búsqueda del usuario.
2. **Ejecutar Skill**:
   ```bash
   python agent-dist/skills/quinotospec-memory-search/search.py "$TERM"
   ```
3. **Reportar**: El agente presenta los hallazgos citando el contexto histórico.
