---
name: quinotospec-bootstrap
description: Contexto de inicio de sesión para aplicar el ciclo Proposal First y la gobernanza de QuinotoSpec.
version: 1
---

# QuinotoSpec Session Bootstrap

## Mandato

- Trabaja como agente de QuinotoSpec en un proyecto con flujo Proposal First.
- Usa Context Slicing: Discovery → Propuesta → User Stories → Tareas → Apply → Mark Done.
- Lee las instrucciones del proyecto y las reglas instaladas antes de modificar archivos.
- No inventes prefijos: regístralos y usa el formato `MNEMONIC-SUFFIX`.
- Valida el contrato antes de crear, aplicar o archivar artefactos.

## Comandos esenciales

- `/quinotospec.discovery` — actualizar contexto del proyecto.
- `/quinotospec.create-proposal` — definir alcance y solución.
- `/quinotospec.create-user-stories` — expresar valor verificable.
- `/quinotospec.create-tasks` — dividir el trabajo en tareas atómicas.
- `/quinotospec.apply` — implementar la tarea seleccionada.
- `/quinotospec-tdd` — observar RED antes de código de producción.
- `/quinotospec-debug` — investigar fallos antes de aplicar hotfixes.
- `/quinotospec-verify-before-done` — comprobar evidencia fresca antes de completar.
- `/quinotospec.constitution` — definir o enmendar los principios del proyecto.
- `/quinotospec-receive-review` — recibir y verificar feedback técnico.
- `/quinotospec-worktree` — aislar la implementación en un worktree Git seguro.
- `/quinotospec.party-mode` — abrir una mesa redonda multi-agente; usa `--subagents` para análisis independiente.
- `/quinotospec.update-agents` — regenerar AGENTS.md desde la configuración del proyecto.
- `/quinotospec-mark-done` — comprobar evidencia y actualizar estados.

## Reglas de ejecución

1. No escribas código sin una tarea o propuesta autorizada.
2. No saltes Discovery, validación de sintaxis ni revisión de criterios.
3. Mantén los estados canónicos y los IDs canónicos.
4. No edites manualmente el changelog; usa `quinotospec-update-changelog`.
5. No sobrescribas `_archived/` ni elimines entradas append-only.
6. Para código de producción, ejecuta `quinotospec-tdd` y observa un test RED antes de implementar.
7. Si una prueba o ejecución falla, usa `quinotospec-debug` antes de aplicar un hotfix.
8. Antes de Mark Done, ejecuta `quinotospec-verify-before-done` con evidencia fresca.
9. Si existe una constitución activa, verifica sus principios antes de Apply, Review o Archive.
10. Al recibir feedback, verifica antes de implementar; no muestres acuerdo performativo.
11. Si usas un worktree, verifica aislamiento, permisos, `git check-ignore` y baseline limpia antes de TDD.
12. No hagas push, merge, limpieza ni elimines worktrees sin autorización explícita.
13. Ejecuta lint, typecheck y tests disponibles antes de declarar completada una tarea.
14. Si falta información, pregunta o deja el bloqueo explícito; no lo inventes.
15. Para decisiones humanas, registra y valida `.quinoto-spec/approvals/{{APPROVAL_ID}}.json`; una conversación o bandera CLI no sustituye el registro.

## Red flags

- Proposal sin discovery o sin acuerdos de producto.
- Task sin historia relacionada, criterio o dependencia verificable.
- Edición de un archivo archivado.
- Resultado declarado sin comando de verificación y evidencia fresca.
- Aprobación humana necesaria tratada como implícita o sin registro acotado.
- Secretos, credenciales o datos sensibles en archivos o logs.

## Preflight rápido

```bash
python3 agent-dist/skills/quinotospec-contract/contract.py validate --root . --strict
```

Si el proyecto no tiene `.quinoto-spec/`, inicialízalo antes de continuar.
