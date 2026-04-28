# Workflow: Recording Engram

Graba una nueva decisión técnica, arquitectura o lección aprendida en la memoria persistente.

## Cuándo Usar
- Al completar una propuesta técnica significativa.
- Después de resolver un bug crítico con una solución no trivial.
- Cuando se establece una nueva convención arquitectónica.

## Pasos
1. **Identificar Hallazgo**: Resume la decisión o lección en una frase concisa.
2. **Determinar Tipo**: Elige entre `decision`, `architecture`, `bug_fix`, `lesson`.
3. **Ejecutar Grabado**:
   ```bash
   python agent-dist/skills/quinotospec-memory-search/record_memory.py --type "TIPO" --content "HALLAZGO" --prefix "PREFIX_O_TASK_ID"
   ```
4. **Verificar**: Confirma al usuario que el conocimiento ha sido persistido en Engram.
