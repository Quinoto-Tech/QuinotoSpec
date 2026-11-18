---
name: Delta Spec — command-layer
---

# Delta Spec: command-layer — command-to-skill-delegation

**Contract Version:** 1
**Proposal ID:** 2026-11-18-command-to-skill-delegation
**Propuesta:** Command-to-Skill Delegation
**Prefijo:** SKDP-m2q8
**Fecha de Creación:** 2026-11-18
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Comando como stub de delegación
Cada uno de los 49 comandos (`agent-dist/workflows/quinotospec.<name>.md`) SHALL contener únicamente: frontmatter de metadatos descriptivos y un cuerpo de delegación que indique leer la skill pareada `quinotospec-<name>/SKILL.md`, pasar `$ARGUMENTS` como contexto y aplicar su contenido textualmente, sin resumirlo ni reescribirlo.

#### Scenario: invocación en repo fuente
- **GIVEN** un desarrollador en el checkout del paquete
- **WHEN** invoca `/quinotospec.status`
- **THEN** el comando resuelve `agent-dist/skills/quinotospec-status/SKILL.md` y el agente ejecuta ese prompt con los argumentos dados.

#### Scenario: invocación tras instalación global
- **GIVEN** un proyecto sin `agent-dist/` y una instalación global de OpenCode
- **WHEN** invoca el comando `status`
- **THEN** el stub resuelve `~/.config/opencode/skills/quinotospec-status/SKILL.md` sin depender de la tool `skill` del IDE.

### Requirement: Resolución multi-IDE por archivo
El stub SHALL buscar el `SKILL.md` en este orden: layout fuente (`agent-dist/skills/`), layouts locales (`.opencode/`, `.cursor/`, `.claude/`, `.agent/`), layouts globales (`~/.config/opencode/`, `~/.cursor/`, `~/.claude/`), y SHALL detenerse con un mensaje que liste las rutas intentadas si no lo encuentra.

#### Scenario: skill ausente
- **GIVEN** una instalación incompleta sin la skill pareada
- **WHEN** se invoca el comando
- **THEN** el agente reporta las rutas buscadas y NO ejecuta un prompt alternativo improvisado.

### Requirement: Stubs generados desde plantilla única
Los 49 stubs SHALL ser generados y verificados por `scripts/generate-command-stubs.py`, de modo que difieran solo en `<skill-id>` y en el `description` del frontmatter.

#### Scenario: desviación detectada
- **GIVEN** un comando editado manualmente con prompt propio
- **WHEN** corre `generate-command-stubs.py --check` o el checker de drift
- **THEN** falla identificando el archivo desviado.

---

## MODIFIED Requirements

## REMOVED Requirements

## RENAMED Requirements
