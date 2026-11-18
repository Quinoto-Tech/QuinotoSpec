---
name: Delta Spec — installer
---

# Delta Spec: installer — validator-path-resolution

**Contract Version:** 1
**Proposal ID:** 2026-11-17-validator-path-resolution
**Propuesta:** Validator Path Resolution
**Prefijo:** VPAT-k4m7
**Fecha de Creación:** 2026-11-17
**Estado:** proposed

---

## ADDED Requirements

### Requirement: Normalización de rutas en staging
El instalador SHALL normalizar, en los archivos `.md` staged del payload (directorios `workflows`/`commands`, `skills`, `rules`, `bootstrap`, `templates`, `agents`, `config`), cada ocurrencia de `agent-dist/` (y de `agent-dist` standalone con word-boundary) por la ruta absoluta del directorio de instalación final, antes de calcular el ownership manifest y de mover el candidate a destino.

#### Scenario: instalación global de OpenCode
- **GIVEN** una ejecución de `./install.sh --opencode --global`
- **WHEN** el staging copia el payload al candidate
- **THEN** ningún `.md` bajo el candidate contiene la cadena `agent-dist/` y el bootstrap instalado referencia `~/.config/opencode/skills/...` como ruta ejecutable.

#### Scenario: idempotencia
- **GIVEN** un candidate ya normalizado
- **WHEN** `normalize_staged_paths` se ejecuta de nuevo
- **THEN** el resultado es un no-op sin errores.

### Requirement: Exclusión de código del rewrite
El instalador MUST restringir el rewrite a archivos `.md` y MUST NOT modificar `*.py`, `*.sh`, `*.js`, `*.json` ni binarios durante la normalización.

#### Scenario: script Python staged intacto
- **GIVEN** `skills/quinotospec-contract/contract.py` en el candidate
- **WHEN** la normalización corre
- **THEN** el contenido del script es byte a byte idéntico al source.

### Requirement: Orden rewrite-antes-de-manifest
El instalador MUST ejecutar la normalización ANTES de calcular los SHA-256 del ownership manifest, de modo que el manifest refleje el contenido finalmente instalado.

#### Scenario: uninstall coherente
- **GIVEN** una instalación completada con archivos `.md` reescritos
- **WHEN** se ejecuta el uninstall
- **THEN** el manifest verifica por SHA-256 los archivos reescritos y los remueve sin conflictos.

### Requirement: Seguridad de caracteres del destino
La normalización MUST soportar rutas de instalación con espacios y con el carácter `&` sin romper el contenido reescrito.

#### Scenario: ruta con espacios
- **GIVEN** `$FINAL_CONFIG_DIR = "/home/usUARIO con espacio/.config/opencode"`
- **WHEN** la normalización corre
- **THEN** los `.md` staged referencian esa ruta correctamente y `verify_installation` pasa.

---

## MODIFIED Requirements

## REMOVED Requirements

## RENAMED Requirements
