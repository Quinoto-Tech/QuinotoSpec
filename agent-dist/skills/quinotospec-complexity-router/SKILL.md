---
name: quinotospec-complexity-router
description: Routing adaptativo por complejidad — clasifica un cambio en Quick Fix, Simple, Complex o Enterprise y deriva al workflow y gates correspondientes.
---

# Skill: Quinotospec Complexity Router

> No todos los cambios merecen el mismo ceremonial. Este router decide cuanto proceso aplicar segun el alcance real, sin dejar de proteger los gates criticos.

## Cuando usar

- Al inicio de `/quinotospec.apply` o `/quinotospec.quick-dev`
- Antes de abrir una propuesta: validar si el cambio realmente la necesita
- Cuando el usuario pide "algo rapido" y hay que decidir sin degradar calidad
- Para justificar ante revision por que un cambio no requiere user stories

## Invocacion

```bash
python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files 2 --services 1 --json
python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files 1 --description "typo en README"
python3 -B agent-dist/skills/quinotospec-complexity-router/router.py --files 8 --services 2 --auth --json
```

## Tracks

| Track | Profundidad | Gatillo | Workflow |
|-------|-------------|---------|----------|
| **Quick Fix** | Spec minima -> implementacion directa | `<=1` archivo, `1` servicio, sin DB/auth/API | `/quinotospec.fix` |
| **Simple** | Tech-spec ligera -> tasks -> implementacion | `2-3` archivos, `1` servicio | `/quinotospec.quick-dev` |
| **Complex** | Spec -> design -> US -> tasks | `4-10` archivos, o DB/auth/API publica, o `>1` servicio | `/quinotospec.create-proposal` |
| **Enterprise** | SDLC completo + constitution + compliance | `>10` archivos, `>2` servicios, contexto regulado | `/quinotospec.flow` |

## Senales evaluadas

| Senal | Flag | Efecto minimo |
|-------|------|---------------|
| Archivos estimados | `--files N` | Define el track base (`1/3/10`) |
| Servicios afectados | `--services N` | `>1` -> Complex; `>2` -> Enterprise |
| Equipos involucrados | `--teams N` | `>1` -> Complex |
| Base de datos / migracion | `--db` | Complex |
| Autenticacion / autorizacion | `--auth` | Complex |
| API publica | `--public-api` | Complex |
| Compliance / regulacion | `--regulated` | Enterprise |
| Descripcion libre | `--description "..."` | Ajusta por palabras clave |
| Override manual | `--override TRACK` | Fuerza el track elegido |

Ninguna senal puede *bajar* el track por debajo del que impone otra: las senales solo escalan (`quick_fix < simple < complex < enterprise`).

## Salida `--json`

```json
{
  "schema_version": 1,
  "track": "complex",
  "label": "Complex",
  "depth": "Spec -> design -> US -> tasks -> implementacion",
  "needs_proposal": true,
  "recommended_workflow": "/quinotospec.create-proposal",
  "gates": ["tdd", "verify-before-done", "validate", "review"],
  "signals": {"files": 8, "services": 2, "db": false, "auth": true},
  "rationale": ["..."]
}
```

## Reglas

- El router solo recomienda: el usuario puede forzar `--override` y la decision queda en el `rationale`.
- `enterprise` nunca omite gates de constitution, evidencia o aprobacion humana.
- Si el cambio toca seguridad, datos o API publica, el minimo es `complex` aunque sea un solo archivo.
- El resultado debe registrarse en el contexto del workflow elegido (tech-spec o propuesta).
