---
name: quinotospec.update-agents
description: Regenera AGENTS.md desde config.yaml y el inventario activo del proyecto.
---

# Workflow: Update Agents

Mantiene el archivo de referencia del proyecto alineado con su configuración real.

## Pasos

1. Verifica `.quinoto-spec/config.yaml`; si falta, crea uno desde `config-template.yml` y solicita completar los valores del stack.
2. Lee el registro `.quinoto-spec/extensions/.registry` y el inventario de workflows/skills/rules.
3. Ejecuta:

```bash
python3 agent-dist/skills/quinotospec-update-agents/update_agents.py \
  --root . --config .quinoto-spec/config.yaml --write
```

4. Verifica el resultado:

```bash
python3 agent-dist/skills/quinotospec-update-agents/update_agents.py \
  --root . --config .quinoto-spec/config.yaml --check --json
```

5. No edites `AGENTS.md` manualmente; registra la regeneración con `quinotospec-update-changelog`.

## Errores

- Placeholder sin resolver: corrige `config.yaml` y vuelve a ejecutar.
- Config ausente o inválida: no generes un archivo parcial.
- Cambio en inventory/extensions: vuelve a ejecutar el comando.
