---
date: 2026-09-27
prefix: QSPE-a7f3
slug: discovery-executed
format: v2
type: change
---

## [2026-09-27] - Discovery Executed

### Resumen
- Se exploró el proyecto completo y se generaron los 8 archivos de especificación en `.quinoto-spec/discovery/` (1391 líneas en total).
- **Hallazgo crítico (F-01):** `agent-dist/plugins/opencode/quinotospec-plugin.js` exporta el contrato de plugin v1, pero OpenCode v2.0.16 exige `default` = objeto `{id, effect|setup}`. Falla en cada arranque del servidor (9 occurrences en `opencode.log`, refs `err_e5e24291` … `err_d3b99bf1`). En v2 el plugin era el único mecanismo que hacía llegar `rules/` y `bootstrap/` al agente, y su `config.instructions` es no-op documentado ⇒ el Bootstrap de sesión no ocurre.
- **Hallazgo crítico (F-02):** con `--opencode --global`, el `AGENTS.md` generado se escribe en `~/.config/AGENTS.md` (`install.sh:1086-1088` + `:1237`), ruta que OpenCode v2 no lee — debería ser `~/.config/opencode/AGENTS.md`. Verificado empíricamente en la instalación real de esta máquina (162 líneas en `~/.config/AGENTS.md`; ausente en `~/.config/opencode/AGENTS.md`). `verify_installation` sólo comprueba existencia, nunca la ruta, por lo que el bug es invisible para el instalador.
- **Causa raíz de F-01/F-02:** `install.sh` nunca consulta la versión del IDE de destino (`check_dependencies` sólo valida bash, git y python), así que instala contra un contrato de API que ya cambió sin ninguna señal (F-04).
- Se verificó que el plugin es **innecesario en v2**: skills, agents y commands ya se descubren de forma nativa en `~/.config/opencode/{skills,agents,commands}`, y `AGENTS.md` es el mecanismo nativo de instrucciones.
- Se inventariaron 12 hallazgos adicionales: 4 medios (tests acoplados al plugin, `hooks-opencode.json` muerto, ausencia de auto-descubrimiento de tests, chequeo de versión de host) y 6 bajos (`__pycache__` versionado, fixtures muertos, campo `external_config` nunca leído, contrato `--json` sin versionar, ausencia de lock, contradicción de Node en `--strict`).
- Auditoría de dependencias: **cero dependencias obligatorias**. Los 15 scripts Python son stdlib puro; PyYAML es un soft-import opcional sin versión pineada. No existe metadata de empaquetado Python por diseño.
- Superficie de red: **nula**. No hay endpoints HTTP; la API del paquete es su CLI (1 instalador + 15 CLIs de script).

**Tiempo Ahorrado**: ~6h (IA: ~35min vs Humano: ~6h)
