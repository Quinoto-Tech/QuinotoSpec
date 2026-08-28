---
name: quinotospec-jormungandr
description: La Serpiente del Mundo — deteccion de ciclos en DAG de artefactos y grafo de imports. Muere mordiendose la cola, como tus dependencias.
---

# Skill: Quinotospec Jormungandr — La Serpiente del Mundo

> Jormungandr rodea Yggdrasil y se muerde la cola. Si tus artefactos hacen lo mismo, el build se ahoga.

## Cuando usar

- `validate --strict` debe fallar si hay ciclo
- Antes de `schema-fork` con nuevas dependencias
- Como gate de `create-proposal` si declara `requires` ciclico

## Invocacion

```bash
/quinotospec-jormungandr --schema .quinoto-spec/schema.yaml
/quinotospec-jormungandr --check-imports ./services
/quinotospec-jormungandr   # ambos
```

## Comportamiento

### 1. Ciclos en schema.yaml (DAG)

Lee `artifacts[].id` + `artifacts[].requires` y construye DAG. Ejecuta Kahn topological sort:

- Si sort incluye todos los nodos → `OK: DAG aciclico (N nodos, orden: ...)`
- Si queda nodo sin visitar → `CYCLE: a -> b -> c -> a` con lista de aristas del ciclo

Salida: exit 1 en ciclo, sugiere `schema-fork` para romper `requires` menor prioridad.

Implementacion: `check.py` usa `yaml` si disponible, fallback parse manual `id:/requires:` con grep+awk (sin dependencias).

### 2. Ciclos en imports (opcional, --check-imports)

Para stack Node/Python/Rust, parsea imports estaticos y detecta ciclo de archivos (solo intra-servicio). Usa `grep -r "from.*import\|require\|use "` y mismo Kahn. Reporta `WARN: ciclo potencial archivoA -> archivoB -> archivoA (verificar runtime)`.

### 3. Integracion validate

`scripts/validate-all.sh` invoca `jormungandr --schema` en modo `--strict` como paso 5. Sin strict solo warn.

## Reglas

- No requiere `pyyaml` obligatorio — fallback grep
- Solo BLOCKING en schema DAG; imports es WARNING (falsos positivos por dynamic import)
