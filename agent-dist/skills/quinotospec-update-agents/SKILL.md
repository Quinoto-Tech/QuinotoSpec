---
name: quinotospec-update-agents
description: Genera AGENTS.md dinámicamente desde config.yaml, inventario activo, extensiones y contexto de discovery.
---

> **Fuente de verdad:** esta skill contiene el prompt canónico; el comando `/quinotospec.update-agents` delega aquí por archivo.

# Skill: Update Agents

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


## Fuentes

1. `.quinoto-spec/config.yaml`.
2. Workflows y skills disponibles en el inventario.
3. `.quinoto-spec/extensions/.registry`.
4. Contexto de discovery, cuando exista.
5. `agent-dist/templates/AGENTS-template.md`.

## Uso

```bash
python3 agent-dist/skills/quinotospec-update-agents/update_agents.py \
  --root . --config .quinoto-spec/config.yaml --write

python3 agent-dist/skills/quinotospec-update-agents/update_agents.py \
  --root . --config .quinoto-spec/config.yaml --check --json
```

Usa `--inventory-root` cuando el inventario se encuentre en otro root y `--state-root` para leer extensiones del proyecto destino. El generador escribe atómicamente, conserva el archivo si no cambia y falla ante placeholders sin resolver.

## Reglas

- No editar el `AGENTS.md` generado manualmente.
- `config.yaml` es la fuente de proyecto; el template solo define estructura.
- Las extensiones se incluyen desde el registro, no desde paths arbitrarios.
- Regenerar después de init, cambiar stack, activar workflows o instalar/remover extensiones.
- Verificar con `--check` antes de cerrar una tarea.
