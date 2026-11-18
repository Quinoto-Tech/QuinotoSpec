Auditoria VPAT-k4m7 (TSK-003):
- Todas las ocurrencias en .md del payload son rutas de comandos ejecutables (agent-dist/skills/...py, etc).
- Cero ocurrencias con prefijo (no hay "<var>/agent-dist") y cero menciones standalone sin slash en .md.
- Conclusion: NO se requieren exclusiones semanticas; el rewrite uniforme de agent-dist/ -> install_root/ es seguro para todo .md.
- Codigo (.py/.sh/.js/.json) queda excluido del rewrite (check H byte-intacto).
